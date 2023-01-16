from typing import Dict, List, Optional, Tuple
from pypika import CustomFunction
from frappe.query_builder.functions import Count, Extract, Sum
import frappe
from frappe import _

from frappe.utils import date_diff, add_days, get_date_str, get_datetime, flt, cint

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
TimeDiff = CustomFunction("TIMEDIFF", ["end_time", "start_time"])

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
            row[from_date] = _("Unmarked Day")
            from_date = add_days(from_date, 1)
        records.append(row)
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
                    abbr = _("Unmarked Day")
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
    status = "Unmarked Day"
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
    from json import loads
    from frappe.utils.print_format import report_to_pdf

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
        filters.update({
            "summarized_view": 1
        })
        sdata = get_rows_for_pdf(employee_details, filters, holiday_map, attendance_map)
        html = get_html_for_monthly_report(filters, data, sdata, employee_details)
    else:
        html = get_html_for_report(filters, data, employee_details)
    report_to_pdf(html, orientation)

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
            if not status or status in ["Unmarked Day"]:
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
                    abbr = "Unmarked Day"
                row[label] = row[label] = {
                    "status_dict": status_dict.get(label, {}),
                    "abbr": abbr,
                }
            from_date = add_days(from_date, 1)

        attendance_values.append(row)

    return list(shifts), attendance_values


def get_html_for_report(filters: Filters, data: List, employee_details: Dict):
    style = """
        <style>
            .styled-table { border-collapse: collapse; font-size: 0.9em; font-family: sans-serif; min-width: 400px; width:100%; box-shadow: rgba(0, 0, 0, 0.05) 0px 6px 24px 0px, rgba(0, 0, 0, 0.08) 0px 0px 0px 1px;}
            .styled-table thead tr { background-color: #FFFFFF; color: #171717;}
            .styled-table thead tr td{border: none;}
            .styled-table th, .styled-table td { padding: 12px 15px; text-align:center; box-shadow: rgba(0, 0, 0, 0.05) 0px 6px 24px 0px, rgba(0, 0, 0, 0.08) 0px 0px 0px 1px; }
            .styled-table tbody tr{ font-weight: bold;}
            .styled-table tbody tr.red { background-color: #FFEBEE;}
            .styled-table tbody tr.orange { background-color: #FFF3E0;}
            .styled-table tbody tr.green { background-color: #E8F5E9;}
        </style>
        """
    
    if filters.report_type == "Monthly Attendance":
        report_letter_head = ""
        report_tbody, report_thead = "", ""
    else:
        report_letter_head = get_report_header(filters, "")
        report_tbody, report_thead = get_report_body(
            filters, data, employee_details
        )
    
    return f"""
        {style}
        {report_letter_head}
        <table class="styled-table">
            <thead>
                {report_thead}
        </thead>
            <tbody>
                {report_tbody}
            </tbody>
        </table>
        """


