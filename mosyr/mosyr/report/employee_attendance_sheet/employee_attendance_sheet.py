from json import loads
from PyPDF2 import PdfFileWriter
from typing import Dict, List, Optional, Tuple
from pypika import functions, CustomFunction

import frappe
from frappe import _

from frappe.query_builder.functions import Count, Sum

from frappe.utils import date_diff, add_days, get_date_str, get_datetime, flt, cint, get_weekday, time_diff_in_hours
from frappe.utils.print_format import report_to_pdf
from weasyprint import HTML, CSS

Filters = frappe._dict

page_length = 20

style = """
<style type="text/css">
table, th, td { border: 1px solid #ccc; border-collapse: collapse; margin:0; }
table{ width: 100%; }
th{ text-align: center; }
@page { size: A3; margin: 1mm;font-family: Arial !important;}
.color-white { color: white; }
.padding-8{ padding: 8px ; }
.padding-12{ padding: 12px ; }
.margin-10{ margin-top: 12px ; }
.font-arial{font-family: Arial}
* { font-family: Arial !important }
.font-size-12 { font-size: 12px; }
.font-size-10 { font-size: 10px; }
.red {color:red;}
.green {color:green;}
.text-center{text-align: center}
.bordernone {border: 0;}
</style>
"""

status_map = {
    "Present": "Present",
    "Absent": "Absent",
    "Half Day": "Half Day",
    "Work From Home": "Work From Home",
    "On Leave": "On Leave",
    "Holiday": "Holiday",
    "Weekly Off": "Weekly Off",
}

day_abbr = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
DateDiff = CustomFunction("DATEDIFF", ["start_date", "end_date"])
TimeDiff = CustomFunction("TIMEDIFF", ["end_time", "start_time"])

from .utils import get_employee_checkin_map

def execute(filters: Optional[Filters] = None) -> Tuple:
    filters = frappe._dict(filters or {})

    if not (filters.from_date and filters.to_date):
        frappe.throw(_("Please select date range."))

    attendance_map = get_attendance_map(filters)
    # checkin_map = get_employee_checkin_map(filters)
    # if not attendance_map:
    #     frappe.msgprint(
    #         _("No attendance records found."), alert=True, indicator="orange"
    #     )
    #     return [], [], None, None

    columns = get_columns(filters)
    data = get_data(filters, attendance_map)

    if not data:
        frappe.msgprint(
            _("No attendance records found for this criteria."),
            alert=True,
            indicator="orange",
        )
        return columns, [], None, None

    message = get_message()
    chart = get_chart_data(attendance_map, filters)
    columns = [
        {
            "label": col.get("label_html", col.get("label")),
            "fieldname": col.get("fieldname"),
            "fieldtype": col.get("fieldtype"),
            "options": col.get("options"),
            "width": col.get("width"),
        }
        for col in columns
    ]
    return columns, data, message, chart


def get_message() -> str:
    message = ""
    colors = ["green", "red", "orange", "green", "#318AD8", "", ""]

    count = 0
    for status in status_map.keys():
        message += f"""
            <span style='border-left: 2px solid {colors[count]}; padding-right: 12px; padding-left: 5px; margin-right: 3px;'>
                {status}
            </span>
        """
        count += 1

    return message


def get_columns(filters: Filters) -> List[Dict]:
    columns = []
    columns.extend(
        [
            {
                "label": _("Employee"),
                "fieldname": "employee",
                "fieldtype": "Link",
                "options": "Employee",
                "width": 135,
            },
            {
                "label": _("Employee Name"),
                "fieldname": "employee_name",
                "fieldtype": "Data",
                "width": 120,
            },
        ]
    )

    columns.append(
        {"label": _("Shift"), "fieldname": "shift", "fieldtype": "Data", "width": 120}
    )
    columns.extend(get_columns_for_days(filters))

    return columns


def get_columns_for_days(filters: Filters) -> List[Dict]:
    total_days = get_total_days(filters)
    from_date = filters.from_date
    days = []

    for day in range(1, total_days + 1):
        label_str = from_date
        day_name = get_datetime(label_str).strftime("%A")
        label = f"<p class='text-center' style='margin:0'>{day_name}<br>{label_str}</p>"
        days.append(
            {
                "label": f"{label_str}",
                "label_html": f"{label}",
                "fieldtype": "Data",
                "fieldname": label_str,
                "width": 170,
            }
        )
        from_date = add_days(from_date, 1)

    return days


def get_total_days(filters: Filters) -> int:
    return date_diff(filters.to_date, filters.from_date) + 1


def get_data(filters: Filters, attendance_map: Dict) -> List[Dict]:
    employee_details = get_employee_related_details(filters.company)
    holiday_map = get_holiday_map(filters)

    data = []
    data = get_rows(employee_details, filters, holiday_map, attendance_map)
    return data


def get_attendance_map(filters: Filters, employees: list = []) -> Dict:
    """Returns a dictionary of employee wise attendance map as per shifts for all the days of the month like
    {
            'employee1': {
                    'Morning Shift': {attendance_date: 'Present', attendance_date: 'Absent', ...}
                    'Evening Shift': {attendance_date: 'Absent', attendance_date: 'Present', ...}
            },
            'employee2': {
                    'Afternoon Shift': {attendance_date: 'Present', attendance_date: 'Absent', ...}
                    'Night Shift': {attendance_date: 'Absent', attendance_date: 'Absent', ...}
            }
    }
    """
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
    attendance_map = {}
    for d in attendance_list:
        attendance_map.setdefault(d.employee, frappe._dict()).setdefault(
            d.shift, frappe._dict()
        )
        attendance_map[d.employee][d.shift][get_date_str(d.day_of_month)] = d

    return attendance_map


def get_employee_related_details(company: str, employees: list = []) -> Tuple[Dict, List]:
    """Returns
    1. nested dict for employee details
    """
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


def get_holiday_map(filters: Filters) -> Dict[str, List[Dict]]:
    """
    Returns a dict of holidays falling in the filter month and year
    with list name as key and list of holidays as values like
    {
            'Holiday List 1': [
                    {'day_of_month': '0' , 'weekly_off': 1},
                    {'day_of_month': '1', 'weekly_off': 0}
            ],
            'Holiday List 2': [
                    {'day_of_month': '0' , 'weekly_off': 1},
                    {'day_of_month': '1', 'weekly_off': 0}
            ]
    }
    """
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


def get_rows(
    employee_details: Dict, filters: Filters, holiday_map: Dict, attendance_map: Dict
) -> List[Dict]:
    records = []
    default_holiday_list = frappe.get_cached_value(
        "Company", filters.company, "default_holiday_list"
    )

    for employee, details in employee_details.items():
        emp_holiday_list = details.holiday_list or default_holiday_list
        holidays = holiday_map.get(emp_holiday_list, [])

        employee_attendance = attendance_map.get(employee)
        try_to_get_from_employee_checkin(employee, employee_attendance, filters)
        if not employee_attendance:
            attendance_for_employee = []
            no_logs = shifts_with_no_logs(employee, filters, [])
            attendance_for_employee.extend(no_logs)
        else:
            shifts, attendance_for_employee = get_attendance_status_for_detailed_view(
                employee, filters, employee_attendance, holidays
            )
            no_logs = shifts_with_no_logs(employee, filters, shifts)
            attendance_for_employee.extend(no_logs)
        # set employee details in the first row
        if len(attendance_for_employee) == 0:
            continue
        attendance_for_employee[0].update(
            {"employee": employee, "employee_name": details.employee_name}
        )

        records.extend(attendance_for_employee)

    return records


