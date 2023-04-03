from datetime import timedelta
import itertools
from typing import Dict, List, Tuple
from pypika import CustomFunction

import frappe
from frappe.utils import get_date_str, time_diff_in_hours, cint, flt

from mosyr.overrides import calculate_working_hours

TimeDiff = CustomFunction("TIMEDIFF", ["end_time", "start_time"])
DateDiff = CustomFunction("DATEDIFF", ["start_date", "end_date"])
Filters = frappe._dict

def get_employee_related_details(company: str, employees: list = []) -> Tuple[Dict, List]:
    Employee = frappe.qb.DocType("Employee")
    query = (
        frappe.qb.from_(Employee)
        .select(
            Employee.name,
            Employee.employee_name,
            Employee.designation,
            Employee.grade,
            Employee.department,
            Employee.branch,
            Employee.company,
            Employee.holiday_list,
            Employee.default_shift,
        )
        .where(Employee.company == company)
    )
    if isinstance(employees, list) and len(employees) > 0:
        query = query.where(Employee.name.isin(tuple(set(employees))))
    employee_details = query.run(as_dict=True)
    emp_map = {}
    for emp in employee_details:
        emp_map[emp.name] = emp

    return emp_map

def get_attendance_list(filters: Filters, employees: list = []) -> List:
    Attendance = frappe.qb.DocType("Attendance")
    ShiftType = frappe.qb.DocType("Shift Type")
    query = (
        frappe.qb.from_(Attendance)
        .select(
            Attendance.employee,
            (Attendance.attendance_date).as_("day_of_month"),
            Attendance.status,
            Attendance.working_hours,
            Attendance.in_time,
            Attendance.out_time,
            Attendance.late_entry,
            Attendance.early_exit,
            Attendance.shift,
            ShiftType.start_time,
            ShiftType.end_time,
            ShiftType.max_working_hours,
            TimeDiff(ShiftType.end_time, ShiftType.start_time).as_("req_hours")
        ).left_join(ShiftType)
        .on(ShiftType.name == Attendance.shift)
        .where(
            (Attendance.docstatus == 1)
            & (Attendance.company == filters.company)
            & (DateDiff(Attendance.attendance_date, filters.from_date) >= 0)
            & (DateDiff(Attendance.attendance_date, filters.to_date) <= 0)
        )
    )
    if filters.employee:
        query = query.where(Attendance.employee == filters.employee)
    if isinstance(employees, list) and len(employees) > 0:
        query = query.where(Attendance.employee.isin(tuple(set(employees))))
    query = query.orderby(Attendance.employee, Attendance.attendance_date)

    attendance_list = query.run(as_dict=1)
    return attendance_list

def get_attendance_map(filters: Filters, employees: list = []) -> Dict:
    attendance_list = get_attendance_list(filters, employees)
    
    attendance_map = {}
    for d in attendance_list:
        attendance_map.setdefault(d.employee, frappe._dict()).setdefault(
            d.shift, frappe._dict()
        )
        if flt(d.max_working_hours) > 0:
            d.update({"req_hours": d.max_working_hours })
        attendance_map[d.employee][d.shift][get_date_str(d.day_of_month)] = d

    return attendance_map

def get_employee_checkin_map(filters: Filters, employees: list = []) -> Dict:
    EmployeeCheckin = frappe.qb.DocType("Employee Checkin")
    ShiftType = frappe.qb.DocType("Shift Type")
    
    shift_list = frappe.get_all("Shift Type", pluck="name")

    checkins_map = {}

    for shift in shift_list:
        doc = frappe.get_cached_doc("Shift Type", shift)
        req_hours = time_diff_in_hours(doc.end_time, doc.start_time)
        if flt(doc.max_working_hours) > 0:
            req_hours = flt(doc.max_working_hours)
        query = (
            frappe.qb.from_(EmployeeCheckin)
            .select(
                EmployeeCheckin.employee,
                (EmployeeCheckin.time).as_("day_of_month"),
                EmployeeCheckin.time,
                EmployeeCheckin.log_type,
                EmployeeCheckin.shift,
                EmployeeCheckin.shift_actual_start,
                EmployeeCheckin.shift_actual_end,
                EmployeeCheckin.shift_start,
                EmployeeCheckin.shift_end,
                ShiftType.determine_check_in_and_check_out,
                ShiftType.working_hours_calculation_based_on,
                ShiftType.start_time,
                ShiftType.end_time,
                ShiftType.enable_exit_grace_period,
                ShiftType.early_exit_grace_period,
                ShiftType.enable_entry_grace_period,
                ShiftType.late_entry_grace_period,
                TimeDiff(ShiftType.end_time, ShiftType.start_time).as_("req_hours"),
            )
            .left_join(ShiftType)
            .on(ShiftType.name == EmployeeCheckin.shift)
            .where(
                (DateDiff(EmployeeCheckin.time, filters.from_date) >= 0)
                & (DateDiff(EmployeeCheckin.time, filters.to_date) <= 0)
                & (ShiftType.name == doc.name)
            )
        )
        if filters.employee:
            query = query.where(EmployeeCheckin.employee == filters.employee)
        if isinstance(employees, list) and len(employees) > 0:
            query = query.where(EmployeeCheckin.employee.isin(tuple(set(employees))))
        query = query.orderby(EmployeeCheckin.employee, EmployeeCheckin.time)
        
        checkin_list = query.run(as_dict=1)
    
        for key, group in itertools.groupby(checkin_list, key=lambda x: (x["employee"], x["shift_actual_start"])):
            single_shift_logs = list(group)
            (
                attendance_status,
                working_hours,
                late_entry,
                early_exit,
                in_time,
                out_time,
            ) = get_attendance_from_logs(doc, single_shift_logs)

            checkins_map.setdefault(key[0], frappe._dict()).setdefault(
                doc.name, frappe._dict()
            )
            
            checkins_map[key[0]][doc.name][get_date_str(key[1].date())] = {
                "employee": key[0],
                "day_of_month": key[1].date(),
                "status": attendance_status,
                "working_hours": working_hours,
                "in_time": in_time,
                "out_time": out_time,
                "late_entry": late_entry,
                "early_exit": early_exit,
                "start_time": doc.start_time,
                "end_time": doc.end_time,
                "shift": doc.name,
                "req_hours": req_hours
            }
    return checkins_map