def get_html_for_monthly_report(filters: Filters, data: List, sdata: List, employee_details: Dict):
    style = """
        <style>
            .styled-table { border-collapse: collapse; font-size: 0.9em; font-family: sans-serif; min-width: 400px; width:100%; box-shadow: rgba(0, 0, 0, 0.05) 0px 6px 24px 0px, rgba(0, 0, 0, 0.08) 0px 0px 0px 1px;}
            .styled-table thead tr { background-color: #FFFFFF; color: #171717;}
            .styled-table thead tr td{border: none;}
            .styled-table th, .styled-table td { padding: 5px; text-align:center; box-shadow: rgba(0, 0, 0, 0.05) 0px 6px 24px 0px, rgba(0, 0, 0, 0.08) 0px 0px 0px 1px; }
            .styled-table tbody tr{ font-weight: bold;}
            .styled-table tbody tr.red { background-color: #FFEBEE;}
            .styled-table tbody tr.orange { background-color: #FFF3E0;}
            .styled-table tbody tr.green { background-color: #E8F5E9;}
            .styled-table td { font-weight: normal; font-size: 15px}
        </style>
        """
    
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
            sub_header = get_report_header(filters, old_employee_name)
            
            report_tbody, report_thead = get_report_body(filters, [], {})
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
                            <td>{date}</td>
                            <td>{shift}</td>
                            <td>-</td>
                            <td>-</td>
                            <td>-</td>
                            <td>-</td>
                            <td>-</td>
                            <td>-</td>
                            <td>{_(v)}</td>
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
                                    <td>{date}</td>
                                    <td>{shift}</td>
                                    <td>-</td>
                                    <td>-</td>
                                    <td>-</td>
                                    <td>-</td>
                                    <td>-</td>
                                    <td>-</td>
                                    <td>{_(v)}</td>
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
                                    <td>{date}</td>
                                    <td>{shift}</td>
                                    <td>{in_time}</td>
                                    <td>{out_time}</td>
                                    <td>{working_hours}</td>
                                    <td>{req_hours}</td>
                                    <td>{is_late}</td>
                                    <td>{is_early}</td>
                                    <td>{v}</td>
                                </tr>"""
            
            summary = ""
            for srow in sdata:
                if employee == srow.get('employee'):
                    summary += f"""<tr>
                                        <td style="width: 100px">{srow.get("shift", "-")}</td>
                                        <td>{srow.get("total_present", "-")}</td>
                                        <td>{srow.get("total_leaves", "-")}</td>
                                        <td>{srow.get("total_absent", "-")}</td>
                                        <td>{srow.get("total_holidays", "-")}</td>
                                        <td>{srow.get("unmarked_days", "-")}</td>
                                        <td>{srow.get("total_late_entries", "-")}</td>
                                        <td>{srow.get("total_early_exits", "-")}</td>
                                    </tr>"""
            if len(summary) > 0:
                summary = f"""<table class="styled-table">
                            <thead>
                                <tr>
                                    <th style="width: 100px">{_("Shift")}</th>
                                    <th>{_("Total Present")}</th>
                                    <th>{_("Total Leaves")}</th>
                                    <th>{_("Total Absent")}</th>
                                    <th>{_("Total Holidays")}</th>
                                    <th>{_("Unmarked Days")}</th>
                                    <th>{_("Total Late Entries")}</th>
                                    <th>{_("Total Early Exits")}</th>
                                </tr>
                            </thead>
                                <tbody>
                                    {summary}
                                </tbody>
                            </table>
                        """
            sub_report += f"""
                        {style}
                        {sub_header}
                        <table class="styled-table">
                            <thead>
                                {report_thead}
                        </thead>
                            <tbody>
                                {report_tbody}
                            </tbody>
                        </table>
                        {summary}
                        """
    else:
        report_letter_head = ""
        report_tbody, report_thead = "", ""
    
    return sub_report

def get_report_body(filters: Filters, data: List, employee_details: Dict):
    if filters.report_type == "Daily Attendance":
        thead = f"""
            <tr>
                <th>{_("Employee")}</th>
                <th>{_("Shift")}</th>
                <th>{_("In Time")}</th>
                <th>{_("Out Time")}</th>
                <th>{_("Working Hours")}</th>
                <th>{_("Reqired Hours")}</th>
                <th>{_("Is Late Entry")}</th>
                <th>{_("Is Early Exit")}</th>
                <th>{_("Status")}</th>
            </tr>"""
        tbody = ""
        for row in data:
            if not isinstance(row, dict):
                continue
            employee_name = row.get("employee_name", "")
            shift = row.get("shift", "")
            status = row.get(filters.from_date, "")
            if isinstance(status, dict):
                abbr = status.get("abbr", "Unmarked Day")
                if abbr == "Absent":
                    color = "red"
                elif abbr == "Present":
                    color = "green"
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
                color = "orange"
                in_time = "-"
                out_time = "-"
                working_hours = "-"
                req_hours = "-"
                is_late = "-"
                is_early = "-"
                abbr = status

            tbody += f"""
                <tr class="{color}">
                    <th>{employee_name}</th>
                    <th>{shift}</th>
                    <th>{in_time}</th>
                    <th>{out_time}</th>
                    <th>{working_hours}</th>
                    <th>{req_hours}</th>
                    <th>{is_late}</th>
                    <th>{is_early}</th>
                    <th>{abbr}</th>
                </tr>"""
        
        return tbody, thead

    elif filters.report_type == "Summary Attendance":
        thead = f"""
            <tr>
                <th>{_("Employee")}</th>
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
                    <th>{row.get("employee_name")}</th>
                    <th>{row.get("shift")}</th>
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
                <th>{_("Reqired Hours")}</th>
                <th>{_("Is Late Entry")}</th>
                <th>{_("Is Early Exit")}</th>
                <th>{_("Status")}</th>
            </tr>"""
        tbody = ""
        return tbody, thead
    return "", ""


def get_report_header(filters: Filters, employee: str):
    from frappe.utils import get_weekday, get_datetime
    if filters.report_type == "Monthly Attendance":
        fweekday = get_weekday(get_datetime(filters.from_date))
        tweekday = get_weekday(get_datetime(filters.to_date))
        return f"""
            <h2 style="background-color: #00aead; color: #ffffff;text-align: center; font-size: 15px; font-family: sans-serif; margin:0; padding: 14px; box-shadow: rgba(0, 0, 0, 0.05) 0px 6px 24px 0px, rgba(0, 0, 0, 0.08) 0px 0px 0px 1px;border-bottom: 3px solid white;">
                <span style="display: inline-block">{_("Monthly Report from Date")}</span>
                <span style="display: inline-block">{filters.from_date}</span>
                <span style="display: inline-block">{_(fweekday)}</span>
                <span style="display: inline-block">{_("to Date")}</span>
                <span style="display: inline-block">{filters.to_date}</span>
                <span style="display: inline-block">{_(tweekday)}</span>
                <div>For Employee { employee }</div>
            </h2>
        """
    elif filters.report_type == "Summary Attendance":
        fweekday = get_weekday(get_datetime(filters.from_date))
        tweekday = get_weekday(get_datetime(filters.to_date))
        return f"""
            <h2 style="background-color: #00aead; font-size: 15px;  color: #ffffff;text-align: center;font-family: sans-serif; margin:0; padding: 14px; box-shadow: rgba(0, 0, 0, 0.05) 0px 6px 24px 0px, rgba(0, 0, 0, 0.08) 0px 0px 0px 1px;border-bottom: 3px solid white;">
                <span style="display: inline-block">{_("Summary Attendance Report from Date")}</span>
                <span style="display: inline-block">{filters.from_date}</span>
                <span style="display: inline-block">{_(fweekday)}</span>
                <span style="display: inline-block">{_("to Date")}</span>
                <span style="display: inline-block">{filters.to_date}</span>
                <span style="display: inline-block">{_(tweekday)}</span>
            </h2>
        """
    elif filters.report_type == "Daily Attendance":
        date = filters.from_date
        weekday = get_weekday(get_datetime(filters.from_date))
        return f"""
            <h2 style="background-color: #00aead; font-size: 15px;  color: #ffffff;text-align: center;font-family: sans-serif; margin:0; padding: 14px; box-shadow: rgba(0, 0, 0, 0.05) 0px 6px 24px 0px, rgba(0, 0, 0, 0.08) 0px 0px 0px 1px;border-bottom: 3px solid white;">
                <span style="display: inline-block">{_("Daily Report for Date")}</span>
                <span style="display: inline-block">{date}</span>
                <span style="display: inline-block">{_(weekday)}</span>
            </h2>
        """
    return ""