def shifts_with_no_logs(employee: str, filters: Filters, shifts: List):
    total_days = get_total_days(filters)
    other_shifts = frappe.get_list(
        "Shift Assignment",
        filters={
            "employee": employee,
            "docstatus": 1,
            "status": "Active",
            "shift_type": ["not in", shifts],
        },
        fields=["DISTINCT(shift_type) as shift_type"],
    )
    records = []
    for shift in other_shifts:
        shift = shift.shift_type
        row = {"shift": shift}
        from_date = filters.from_date
        for day in range(1, total_days + 1):
            row[from_date] = _("Unmarked")
            from_date = add_days(from_date, 1)
        records.append(row)
    return records

def try_to_get_from_employee_checkin(employee: str, employee_attendance: Dict, filters: Filters) -> Dict:
    dates_with_attendance = []
    if employee_attendance is None:
        employee_attendance = {}
    
    if employee_attendance is not None:    
        for shift, details in employee_attendance.items():
            dates_with_attendance.extend(list(details.keys()))
        dates_with_attendance = list(set(dates_with_attendance))
    
    total_days = get_total_days(filters)
    from_date = filters.from_date
    
    attendance_map_from_checkin = {}
    
    for day in range(1, total_days + 1):
        if from_date in dates_with_attendance:
            from_date = add_days(from_date, 1)
            continue
        checkin_list = read_checkin_list(employee, from_date)
        
        if checkin_list is None:
            from_date = add_days(from_date, 1)
            continue
        
        for k, v in checkin_list.items():
            logs = v.get("logs", [])
            if len(logs) == 0:
                continue
            status = "Unmarked"
            check_in_out_type = logs[0].get('determine_check_in_and_check_out', False)
            working_hours_calc_type = logs[0].get('working_hours_calculation_based_on', False)
            start_time = logs[0].get('start_time')
            end_time = logs[0].get('end_time')
            req_hours = logs[0].get('req_hours')
            enable_exit_grace_period = logs[0].get('enable_exit_grace_period')
            early_exit_grace_period = logs[0].get('early_exit_grace_period')
            enable_entry_grace_period = logs[0].get('enable_entry_grace_period')
            late_entry_grace_period = logs[0].get('late_entry_grace_period')
            total_hours = 0
            in_time = out_time = None
            late_entry = early_exit = False
            if check_in_out_type and working_hours_calc_type:
                total_hours, in_time, out_time, late_entry, early_exit = calculate_working_hours(
                    logs, check_in_out_type, working_hours_calc_type,
                    enable_exit_grace_period, early_exit_grace_period, 
                    enable_entry_grace_period, late_entry_grace_period,
                    start_time, end_time
                )
                if in_time:
                    status = "Present"
            if employee  == "HR-EMP-00008":
                print(employee, total_hours, in_time, out_time)
            attendance_map_from_checkin.setdefault(k, frappe._dict())
            attendance_map_from_checkin[k][get_date_str(from_date)] = {
                "employee": "HR-EMP-00031",
                "day_of_month": from_date,
                "status": status,
                "working_hours": total_hours,
                "in_time": in_time,
                "out_time": out_time,
                "late_entry": late_entry,
                "early_exit": early_exit,
                "shift": k,
                "start_time": start_time,
                "end_time": end_time,
                "req_hours": req_hours,
            }

        from_date = add_days(from_date, 1)
    if len(attendance_map_from_checkin) == 0:
        return None
    for k, v in employee_attendance.items():
        employee_attendance.get(k).update(attendance_map_from_checkin.get(k, {}))
    
    return attendance_map_from_checkin

def find_index_in_dict(dict_list, key, value):
    return next((index for (index, d) in enumerate(dict_list) if d[key] == value), None)

def calculate_working_hours(logs, check_in_out_type, working_hours_calc_type,
                            enable_exit_grace_period, early_exit_grace_period, 
                            enable_entry_grace_period, late_entry_grace_period,
                            start_time, end_time):
    """Given a set of logs in chronological order calculates the total working hours based on the parameters.
    Zero is returned for all invalid cases.

    :param logs: The List of 'Employee Checkin'.
    :param check_in_out_type: One of: 'Alternating entries as IN and OUT during the same shift', 'Strictly based on Log Type in Employee Checkin'
    :param working_hours_calc_type: One of: 'First Check-in and Last Check-out', 'Every Valid Check-in and Check-out'
    """
    from datetime import timedelta
    total_hours = 0
    in_time = out_time = None
    late_entry = early_exit = False
    if check_in_out_type == "Alternating entries as IN and OUT during the same shift":
        in_time = logs[0].time
        if len(logs) >= 2:
            out_time = logs[-1].time
        if working_hours_calc_type == "First Check-in and Last Check-out":
            # assumption in this case: First log always taken as IN, Last log always taken as OUT
            total_hours = time_diff_in_hours(in_time, logs[-1].time)
        elif working_hours_calc_type == "Every Valid Check-in and Check-out":
            logs = logs[:]
            while len(logs) >= 2:
                total_hours += time_diff_in_hours(logs[0].time, logs[1].time)
                del logs[:2]

    elif check_in_out_type == "Strictly based on Log Type in Employee Checkin":
        if working_hours_calc_type == "First Check-in and Last Check-out":
            first_in_log_index = find_index_in_dict(logs, "log_type", "IN")
            first_in_log = (
                logs[first_in_log_index] if first_in_log_index or first_in_log_index == 0 else None
            )
            last_out_log_index = find_index_in_dict(reversed(logs), "log_type", "OUT")
            last_out_log = (
                logs[len(logs) - 1 - last_out_log_index]
                if last_out_log_index or last_out_log_index == 0
                else None
            )
            if first_in_log:
                in_time = first_in_log.time
            if last_out_log:
                out_time = last_out_log.time
            if first_in_log and last_out_log:
                in_time, out_time = first_in_log.time, last_out_log.time
                total_hours = time_diff_in_hours(in_time, out_time)
        elif working_hours_calc_type == "Every Valid Check-in and Check-out":
            in_log = out_log = None
            for log in logs:
                if in_log and out_log:
                    if not in_time:
                        in_time = in_log.time
                    out_time = out_log.time
                    total_hours += time_diff_in_hours(in_log.time, out_log.time)
                    in_log = out_log = None
                if not in_log:
                    in_log = log if log.log_type == "IN" else None
                    if in_log and not in_time:
                        in_time = in_log.time
                elif not out_log:
                    out_log = log if log.log_type == "OUT" else None

            if in_log and out_log:
                out_time = out_log.time
                total_hours += time_diff_in_hours(in_log.time, out_log.time)

    # if (
    #     cint(enable_entry_grace_period) 
    #     and in_time and start_time
    #     and in_time > start_time + timedelta(minutes=cint(late_entry_grace_period))):
    #     late_entry = True

    # if (
    #     cint(enable_exit_grace_period)
    #     and out_time and end_time
    #     and out_time < end_time - timedelta(minutes=cint(early_exit_grace_period))
    # ):
    #     early_exit = True

    return total_hours, in_time, out_time, late_entry, early_exit