def get_attendance_from_logs(shift_doc, logs):
    late_entry = early_exit = False
    total_working_hours, in_time, out_time = calculate_working_hours(
        logs,
        shift_doc.determine_check_in_and_check_out,
        shift_doc.working_hours_calculation_based_on,
        flt(shift_doc.max_working_hours)
    )
    if (
        cint(shift_doc.enable_entry_grace_period)
        and in_time
        and in_time
        > logs[0].shift_start
        + timedelta(minutes=cint(shift_doc.late_entry_grace_period))
    ):
        late_entry = True

    if (
        cint(shift_doc.enable_exit_grace_period)
        and out_time
        and out_time
        < logs[0].shift_end - timedelta(minutes=cint(shift_doc.early_exit_grace_period))
    ):
        early_exit = True

    if (
        shift_doc.working_hours_threshold_for_half_day
        and total_working_hours < shift_doc.working_hours_threshold_for_half_day
    ):
        return (
            "Half Day",
            total_working_hours,
            late_entry,
            early_exit,
            in_time,
            out_time,
        )
    if (
        shift_doc.working_hours_threshold_for_absent
        and total_working_hours < shift_doc.working_hours_threshold_for_absent
    ):
        return (
            "Absent",
            total_working_hours,
            late_entry,
            early_exit,
            in_time,
            out_time,
        )
    return "Present", total_working_hours, late_entry, early_exit, in_time, out_time

def get_attendance_details(filters: Filters, employees: list = []) -> Dict:
    employee_checkin_map = get_employee_checkin_map(filters, employees)
    attendance_map = get_attendance_map(filters, employees)
    def mergedicts(attendance_map, employee_checkin_map):
        for k in set(attendance_map.keys()).union(employee_checkin_map.keys()):
            if k in attendance_map and k in employee_checkin_map:
                if isinstance(attendance_map[k], dict) and isinstance(employee_checkin_map[k], dict):
                    yield (k, dict(mergedicts(attendance_map[k], employee_checkin_map[k])))
                else:
                    # If one of the values is not a dict, you can't continue merging it.
                    # Value from second dict overrides one in first and we move on.
                    yield (k, employee_checkin_map[k])
                    # Alternatively, replace this with exception raiser to alert you of value conflicts
            elif k in attendance_map:
                yield (k, attendance_map[k])
            else:
                yield (k, employee_checkin_map[k])
    attendance_details_map = dict(mergedicts(attendance_map,employee_checkin_map))
    return attendance_details_map

def get_holiday_map(filters: Filters) -> Dict[str, List[Dict]]:
    # add default holiday list too
    holiday_lists = frappe.db.get_all("Holiday List", pluck="name")
    default_holiday_list = frappe.get_cached_value(
        "Company", filters.company, "default_holiday_list"
    )
    holiday_lists.append(default_holiday_list)

    holiday_map = frappe._dict()
    Holiday = frappe.qb.DocType("Holiday")

    for d in holiday_lists:
        if not d:
            continue

        holidays = (
            frappe.qb.from_(Holiday)
            .select(
                (Holiday.holiday_date).as_("day_of_month"),
                Holiday.weekly_off,
            )
            .where(
                (Holiday.parent == d)
                & (DateDiff(Holiday.holiday_date, filters.from_date) >= 0)
                & (DateDiff(Holiday.holiday_date, filters.to_date) <= 0)
            )
        ).run(as_dict=True)
        result = []
        for hd in holidays:
            result.append(
                {
                    "weekly_off": hd.weekly_off,
                    "day_of_month": get_date_str(hd.day_of_month),
                }
            )
        holiday_map.setdefault(d, result)

    return holiday_map

def get_holiday_status(day: int, holidays: List) -> str:
    for holiday in holidays:
        if day == holiday.get("day_of_month"):
            if holiday.get("weekly_off"):
                return "Weekly Off"
            else:
                return "Holiday"
    return "Unmarked"