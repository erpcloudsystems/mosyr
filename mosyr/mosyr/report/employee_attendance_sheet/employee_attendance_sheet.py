from calendar import monthrange

from typing import Dict, List, Optional, Tuple
from pypika import CustomFunction

import frappe
from frappe import _

from frappe.utils import date_diff, add_days, get_date_str, get_datetime

Filters = frappe._dict

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

def execute(filters: Optional[Filters] = None) -> Tuple:
    filters = frappe._dict(filters or {})

    if not (filters.from_date and filters.to_date):
        frappe.throw(_("Please select date range."))

    attendance_map = get_attendance_map(filters)
    if not attendance_map:
        frappe.msgprint(
            _("No attendance records found."), alert=True, indicator="orange"
        )
        return [], [], None, None

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
            {"label": f"{label}", "fieldtype": "Data", "fieldname": label_str, "width": 170}
        )
        from_date = add_days(from_date, 1)

    return days


def get_total_days(filters: Filters) -> int:
    return date_diff(filters.to_date, filters.from_date)+1

def get_data(filters: Filters, attendance_map: Dict) -> List[Dict]:
    employee_details = get_employee_related_details(filters.company)
    holiday_map = get_holiday_map(filters)

    data = []
    data = get_rows(employee_details, filters, holiday_map, attendance_map)
    return data


def get_attendance_map(filters: Filters) -> Dict:
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
        )
        .where(
            (Attendance.docstatus == 1)
            & (Attendance.company == filters.company)
            & (DateDiff(Attendance.attendance_date, filters.from_date)>=0)
            & (DateDiff(Attendance.attendance_date, filters.to_date)<=0)
        )
    )
    if filters.employee:
        query = query.where(Attendance.employee == filters.employee)
    query = query.orderby(Attendance.employee, Attendance.attendance_date)

    attendance_list = query.run(as_dict=1)
    attendance_map = {}
    for d in attendance_list:
        attendance_map.setdefault(d.employee, frappe._dict()).setdefault(
            d.shift, frappe._dict()
        )
        attendance_map[d.employee][d.shift][get_date_str(d.day_of_month)] = d

    return attendance_map


def get_employee_related_details(company: str) -> Tuple[Dict, List]:
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
                & (DateDiff(Holiday.holiday_date, filters.from_date)>=0)
                & (DateDiff(Holiday.holiday_date, filters.to_date)<=0)
            )
        ).run(as_dict=True)
        result = []
        for hd in holidays:
            result.append({
                "weekly_off": hd.weekly_off,
                "day_of_month": get_date_str(hd.day_of_month),
            })
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
        holidays = holiday_map.get(emp_holiday_list)

        employee_attendance = attendance_map.get(employee)
        if not employee_attendance:
            continue
        
        attendance_for_employee = get_attendance_status_for_detailed_view(
            employee, filters, employee_attendance, holidays
        )
        # set employee details in the first row
        attendance_for_employee[0].update(
            {"employee": employee, "employee_name": details.employee_name}
        )

        records.extend(attendance_for_employee)

    return records


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
    for shift, status_dict in employee_attendance.items():
        row = {"shift": shift}
        from_date = filters.from_date
        for day in range(1, total_days + 1):
            label = from_date
            status = status_dict.get(label, {}).get("status")
            
            update_in_holiday = False 
            if status is None and holidays:
                status = get_holiday_status(label, holidays)
                update_in_holiday = True

            abbr = status_map.get(status, "")
            if update_in_holiday:
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
                    
                abbr =  f"<div>{trans_st_label}</div>"

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
                abbr += f"<div>{styles_status}</div>"

                abbr += f"<div>{trans_st_wh}</div>"
                abbr += f"<div style='color:green'>{working_hours}</div>"

                abbr += f"<div>{trans_st_int}</div>"
                abbr += f"<div style='color:orange'>{in_time}</div>"

                abbr += f"<div>{trans_st_ott}</div>"
                abbr += f"<div style='color:orange'>{out_time}</div>"

                abbr += f"<div>{trans_is_late}</div>"
                late_entry = _("Yes") if late_entry == 1 else  _("No")
                abbr += f"<div>{late_entry}</div>"
                
                abbr += f"<div>{trans_is_early}</div>"
                early_exit = _("Yes") if early_exit == 1 else  _("No")
                abbr += f"<div>{early_exit}</div>"

                abbr = f"<div class='datatable-table-2cols-6rows' style='margin:0'>{abbr}</div>"
                row[label] = abbr
            from_date = add_days(from_date, 1)

        attendance_values.append(row)

    return attendance_values


def get_holiday_status(day: int, holidays: List) -> str:
    status = None
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
                attendance_on_day = attendance.get(day["fieldname"])

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