def read_checkin_list(employee: str, from_date) -> List:
    EmployeeCheckin = frappe.qb.DocType("Employee Checkin")
    ShiftType = frappe.qb.DocType("Shift Type")
    
    query = (
        frappe.qb.from_(EmployeeCheckin)
        .select(
            EmployeeCheckin.employee,
            (EmployeeCheckin.time).as_("day_of_month"),
            EmployeeCheckin.time,
            EmployeeCheckin.log_type,
            EmployeeCheckin.shift,
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
            (EmployeeCheckin.employee == employee)
            & (DateDiff(EmployeeCheckin.time, from_date) == 0)
        ).orderby(EmployeeCheckin.time)
    )
    
    checkin_list = query.run(as_dict=1)
    if len(checkin_list) == 0:
        return None
    
    # group by shift
    checkins_map = {}
    for d in checkin_list:
        if checkins_map.get(d.shift):
            lst = checkins_map.get(d.shift).get('logs', [])
            lst.append(d)
        else:
            checkins_map.update({
                d.shift: {
                    "logs": [d],
                    "start_time": d.start_time,
                    "end_time": d.end_time,
                    "shift": d.shift,
                    "day_of_month": d.day_of_month,
                    "req_hours": d.req_hours,
                }
            })
    return checkins_map
    # calculate_working_hours(checkin_list, check_in_out_type, working_hours_calc_type)

def get_attendance_status_for_detailed_view(
    employee: str, filters: Filters, employee_attendance: Dict, holidays: List
) -> List[Dict]:
    """Returns list of shift-wise attendance status for employee
    [
            {'shift': 'Morning Shift', 1: 'A', 2: 'P', 3: 'A'....},
            {'shift': 'Evening Shift', 1: 'P', 2: 'A', 3: 'P'....}
    ]
    """
    total_days = get_total_days(filters)
    attendance_values = []
    shifts = set()
    for shift, status_dict in employee_attendance.items():
        row = {"shift": shift}
        shifts.add(shift)
        from_date = filters.from_date
        for day in range(1, total_days + 1):
            label = from_date
            status = status_dict.get(label, {}).get("status")

            update_in_holiday = False
            if status is None and holidays:
                status = get_holiday_status(label, holidays)
                update_in_holiday = True

            abbr = status_map.get(status)
            if update_in_holiday:
                abbr = (
                    abbr
                    if abbr
                    else f"<div style='margin:0; text-align:center;font-weight:bold'>{status}</div>"
                )
                abbr = f"<div style='margin:0'>{abbr}</div>"
                row[label] = abbr
            else:
                trans_st_label = _("Status")
                trans_st_wh = _("Working Hours")
                trans_st_int = _("In Time")
                trans_st_ott = _("Out Time")
                trans_is_late = _("Is Late")
                trans_is_early = _("is Early Exit")

                working_hours = status_dict.get(label, {}).get("working_hours", 0)
                in_time = status_dict.get(label, {}).get("in_time", "-")
                out_time = status_dict.get(label, {}).get("out_time", "-")
                late_entry = status_dict.get(label, {}).get("late_entry", 0)
                early_exit = status_dict.get(label, {}).get("early_exit", 0)
                if in_time:
                    in_time = str(in_time).split(" ")
                    if len(in_time) > 1:
                        in_time = in_time[1]

                if out_time:
                    out_time = str(out_time).split(" ")
                    if len(out_time) > 1:
                        out_time = out_time[1]

                abbr = f"<div>{trans_st_label}</div>"

                if status in ["Present", "Work From Home"]:
                    styles_status = "<span style='color:green'>" + status + "</span>"
                elif status in ["Absent"]:
                    styles_status = "<span style='color:red'>" + status + "</span>"
                elif status in ["Half Day"]:
                    styles_status = "<span style='color:orange'>" + status + "</span>"
                elif status in ["On Leave"]:
                    styles_status = "<span style='color:#318AD8'>" + status + "</span>"
                else:
                    styles_status = status

                if styles_status is None:
                    abbr = _("Unmarked")
                    abbr = f"<div class='datatable-table-2cols-6rows' style='margin:0; text-align:center;font-weight:bold'>{abbr}</div>"
                else:
                    abbr += f"<div>{styles_status}</div>"

                    abbr += f"<div>{trans_st_wh}</div>"
                    abbr += f"<div style='color:green'>{working_hours}</div>"

                    abbr += f"<div>{trans_st_int}</div>"
                    abbr += f"<div style='color:orange'>{in_time}</div>"

                    abbr += f"<div>{trans_st_ott}</div>"
                    abbr += f"<div style='color:orange'>{out_time}</div>"

                    abbr += f"<div>{trans_is_late}</div>"
                    late_entry = _("Yes") if late_entry == 1 else _("No")
                    abbr += f"<div>{late_entry}</div>"

                    abbr += f"<div>{trans_is_early}</div>"
                    early_exit = _("Yes") if early_exit == 1 else _("No")
                    abbr += f"<div>{early_exit}</div>"

                    abbr = f"<div class='datatable-table-2cols-6rows' style='margin:0'>{abbr}</div>"
                row[label] = abbr
            from_date = add_days(from_date, 1)

        attendance_values.append(row)

    return list(shifts), attendance_values


def get_holiday_status(day: int, holidays: List) -> str:
    status = "Unmarked"
    for holiday in holidays:
        if day == holiday.get("day_of_month"):
            if holiday.get("weekly_off"):
                status = "Weekly Off"
            else:
                status = "Holiday"
            break
    return status


def get_chart_data(attendance_map: Dict, filters: Filters) -> Dict:
    days = get_columns_for_days(filters)
    labels = []
    absent = []
    present = []
    leave = []

    for day in days:
        labels.append(day["label"])
        total_absent_on_day = total_leaves_on_day = total_present_on_day = 0

        for employee, attendance_dict in attendance_map.items():
            for shift, attendance in attendance_dict.items():
                attendance_on_day = attendance.get(day["fieldname"], {}).get("status")
                if attendance_on_day == "Absent":
                    total_absent_on_day += 1
                elif attendance_on_day in ["Present", "Work From Home"]:
                    total_present_on_day += 1
                elif attendance_on_day == "Half Day":
                    total_present_on_day += 0.5
                    total_leaves_on_day += 0.5
                elif attendance_on_day == "On Leave":
                    total_leaves_on_day += 1

        absent.append(total_absent_on_day)
        present.append(total_present_on_day)
        leave.append(total_leaves_on_day)

    return {
        "data": {
            "labels": labels,
            "datasets": [
                {"name": "Absent", "values": absent},
                {"name": "Present", "values": present},
                {"name": "Leave", "values": leave},
            ],
        },
        "type": "line",
        "colors": ["red", "green", "blue"],
    }


@frappe.whitelist()
def export_report(filters, orientation="Landscape"):
    try:
        filters = loads(filters)
    except:
        filters = {}
    filters = frappe._dict(filters or {})
    if filters.report_type == "Daily Attendance":
        if not filters.from_date:
            frappe.throw(_("Date required to export Daily Attendance Report"))
            return
        filters.update({"to_date": filters.from_date})
    elif filters.report_type in ["Summary Attendance", "Monthly Attendance"]:
        if not filters.from_date or not filters.to_date:
            frappe.throw(
                _("From/to Dates required to export Summary/Monthly Attendance Report")
            )
            return
    else:
        frappe.throw(_("Not allow to export this report!"))
        return
    if filters.report_type == "Summary Attendance":
        filters.update({
            "summarized_view": 1
        })
    if not filters.company:
        frappe.throw(_("Company is required to export this report!"))
        return

    employees = filters.get("employees")
    if not isinstance(employees, list):
        employees = []
    else:
        employees = [emp.get("employee", "") for emp in filters.get("employees", [])]

    attendance_map = get_attendance_map(filters, employees)
    employee_details = get_employee_related_details(filters.company, employees)
    holiday_map = get_holiday_map(filters)
    data = get_rows_for_pdf(employee_details, filters, holiday_map, attendance_map)
    if filters.report_type == "Monthly Attendance":
        data = get_rows_for_pdf2(employee_details, filters, holiday_map, attendance_map)
        filters.update({ "summarized_view": 1 })
        sdata = get_rows_for_pdf2(employee_details, filters, holiday_map, attendance_map)
        try: 
            html_string = get_html_for_monthly_report2(filters, data, sdata)
            base_css = CSS(string= style)
            html = HTML(string=html_string)
            pdf_content = html.write_pdf(stylesheets=[base_css])

            frappe.local.response.filename = "report.pdf"
            frappe.local.response.filecontent = pdf_content
            frappe.local.response.type = "download"
            return 
        except Exception as e:
            print(e)
            return
    elif filters.report_type == "Daily Attendance":
        try:
            download_pdf_for_daily_attendance(filters, data)
        except Exception as e:
            print(e)
            report_to_pdf(f"<h1>Error Report {e}</h1>", orientation)
        return
    elif filters.report_type == "Summary Attendance":
        try:
            download_pdf_for_summary_attendance(filters, data)
        except Exception as e:
            print(e)
            report_to_pdf(f"<h1>Error Report {e}</h1>", orientation)
        return
    else:
        report_to_pdf("<h1>Error Report Type</h1>", orientation)

def get_attendance_summary_and_days(employee: str, filters: Filters) -> Tuple[Dict, List]:
    Attendance = frappe.qb.DocType("Attendance")

    present_case = (
        frappe.qb.terms.Case()
        .when(((Attendance.status == "Present") | (Attendance.status == "Work From Home")), 1)
        .else_(0)
    )
    sum_present = Sum(present_case).as_("total_present")
    sum_working_hours = Sum(Attendance.working_hours).as_("total_working_hours")

    absent_case = frappe.qb.terms.Case().when(Attendance.status == "Absent", 1).else_(0)
    sum_absent = Sum(absent_case).as_("total_absent")

    leave_case = frappe.qb.terms.Case().when(Attendance.status == "On Leave", 1).else_(0)
    sum_leave = Sum(leave_case).as_("total_leaves")

    half_day_case = frappe.qb.terms.Case().when(Attendance.status == "Half Day", 0.5).else_(0)
    sum_half_day = Sum(half_day_case).as_("total_half_days")
    result = []
    summary = (
        frappe.qb.from_(Attendance)
        .select(
            Attendance.shift.as_("shift"),
            sum_present,
            sum_absent,
            sum_leave,
            sum_half_day,
            sum_working_hours,
        ).groupby(Attendance.shift)
        .where(
            (Attendance.docstatus == 1)
            & (Attendance.employee == employee)
            & (Attendance.company == filters.company)
            & (DateDiff(Attendance.attendance_date, filters.from_date) >= 0)
            & (DateDiff(Attendance.attendance_date, filters.to_date) <= 0)
        )
    ).run(as_dict=True)
    for suma in summary:
        row = {}
        row.update(suma)
        days = (
            frappe.qb.from_(Attendance)
            .select(
                (Attendance.attendance_date).as_("day_of_month"),
                Attendance.shift.as_("shift"),
            ).distinct()
            .where(
                (Attendance.docstatus == 1)
                & (Attendance.employee == employee)
                & (Attendance.shift == suma.shift)
                & (Attendance.company == filters.company)
                & (DateDiff(Attendance.attendance_date, filters.from_date) >= 0)
                & (DateDiff(Attendance.attendance_date, filters.to_date) <= 0)
            )
        ).run(as_dict=True)
        row.update({
            "attendance_days": [get_date_str(day.day_of_month) for day in days]
        })
        result.append(row)
    
    return result

def get_attendance_status_for_summarized_view(
    employee: str, filters: Filters, holidays: List
) -> Dict:
    """Returns dict of attendance status for employee like
    {'total_present': 1.5, 'total_leaves': 0.5, 'total_absent': 13.5, 'total_holidays': 8, 'unmarked_days': 5}
    """
    ss = get_attendance_summary_and_days(employee, filters)
    total_days = get_total_days(filters)
    

    result = []
    for s in ss:
        total_holidays = total_unmarked_days = 0
        attendance_days = s.get('attendance_days', [])
        from_date = filters.from_date
        row = {}
        row.update(s)
        for day in range(1, total_days + 1):
            if from_date in attendance_days:
                from_date = add_days(from_date, 1)
                continue
            status = get_holiday_status(from_date, holidays)
            if status in ["Weekly Off", "Holiday"]:
                total_holidays += 1
            if not status or status in ["Unmarked"]:
                total_unmarked_days += 1
            from_date = add_days(from_date, 1)
        row.update({
            "shift": s.get("shift"),
            "total_present": s.get("total_present", 0) + s.get("total_half_days", 0),
            "total_working_hours": s.get("total_working_hours", 0),
            "total_leaves": s.get("total_leaves", 0) + s.get("total_half_days", 0),
            "total_absent": s.get("total_absent", 0) + s.get("total_half_days", 0),
            "total_holidays": total_holidays,
            "unmarked_days": total_unmarked_days,
        })
        result.append(row)
    return result

def get_leave_summary(employee: str, filters: Filters) -> Dict[str, float]:
    """Returns a dict of leave type and corresponding leaves taken by employee like:
    {'leave_without_pay': 1.0, 'sick_leave': 2.0}
    """
    Attendance = frappe.qb.DocType("Attendance")
    day_case = frappe.qb.terms.Case().when(Attendance.status == "Half Day", 0.5).else_(1)
    sum_leave_days = Sum(day_case).as_("leave_days")

    leave_details = (
        frappe.qb.from_(Attendance)
        .select(Attendance.leave_type, sum_leave_days)
        .where(
            (Attendance.employee == employee)
            & (Attendance.docstatus == 1)
            & (Attendance.company == filters.company)
            & ((Attendance.leave_type.isnotnull()) | (Attendance.leave_type != ""))
            & (DateDiff(Attendance.attendance_date, filters.from_date) >= 0)
            & (DateDiff(Attendance.attendance_date, filters.to_date) <= 0)
        )
        .groupby(Attendance.leave_type)
    ).run(as_dict=True)

    leaves = {}
    for d in leave_details:
        leave_type = frappe.scrub(d.leave_type)
        leaves[leave_type] = d.leave_days

    return leaves

def get_entry_exits_summary(employee: str, filters: Filters) -> Dict[str, float]:
    """Returns total late entries and total early exits for employee like:
    {'total_late_entries': 5, 'total_early_exits': 2}
    """
    Attendance = frappe.qb.DocType("Attendance")

    late_entry_case = frappe.qb.terms.Case().when(Attendance.late_entry == "1", "1")
    count_late_entries = Count(late_entry_case).as_("total_late_entries")

    early_exit_case = frappe.qb.terms.Case().when(Attendance.early_exit == "1", "1")
    count_early_exits = Count(early_exit_case).as_("total_early_exits")

    entry_exits = (
        frappe.qb.from_(Attendance)
        .select(count_late_entries, count_early_exits)
        .where(
            (Attendance.docstatus == 1)
            & (Attendance.employee == employee)
            & (Attendance.company == filters.company)
            & (DateDiff(Attendance.attendance_date, filters.from_date) >= 0)
            & (DateDiff(Attendance.attendance_date, filters.to_date) <= 0)
        )
    ).run(as_dict=True)

    return entry_exits[0]

def get_rows_for_pdf(
    employee_details: Dict, filters: Filters, holiday_map: Dict, attendance_map: Dict
) -> List[Dict]:
    records = []
    default_holiday_list = frappe.get_cached_value(
        "Company", filters.company, "default_holiday_list"
    )
    for employee, details in employee_details.items():
        emp_holiday_list = details.holiday_list or default_holiday_list
        holidays = holiday_map.get(emp_holiday_list, [])
        if filters.summarized_view:
            attendance = get_attendance_status_for_summarized_view(employee, filters, holidays)
            if not attendance:
                continue
            leave_summary = get_leave_summary(employee, filters)
            entry_exits_summary = get_entry_exits_summary(employee, filters)
            # row = {"employee": employee, "employee_name": details.employee_name}
            # set_defaults_for_summarized_view(filters, row)
            result = []
            for att in attendance:
                row = {"employee": employee, "employee_name": details.employee_name}
                row.update(att)
                row.update(leave_summary)
                row.update(entry_exits_summary)
                records.append(row)
            # records.extend(result)
        else:
            employee_attendance = attendance_map.get(employee)
            if not employee_attendance:
                attendance_for_employee = []
                no_logs = shifts_with_no_logs(employee, filters, [])
                attendance_for_employee.extend(no_logs)
            else:
                (
                    shifts,
                    attendance_for_employee,
                ) = get_attendance_status_for_pdf_detailed_view(
                    employee, filters, employee_attendance, holidays
                )
                no_logs = shifts_with_no_logs(employee, filters, shifts)
                attendance_for_employee.extend(no_logs)
            # set employee details in the first row
            if len(attendance_for_employee) == 0:
                continue
            attendance_for_employee[0].update(
                {"employee": employee, "employee_name": details.employee_name}
            )
            records.extend(attendance_for_employee)
    return records

def get_attendance_status_for_pdf_detailed_view(
    employee: str, filters: Filters, employee_attendance: Dict, holidays: List
) -> List[Dict]:
    total_days = get_total_days(filters)
    attendance_values = []
    shifts = set()
    for shift, status_dict in employee_attendance.items():
        row = {"shift": shift}
        shifts.add(shift)
        from_date = filters.from_date
        for day in range(1, total_days + 1):
            label = from_date
            status = status_dict.get(label, {}).get("status")

            update_in_holiday = False
            if status is None and holidays:
                status = get_holiday_status(label, holidays)
                update_in_holiday = True

            abbr = status_map.get(status)
            if update_in_holiday:
                abbr = abbr if abbr else status
                row[label] = {"status_dict": status_dict.get(label, {}), "abbr": abbr}
            else:
                if status is None:
                    abbr = "Unmarked"
                row[label] = row[label] = {
                    "status_dict": status_dict.get(label, {}),
                    "abbr": abbr,
                }
            from_date = add_days(from_date, 1)

        attendance_values.append(row)

    return list(shifts), attendance_values


def get_report_body(filters: Filters, data: List, employee_details: Dict):
    if filters.report_type == "Summary Attendance":
        thead = f"""
            <tr>
                <th style="color:red !important" class="fs-5">{_("Employee")}</th>
                <th>{_("Shift")}</th>
                <th>{_("Total Present")}</th>
                <th>{_("Total Working Hours")}</th>
                <th>{_("Total Leaves")}</th>
                <th>{_("Total Absent")}</th>
                <th>{_("Total Holidays")}</th>
                <th>{_("Unmarked Days")}</th>
                <th>{_("Total Late Entries")}</th>
                <th>{_("Total Early Exits")}</th>
            </tr>"""
        tbody = ""
        for row in data:
            if not isinstance(row, dict):
                continue
            total_working_hours = flt(row.get("total_working_hours"))
            if total_working_hours != 0:
                from datetime import datetime
                from datetime import timedelta
                d1 = datetime(2022,5,8,0,0,0)
                d2 = d1 + timedelta(hours = flt(total_working_hours))
                total_working_hours = str(d2.time())[:-3]
            else:
                total_working_hours = "00:00"
            tbody += f"""
                <tr>
                    <th>{_(row.get("employee_name"))}</th>
                    <th>{_(row.get("shift"))}</th>
                    <th>{cint(row.get("total_present"))}</th>
                    <th>{total_working_hours}</th>
                    <th>{cint(row.get("total_leaves"))}</th>
                    <th>{cint(row.get("total_absent"))}</th>
                    <th>{cint(row.get("total_holidays"))}</th>
                    <th>{cint(row.get("unmarked_days"))}</th>
                    <th>{cint(row.get("total_late_entries"))}</th>
                    <th>{cint(row.get("total_early_exits"))}</th>
                </tr>"""

        return tbody, thead
    elif filters.report_type == "Monthly Attendance":
        thead = f"""
            <tr>
                <th>{_("Date")}</th>
                <th>{_("Shift")}</th>
                <th>{_("In Time")}</th>
                <th>{_("Out Time")}</th>
                <th>{_("Working Hours")}</th>
                <th>{_("Required Hours")}</th>
                <th>{_("Is Late Entry")}</th>
                <th>{_("Is Early Exit")}</th>
                <th>{_("Status")}</th>
            </tr>"""
        tbody = ""
        return tbody, thead
    return "", ""


def download_pdf_for_daily_attendance(filters, data):
    date = filters.from_date
    weekday = get_weekday(get_datetime(filters.from_date))
    report_header = f"""
        <h2 class="color-white" style="background-color: #00aead; font-size: 12px;  color: #ffffff;text-align: center;font-family: Arial; margin:0 !important; padding: 14px;">
            <span style="display: inline-block" class="color-white">{_("Daily Report for Date")}</span>
            <span style="display: inline-block" class="color-white">{date}</span>
            <span style="display: inline-block" class="color-white">{_(weekday)}</span>
        </h2>""".replace("\n", "").replace("\t", "")
    thead = f"""
        <tr>
            <th class="padding-8 color-white font-size-12" style="background-color: #00aead;">{_("Employee")}</th>
            <th class="padding-8 color-white font-size-12" style="background-color: #00aead;">{_("Shift")}</th>
            <th class="padding-8 color-white font-size-12" style="background-color: #00aead;">{_("In Time")}</th>
            <th class="padding-8 color-white font-size-12" style="background-color: #00aead;">{_("Out Time")}</th>
            <th class="padding-8 color-white font-size-12" style="background-color: #00aead;">{_("Working Hours")}</th>
            <th class="padding-8 color-white font-size-12" style="background-color: #00aead;">{_("Required Hours")}</th>
            <th class="padding-8 color-white font-size-12" style="background-color: #00aead;">{_("Is Late Entry")}</th>
            <th class="padding-8 color-white font-size-12" style="background-color: #00aead;">{_("Is Early Exit")}</th>
            <th class="padding-8 color-white font-size-12" style="background-color: #00aead;">{_("Status")}</th>
        </tr>""".replace("\n", "").replace("\t", "")
    tbody = []
    table = []
    if frappe.lang == 'ar':
        dirction = 'rtl'
    else:
        dirction = 'ltr'
    for row in data:
        if not isinstance(row, dict):
            continue
        employee_name = row.get("employee_name", "")
        shift = row.get("shift", "")
        status = row.get(filters.from_date, "")
        if isinstance(status, dict):
            abbr = status.get("abbr", "Unmarked")
            status_dict = status.get("status_dict", {})
            in_time = status_dict.get("in_time", "")
            out_time = status_dict.get("out_time", "")
            
            is_late = "No" if status_dict.get("late_entry", "") == 0 else "Yes"
            is_early = "No" if status_dict.get("early_exit", "") == 0 else "Yes"
            req_hours = status_dict.get("req_hours", "")
            if req_hours:
                hours, remainder = divmod(req_hours.seconds, 3600)
                minutes, seconds = divmod(remainder, 60)
                req_hours = '{:02}:{:02}'.format(int(hours), int(minutes))
            working_hours = flt(status_dict.get("working_hours", 0))
            if working_hours != 0:
                from datetime import datetime
                from datetime import timedelta
                d1 = datetime(2022,5,8,0,0,0)
                d2 = d1 + timedelta(hours = flt(working_hours))
                working_hours = str(d2.time())[:-3]
            else:
                working_hours = "00:00"
            if in_time:
                in_time = str(in_time).split(" ")
                if len(in_time) > 1:
                    in_time = in_time[1][:-3]

            if out_time:
                out_time = str(out_time).split(" ")
                if len(out_time) > 1:
                    out_time = out_time[1][:-3]
        else:
            in_time = "-"
            out_time = "-"
            working_hours = "-"
            req_hours = "-"
            is_late = "-"
            is_early = "-"
            abbr = status
        tbody.append(f"""
            <tr>
                <td class="padding-8 font-size-10" style="text-align:center">{_(employee_name)}</td>
                <td class="padding-8 font-size-10" style="text-align:center">{_(shift)}</td>
                <td class="padding-8 font-size-10" style="text-align:center">{in_time}</td>
                <td class="padding-8 font-size-10" style="text-align:center">{out_time}</td>
                <td class="padding-8 font-size-10" style="text-align:center">{working_hours}</td>
                <td class="padding-8 font-size-10" style="text-align:center">{req_hours}</td>
                <td class="padding-8 font-size-10" style="text-align:center">{is_late}</td>
                <td class="padding-8 font-size-10" style="text-align:center">{is_early}</td>
                <td class="padding-8 font-size-10" style="text-align:center">{abbr}</td>
            </tr>""".replace("\n", "").replace("\t", ""))
    split_tabels = []
    for i in range(0, len(tbody), page_length):
        table = [report_header, thead] + tbody[i:i+page_length]
        split_tabels.append(table)
    tables_as_pages = ""
    for table in split_tabels:
        if len(table) <= 2:
            continue
        report_header = table[0]
        thead = table[1]
        tbody = "".join(table[2:])
        tables_as_pages += f"""
            <table class="page">
                <thead> {thead} </thead>
                <tbody> {tbody} </tbody>
            </table>"""
    html_string = f"""
        <html dir="{dirction}" >
            <head>
                <meta charset='utf-8'>
                <meta name="description" content="" />
                <meta http-equiv="Content-Type" content="text/html;charset=UTF-8">
                {style}
            </head>
            <body>
                {report_header}
                {tables_as_pages}
            </body>
        </html>""".replace("\n", "")
    base_css = CSS(string= style)
    html = HTML(string=html_string)
    pdf_content = html.write_pdf(stylesheets=[base_css])
    frappe.local.response.filename = "report.pdf"
    frappe.local.response.filecontent = pdf_content
    frappe.local.response.type = "download"

def download_pdf_for_summary_attendance(filters, data):
    fweekday = get_weekday(get_datetime(filters.from_date))
    tweekday = get_weekday(get_datetime(filters.to_date))

    report_header = f"""
        <h2 style="background-color: #00aead; font-size: 12px;  color: #ffffff;text-align: center;font-family: Arial; margin:0; padding-top: 10px;">
            <span style="display: inline-block">{_("Summary Attendance Report from Date")}</span>
        </h2>
        <h2 style="background-color: #00aead; font-size: 12px;  color: #ffffff;text-align: center;font-family: Arial; margin:0; padding: 0 10px 10px 10px;">
            <span style="display: inline-block">{filters.from_date}</span>
            <span style="display: inline-block">{_(fweekday)}</span>
            <span style="display: inline-block">{_("to Date")}</span>
            <span style="display: inline-block">{filters.to_date}</span>
            <span style="display: inline-block">{_(tweekday)}</span>
        </h2>
    """.replace("\n", "").replace("\t", "")
    thead = f"""
        <tr>
            <th class="padding-8 color-white font-size-12" style="background-color: #00aead; " >{_("Employee")}</th>
            <th class="padding-8 color-white font-size-12" style="background-color: #00aead; ">{_("Shift")}</th>
            <th class="padding-8 color-white font-size-12" style="background-color: #00aead; ">{_("Total Present")}</th>
            <th class="padding-8 color-white font-size-12" style="background-color: #00aead; ">{_("Total Working Hours")}</th>
            <th class="padding-8 color-white font-size-12" style="background-color: #00aead; ">{_("Total Leaves")}</th>
            <th class="padding-8 color-white font-size-12" style="background-color: #00aead; ">{_("Total Absent")}</th>
            <th class="padding-8 color-white font-size-12" style="background-color: #00aead; ">{_("Total Holidays")}</th>
            <th class="padding-8 color-white font-size-12" style="background-color: #00aead; ">{_("Unmarked Days")}</th>
            <th class="padding-8 color-white font-size-12" style="background-color: #00aead; ">{_("Total Late Entries")}</th>
            <th class="padding-8 color-white font-size-12" style="background-color: #00aead; ">{_("Total Early Exits")}</th>
        </tr>""".replace("\n", "").replace("\t", "")
    tbody = []
    table = []
    if frappe.lang == 'ar':
        dirction = 'rtl'
    else:
        dirction = 'ltr'
    for row in data:
        if not isinstance(row, dict):
            continue
        total_working_hours = flt(row.get("total_working_hours"))
        if total_working_hours != 0:
            from datetime import datetime
            from datetime import timedelta
            d1 = datetime(2022,5,8,0,0,0)
            d2 = d1 + timedelta(hours = flt(total_working_hours))
            total_working_hours = str(d2.time())[:-3]
        else:
            total_working_hours = "00:00"
        tbody.append(f"""
            <tr>
                <td style="text-align:center" class="padding-8 font-size-10">{_(row.get("employee_name"))}</td>
                <td style="text-align:center" class="padding-8 font-size-10">{_(row.get("shift") or "-")}</td>
                <td  style="text-align:center" class="padding-8 font-size-10">{cint(row.get("total_present"))}</td>
                <td  style="text-align:center" class="padding-8 font-size-10">{total_working_hours}</td>
                <td  style="text-align:center" class="padding-8 font-size-10">{cint(row.get("total_leaves"))}</td>
                <td  style="text-align:center" class="padding-8 font-size-10">{cint(row.get("total_absent"))}</td>
                <td  style="text-align:center" class="padding-8 font-size-10">{cint(row.get("total_holidays"))}</td>
                <td  style="text-align:center" class="padding-8 font-size-10">{cint(row.get("unmarked_days"))}</td>
                <td  style="text-align:center" class="padding-8 font-size-10">{cint(row.get("total_late_entries"))}</td>
                <td  style="text-align:center" class="padding-8 font-size-10">{cint(row.get("total_early_exits"))}</td>
            </tr>""".replace("\n", "").replace("\t", ""))
    
    split_tabels = []
    for i in range(0, len(tbody), page_length):
        table = [report_header, thead] + tbody[i:i+page_length]
        split_tabels.append(table)

    tables_as_pages = ""
    for table in split_tabels:
        if len(table) <= 2:
            continue
        report_header = table[0]
        thead = table[1]
        tbody = "".join(table[2:])
        tables_as_pages += f"""
                <table class="page">
                    <thead> {thead} </thead>
                    <tbody> {tbody} </tbody>
                </table>"""
    html_string = f"""
        <html dir="{dirction}">
            <head>
                <meta charset='utf-8'>
                <meta name="description" content="" />
                <meta http-equiv="Content-Type" content="text/html;charset=UTF-8">
                {style}
            </head>
            <body>
                {report_header}
                {tables_as_pages}
            </body>
            </html>""".replace("\n", "")

    base_css = CSS(string= style)
    html = HTML(string=html_string)
    pdf_content = html.write_pdf(stylesheets=[base_css])

    frappe.local.response.filename = "report.pdf"
    frappe.local.response.filecontent = pdf_content
    frappe.local.response.type = "download"

def get_html_for_monthly_report2(filters: Filters, data: List, sdata: List):

    report_letter_head = ""
    old_name = ""
    old_employee_name = ""
    sub_report = ""
    if filters.report_type == "Monthly Attendance":
        for att in data:
            # sub_report = ""
            employee = att.get('employee', False)
            employee_name = att.get('employee_name')
            shift = att.get('shift', False)
            if employee and employee != old_name:
                old_employee_name = employee_name
                old_name = employee
            sub_header = get_report_header2(filters, old_employee_name)
            report_tbody, report_thead = get_report_body2(filters, [], {})
            report_letter_head += sub_header
            report_tbody = ""
            for k, v in att.items():
                if k in ['employee', 'employee_name', 'shift']: continue
                date = k
                if isinstance(v, str):
                    color = ""
                    if v == "Absent":
                        color = "red"
                    elif v == "Present":
                        color = "green"
                    report_tbody += f"""
                        <tr class="{color}">
                            <td  class="padding-8 font-size-10" style="text-align:center">{date}</td>
                            <td  class="padding-8 font-size-10" style="text-align:center">{shift or "-"}</td>
                            <td  class="padding-8 font-size-10" style="text-align:center">-</td>
                            <td  class="padding-8 font-size-10" style="text-align:center">-</td>
                            <td  class="padding-8 font-size-10" style="text-align:center">-</td>
                            <td  class="padding-8 font-size-10" style="text-align:center">-</td>
                            <td  class="padding-8 font-size-10" style="text-align:center">-</td>
                            <td  class="padding-8 font-size-10" style="text-align:center">-</td>
                            <td  class="padding-8 font-size-10" style="text-align:center">{_(v)}</td>
                        </tr>"""
                elif isinstance(v, dict):
                    if len(v.get("status_dict", {}).keys()) == 0:
                        v = v.get("abbr", "")
                        color = ""
                        if v == "Absent":
                            color = "red"
                        elif v == "Present":
                            color = "green"
                        report_tbody += f"""
                                <tr class="{color}">
                                    <td  class="padding-8 font-size-10" style="text-align:center">{date}</td>
                                    <td  class="padding-8 font-size-10" style="text-align:center">{shift or "-"}</td>
                                    <td  class="padding-8 font-size-10" style="text-align:center">-</td>
                                    <td  class="padding-8 font-size-10" style="text-align:center">-</td>
                                    <td  class="padding-8 font-size-10" style="text-align:center">-</td>
                                    <td  class="padding-8 font-size-10" style="text-align:center">-</td>
                                    <td  class="padding-8 font-size-10" style="text-align:center">-</td>
                                    <td  class="padding-8 font-size-10" style="text-align:center">-</td>
                                    <td  class="padding-8 font-size-10" style="text-align:center">{_(v)}</td>
                                </tr>"""
                    else:
                        status_dict = v.get("status_dict", {})
                        v = status_dict.get('status', 'Unmarked Day')
                        in_time = status_dict.get('in_time', 0)
                        out_time = status_dict.get('out_time', 0)
                        is_late = "No" if status_dict.get("late_entry", "") == 0 else "Yes"
                        is_early = "No" if status_dict.get("early_exit", "") == 0 else "Yes"
                        req_hours = status_dict.get("req_hours", "")
                        if req_hours:
                            hours, remainder = divmod(req_hours.seconds, 3600)
                            minutes, seconds = divmod(remainder, 60)
                            req_hours = '{:02}:{:02}'.format(int(hours), int(minutes))
                        working_hours = flt(status_dict.get("working_hours", 0))
                        if working_hours != 0:
                            from datetime import datetime
                            from datetime import timedelta
                            d1 = datetime(2022,5,8,0,0,0)
                            d2 = d1 + timedelta(hours = flt(working_hours))
                            working_hours = str(d2.time())[:-3]
                        else:
                            working_hours = "00:00"
                        if in_time:
                            in_time = str(in_time).split(" ")
                            if len(in_time) > 1:
                                in_time = in_time[1][:-3]
                        else:
                            in_time = "-"
                        if out_time:
                            out_time = str(out_time).split(" ")
                            if len(out_time) > 1:
                                out_time = out_time[1][:-3]
                        else:
                            out_time = "-"
                        color = ""
                        if v == "Absent":
                            color = "red"
                        elif v == "Present":
                            color = "green"
                        report_tbody += f"""
                                <tr class="{color}">
                                    <td  class="padding-8 font-size-10" style="text-align:center">{date}</td>
                                    <td  class="padding-8 font-size-10" style="text-align:center">{shift or "-"}</td>
                                    <td  class="padding-8 font-size-10" style="text-align:center">{in_time}</td>
                                    <td  class="padding-8 font-size-10" style="text-align:center">{out_time}</td>
                                    <td  class="padding-8 font-size-10" style="text-align:center">{working_hours}</td>
                                    <td  class="padding-8 font-size-10" style="text-align:center">{req_hours or "-"}</td>
                                    <td  class="padding-8 font-size-10" style="text-align:center">{is_late}</td>
                                    <td  class="padding-8 font-size-10" style="text-align:center">{is_early}</td>
                                    <td  class="padding-8 font-size-10" style="text-align:center">{v}</td>
                                </tr>"""
            summary1 = ""
            summary2 = ""
            for srow in sdata:
                if employee == srow.get('employee'):
                    summary1 += f"""<tr>
                                        <td class="padding-8 font-size-10 bordernone" style="text-align:center" style="width: 100px">{srow.get("shift", "-") or "-"}</td>
                                        <td class="padding-8 font-size-10 bordernone" style="text-align:center" >{srow.get("total_present", "-")}</td>
                                        <td class="padding-8 font-size-10 bordernone" style="text-align:center" >{srow.get("total_leaves", "-")}</td>
                                        <td class="padding-8 font-size-10 bordernone" style="text-align:center" >{srow.get("total_absent", "-")}</td>
                                    </tr>"""
                    summary2 += f"""<tr>
                                        <td class="padding-8 font-size-10 bordernone" style="text-align:center" >{srow.get("total_holidays", "-")}</td>
                                        <td class="padding-8 font-size-10 bordernone" style="text-align:center" >{srow.get("unmarked_days", "-")}</td>
                                        <td class="padding-8 font-size-10 bordernone" style="text-align:center" >{srow.get("total_late_entries", "-")}</td>
                                        <td class="padding-8 font-size-10 bordernone" style="text-align:center" >{srow.get("total_early_exits", "-")}</td>
                                    </tr>"""
            if len(summary1) > 0:
                summary = f"""
                            <table  class=" margin-10 text-center">
                                <thead class="bordernone">
                                    <tr class="font-size-12">
                                        <th class=" padding-12 bordernone" style="width: 100px">{_("Shift")}</th>
                                        <th class=" padding-12 bordernone ">{_("Total Present")}</th>
                                        <th class=" padding-12 bordernone ">{_("Total Leaves")}</th>
                                        <th class=" padding-12 bordernone ">{_("Total Absent")}</th>
                                    </tr>
                                </thead>
                                <tbody class="bordernone">
                                    {summary1}
                                </tbody>
                                <thead class="bordernone">
                                    <tr class="font-size-12">
                                        <th class=" padding-12 bordernone ">{_("Total Holidays")}</th>
                                        <th class=" padding-12 bordernone ">{_("Unmarked Days")}</th>
                                        <th class=" padding-12 bordernone ">{_("Total Late Entries")}</th>
                                        <th class=" padding-12 bordernone ">{_("Total Early Exits")}</th>
                                    </tr>
                                </thead>
                                <tbody class="bordernone">
                                    {summary2}
                                </tbody>
                            </table>
                        """
            sub_report += f"""
                        <div class="page text-center">
                        {style}
                        {sub_header}
                        <table>
                            <thead>
                                {report_thead}
                        </thead>
                            <tbody>
                                {report_tbody}
                            </tbody>
                        </table>
                        {summary}
                        </div>
                        """
    else:
        report_letter_head = ""
        report_tbody, report_thead = "", ""
    return sub_report

def get_report_header2(filters: Filters, employee: str):
    from frappe.utils import get_weekday, get_datetime
    if filters.report_type == "Monthly Attendance":
        fweekday = get_weekday(get_datetime(filters.from_date))
        tweekday = get_weekday(get_datetime(filters.to_date))
        return f"""
            <h2 style="break-before: page;background-color: #00aead; color: #ffffff;text-align: center; font-size: 15px; bold:100; margin:0; padding: 14px;">
                <span style="display: inline-block">{_("Monthly Report from Date")}</span>
                <span style="display: inline-block">{filters.from_date}</span>
                <span style="display: inline-block">{_(fweekday)}</span>
                <span style="display: inline-block">{_("to Date")}</span>
                <span style="display: inline-block">{filters.to_date}</span>
                <span style="display: inline-block">{_(tweekday)}</span>
                <div>For Employee { _(employee) }</div>
            </h2>
        """
    return ""

def get_report_body2(filters: Filters, data: List, employee_details: Dict):
    if filters.report_type == "Monthly Attendance":
        thead = f"""
            <tr>
                <th class="padding-8 color-white font-size-12" style="background-color: #00aead;">{_("Date")}</th>
                <th class="padding-8 color-white font-size-12" style="background-color: #00aead;">{_("Shift")}</th>
                <th class="padding-8 color-white font-size-12" style="background-color: #00aead;">{_("In Time")}</th>
                <th class="padding-8 color-white font-size-12" style="background-color: #00aead;">{_("Out Time")}</th>
                <th class="padding-8 color-white font-size-12" style="background-color: #00aead;">{_("Working Hours")}</th>
                <th class="padding-8 color-white font-size-12" style="background-color: #00aead;">{_("Required Hours")}</th>
                <th class="padding-8 color-white font-size-12" style="background-color: #00aead;">{_("Is Late Entry")}</th>
                <th class="padding-8 color-white font-size-12" style="background-color: #00aead;">{_("Is Early Exit")}</th>
                <th class="padding-8 color-white font-size-12" style="background-color: #00aead;">{_("Status")}</th>
            </tr>"""
        tbody = ""
        return tbody, thead
    return "", ""


def get_rows_for_pdf2(
    employee_details: Dict, filters: Filters, holiday_map: Dict, attendance_map: Dict
) -> List[Dict]:
    records = []
    default_holiday_list = frappe.get_cached_value(
        "Company", filters.company, "default_holiday_list"
    )
    for employee, details in employee_details.items():
        emp_holiday_list = details.holiday_list or default_holiday_list
        holidays = holiday_map.get(emp_holiday_list, [])
        if filters.summarized_view:
            attendance = get_attendance_status_for_summarized_view(employee, filters, holidays)
            if not attendance:
                continue
            leave_summary = get_leave_summary(employee, filters)
            entry_exits_summary = get_entry_exits_summary(employee, filters)
            # row = {"employee": employee, "employee_name": details.employee_name}
            # set_defaults_for_summarized_view(filters, row)
            result = []
            for att in attendance:
                row = {"employee": employee, "employee_name": details.employee_name}
                row.update(att)
                row.update(leave_summary)
                row.update(entry_exits_summary)
                records.append(row)
            # records.extend(result)
        else:
            employee_attendance = attendance_map.get(employee)
            if not employee_attendance:
                attendance_for_employee = []
                no_logs = shifts_with_no_logs(employee, filters, [])
                attendance_for_employee.extend(no_logs)
            else:
                (
                    shifts,
                    attendance_for_employee,
                ) = get_attendance_status_for_pdf_detailed_view(
                    employee, filters, employee_attendance, holidays
                )
                no_logs = shifts_with_no_logs(employee, filters, shifts)
                attendance_for_employee.extend(no_logs)
            # set employee details in the first row
            if len(attendance_for_employee) == 0:
                continue
            attendance_for_employee[0].update(
                {"employee": employee, "employee_name": details.employee_name}
            )
            records.extend(attendance_for_employee)
    return records
