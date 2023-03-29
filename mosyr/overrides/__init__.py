from datetime import datetime, timedelta

from typing import Dict, List

import frappe
from frappe import _
from frappe.query_builder import Criterion
from frappe.utils import (
    get_datetime,
    get_time,
    getdate,
    now_datetime,
    flt,
)
from erpnext.hr.doctype.employee.employee import get_holiday_list_for_employee
from erpnext.hr.doctype.holiday_list.holiday_list import is_holiday


############################################
############## Shift Request ############
############################################
def has_overlapping_timings(shift_1: str, shift_2: str) -> bool:
    """
    Accepts two shift types and checks whether their timings are overlapping
    """
    curr_shift = frappe.db.get_value(
        "Shift Type", shift_1, ["start_time", "end_time"], as_dict=True
    )
    overlapping_shift = frappe.db.get_value(
        "Shift Type", shift_2, ["start_time", "end_time"], as_dict=True
    )

    if (
        (
            curr_shift.start_time > overlapping_shift.start_time
            and curr_shift.start_time < overlapping_shift.end_time
        )
        or (
            curr_shift.end_time > overlapping_shift.start_time
            and curr_shift.end_time < overlapping_shift.end_time
        )
        or (
            curr_shift.start_time <= overlapping_shift.start_time
            and curr_shift.end_time >= overlapping_shift.end_time
        )
    ):
        return True
    return False


def get_shift_for_time(shifts: List[Dict], for_timestamp: datetime) -> Dict:
    """Returns shift with details for given timestamp"""
    valid_shifts = []

    for entry in shifts:
        shift_details = get_shift_details(entry.shift_type, for_timestamp=for_timestamp)

        if (
            get_datetime(shift_details.actual_start)
            <= get_datetime(for_timestamp)
            <= get_datetime(shift_details.actual_end)
        ):
            valid_shifts.append(shift_details)

    valid_shifts.sort(key=lambda x: x["actual_start"])

    if len(valid_shifts) > 1:
        for i in range(len(valid_shifts) - 1):
            # comparing 2 consecutive shifts and adjusting start and end times
            # if they are overlapping within grace period
            curr_shift = valid_shifts[i]
            next_shift = valid_shifts[i + 1]

            if curr_shift and next_shift:
                next_shift.actual_start = (
                    curr_shift.end_datetime
                    if next_shift.actual_start < curr_shift.end_datetime
                    else next_shift.actual_start
                )
                curr_shift.actual_end = (
                    next_shift.actual_start
                    if curr_shift.actual_end > next_shift.actual_start
                    else curr_shift.actual_end
                )

            valid_shifts[i] = curr_shift
            valid_shifts[i + 1] = next_shift

        return get_exact_shift(valid_shifts, for_timestamp) or {}

    return (valid_shifts and valid_shifts[0]) or {}


def get_shifts_for_date(employee: str, for_timestamp: datetime) -> List[Dict[str, str]]:
    """Returns list of shifts with details for given date"""
    assignment = frappe.qb.DocType("Shift Assignment")

    return (
        frappe.qb.from_(assignment)
        .select(assignment.name, assignment.shift_type)
        .where(
            (assignment.employee == employee)
            & (assignment.docstatus == 1)
            & (assignment.status == "Active")
            & (assignment.start_date <= getdate(for_timestamp.date()))
            & (
                Criterion.any(
                    [
                        assignment.end_date.isnull(),
                        (
                            assignment.end_date.isnotnull()
                            & (getdate(for_timestamp.date()) >= assignment.end_date)
                        ),
                    ]
                )
            )
        )
    ).run(as_dict=True)


def get_shift_for_timestamp(employee: str, for_timestamp: datetime) -> Dict:
    shifts = get_shifts_for_date(employee, for_timestamp)
    if shifts:
        return get_shift_for_time(shifts, for_timestamp)
    return {}


def get_employee_shift(
    employee: str,
    for_timestamp: datetime = None,
    consider_default_shift: bool = False,
    next_shift_direction: str = None,
) -> Dict:
    """Returns a Shift Type for the given employee on the given date. (excluding the holidays)
    :param employee: Employee for which shift is required.
    :param for_timestamp: DateTime on which shift is required
    :param consider_default_shift: If set to true, default shift is taken when no shift assignment is found.
    :param next_shift_direction: One of: None, 'forward', 'reverse'. Direction to look for next shift if shift not found on given date.
    """
    if for_timestamp is None:
        for_timestamp = now_datetime()

    shift_details = get_shift_for_timestamp(employee, for_timestamp)

    # if shift assignment is not found, consider default shift
    default_shift = frappe.db.get_value("Employee", employee, "default_shift")
    if not shift_details and consider_default_shift:
        shift_details = get_shift_details(default_shift, for_timestamp)

    # if its a holiday, reset
    if shift_details and is_holiday_date(employee, shift_details):
        shift_details = None

    # if no shift is found, find next or prev shift assignment based on direction
    if not shift_details and next_shift_direction:
        shift_details = get_prev_or_next_shift(
            employee,
            for_timestamp,
            consider_default_shift,
            default_shift,
            next_shift_direction,
        )

    return shift_details or {}


def get_prev_or_next_shift(
    employee: str,
    for_timestamp: datetime,
    consider_default_shift: bool,
    default_shift: str,
    next_shift_direction: str,
) -> Dict:
    """Returns a dict of shift details for the next or prev shift based on the next_shift_direction"""
    MAX_DAYS = 366
    shift_details = {}

    if consider_default_shift and default_shift:
        direction = -1 if next_shift_direction == "reverse" else 1
        for i in range(MAX_DAYS):
            date = for_timestamp + timedelta(days=direction * (i + 1))
            shift_details = get_employee_shift(
                employee, date, consider_default_shift, None
            )
            if shift_details:
                break
    else:
        direction = "<" if next_shift_direction == "reverse" else ">"
        sort_order = "desc" if next_shift_direction == "reverse" else "asc"
        dates = frappe.db.get_all(
            "Shift Assignment",
            ["start_date", "end_date"],
            {
                "employee": employee,
                "start_date": (direction, for_timestamp.date()),
                "docstatus": 1,
                "status": "Active",
            },
            as_list=True,
            limit=MAX_DAYS,
            order_by="start_date " + sort_order,
        )

        if dates:
            for date in dates:
                if date[1] and date[1] < for_timestamp.date():
                    continue
                shift_details = get_employee_shift(
                    employee,
                    datetime.combine(date[0], for_timestamp.time()),
                    consider_default_shift,
                    None,
                )
                if shift_details:
                    break

    return shift_details or {}


def is_holiday_date(employee: str, shift_details: Dict) -> bool:
    holiday_list_name = frappe.db.get_value(
        "Shift Type", shift_details.shift_type.name, "holiday_list"
    )

    if not holiday_list_name:
        holiday_list_name = get_holiday_list_for_employee(employee, False)

    return holiday_list_name and is_holiday(
        holiday_list_name, shift_details.start_datetime.date()
    )


def get_employee_shift_timings(
    employee: str, for_timestamp: datetime = None, consider_default_shift: bool = False
) -> List[Dict]:
    """Returns previous shift, current/upcoming shift, next_shift for the given timestamp and employee"""
    if for_timestamp is None:
        for_timestamp = now_datetime()

    # write and verify a test case for midnight shift.
    prev_shift = curr_shift = next_shift = None
    curr_shift = get_employee_shift(
        employee, for_timestamp, consider_default_shift, "forward"
    )
    if curr_shift:
        next_shift = get_employee_shift(
            employee,
            curr_shift.start_datetime + timedelta(days=1),
            consider_default_shift,
            "forward",
        )
    prev_shift = get_employee_shift(
        employee, for_timestamp + timedelta(days=-1), consider_default_shift, "reverse"
    )

    if curr_shift:
        # adjust actual start and end times if they are overlapping with grace period (before start and after end)
        if prev_shift:
            curr_shift.actual_start = (
                prev_shift.end_datetime
                if curr_shift.actual_start < prev_shift.end_datetime
                else curr_shift.actual_start
            )
            prev_shift.actual_end = (
                curr_shift.actual_start
                if prev_shift.actual_end > curr_shift.actual_start
                else prev_shift.actual_end
            )
        if next_shift:
            next_shift.actual_start = (
                curr_shift.end_datetime
                if next_shift.actual_start < curr_shift.end_datetime
                else next_shift.actual_start
            )
            curr_shift.actual_end = (
                next_shift.actual_start
                if curr_shift.actual_end > next_shift.actual_start
                else curr_shift.actual_end
            )

    return prev_shift, curr_shift, next_shift


def get_actual_start_end_datetime_of_shift(
    employee: str, for_timestamp: datetime, consider_default_shift: bool = False
) -> Dict:
    """Returns a Dict containing shift details with actual_start and actual_end datetime values
    Here 'actual' means taking into account the "begin_check_in_before_shift_start_time" and "allow_check_out_after_shift_end_time".
    Empty Dict is returned if the timestamp is outside any actual shift timings.
    :param employee (str): Employee name
    :param for_timestamp (datetime, optional): Datetime value of checkin, if not provided considers current datetime
    :param consider_default_shift (bool, optional): Flag (defaults to False) to specify whether to consider
    default shift in employee master if no shift assignment is found
    """
    shift_timings_as_per_timestamp = get_employee_shift_timings(
        employee, for_timestamp, consider_default_shift
    )
    return get_exact_shift(shift_timings_as_per_timestamp, for_timestamp)


def get_shift_details(shift_type_name: str, for_timestamp: datetime = None) -> Dict:
    """Returns a Dict containing shift details with the following data:
    'shift_type' - Object of DocType Shift Type,
    'start_datetime' - datetime of shift start on given timestamp,
    'end_datetime' - datetime of shift end on given timestamp,
    'actual_start' - datetime of shift start after adding 'begin_check_in_before_shift_start_time',
    'actual_end' - datetime of shift end after adding 'allow_check_out_after_shift_end_time' (None is returned if this is zero)
    :param shift_type_name (str): shift type name for which shift_details are required.
    :param for_timestamp (datetime, optional): Datetime value of checkin, if not provided considers current datetime
    """
    if not shift_type_name:
        return {}

    if for_timestamp is None:
        for_timestamp = now_datetime()

    shift_type = frappe.get_doc("Shift Type", shift_type_name)
    shift_actual_start = shift_type.start_time - timedelta(
        minutes=shift_type.begin_check_in_before_shift_start_time
    )

    if shift_type.start_time > shift_type.end_time:
        # shift spans accross 2 different days
        if get_time(for_timestamp.time()) >= get_time(shift_actual_start):
            # if for_timestamp is greater than start time, it's within the first day
            start_datetime = (
                datetime.combine(for_timestamp, datetime.min.time())
                + shift_type.start_time
            )
            for_timestamp = for_timestamp + timedelta(days=1)
            end_datetime = (
                datetime.combine(for_timestamp, datetime.min.time())
                + shift_type.end_time
            )

        elif get_time(for_timestamp.time()) < get_time(shift_actual_start):
            # if for_timestamp is less than start time, it's within the second day
            end_datetime = (
                datetime.combine(for_timestamp, datetime.min.time())
                + shift_type.end_time
            )
            for_timestamp = for_timestamp + timedelta(days=-1)
            start_datetime = (
                datetime.combine(for_timestamp, datetime.min.time())
                + shift_type.start_time
            )
    else:
        # start and end timings fall on the same day
        start_datetime = (
            datetime.combine(for_timestamp, datetime.min.time()) + shift_type.start_time
        )
        end_datetime = (
            datetime.combine(for_timestamp, datetime.min.time()) + shift_type.end_time
        )

    actual_start = start_datetime - timedelta(
        minutes=shift_type.begin_check_in_before_shift_start_time
    )
    actual_end = end_datetime + timedelta(
        minutes=shift_type.allow_check_out_after_shift_end_time
    )

    return frappe._dict(
        {
            "shift_type": shift_type,
            "start_datetime": start_datetime,
            "end_datetime": end_datetime,
            "actual_start": actual_start,
            "actual_end": actual_end,
        }
    )


def get_exact_shift(shifts: List, for_timestamp: datetime) -> Dict:
    """Returns the shift details (dict) for the exact shift in which the 'for_timestamp' value falls among multiple shifts"""
    shift_details = dict()
    timestamp_list = []

    for shift in shifts:
        if shift:
            timestamp_list.extend([shift.actual_start, shift.actual_end])
        else:
            timestamp_list.extend([None, None])

    timestamp_index = None
    for index, timestamp in enumerate(timestamp_list):
        if not timestamp:
            continue

        if for_timestamp < timestamp:
            timestamp_index = index
        elif for_timestamp == timestamp:
            # on timestamp boundary
            if index % 2 == 1:
                timestamp_index = index
            else:
                timestamp_index = index + 1

        if timestamp_index:
            break

    if timestamp_index and timestamp_index % 2 == 1:
        shift_details = shifts[int((timestamp_index - 1) / 2)]

    return shift_details


############################################
############## Attendance ############
############################################
def get_duplicate_attendance_record(employee, attendance_date, shift, name=None):
    attendance = frappe.qb.DocType("Attendance")
    query = (
        frappe.qb.from_(attendance)
        .select(attendance.name)
        .where((attendance.employee == employee) & (attendance.docstatus < 2))
    )

    if shift:
        query = query.where(
            Criterion.any(
                [
                    Criterion.all(
                        [
                            ((attendance.shift.isnull()) | (attendance.shift == "")),
                            (attendance.attendance_date == attendance_date),
                        ]
                    ),
                    Criterion.all(
                        [
                            ((attendance.shift.isnotnull()) | (attendance.shift != "")),
                            (attendance.attendance_date == attendance_date),
                            (attendance.shift == shift),
                        ]
                    ),
                ]
            )
        )
    else:
        query = query.where((attendance.attendance_date == attendance_date))

    if name:
        query = query.where(attendance.name != name)

    return query.run(as_dict=True)


def get_overlapping_shift_attendance(employee, attendance_date, shift, name=None):
    if not shift:
        return {}

    attendance = frappe.qb.DocType("Attendance")
    query = (
        frappe.qb.from_(attendance)
        .select(attendance.name, attendance.shift)
        .where(
            (attendance.employee == employee)
            & (attendance.docstatus < 2)
            & (attendance.attendance_date == attendance_date)
            & (attendance.shift != shift)
        )
    )

    if name:
        query = query.where(attendance.name != name)

    overlapping_attendance = query.run(as_dict=True)

    if overlapping_attendance and has_overlapping_timings(
        shift, overlapping_attendance[0].shift
    ):
        return overlapping_attendance[0]
    return {}


def mark_attendance(
    employee,
    attendance_date,
    status,
    shift=None,
    leave_type=None,
    ignore_validate=False,
    late_entry=False,
    early_exit=False,
):
    if get_duplicate_attendance_record(employee, attendance_date, shift):
        return

    if get_overlapping_shift_attendance(employee, attendance_date, shift):
        return

    company = frappe.db.get_value("Employee", employee, "company")
    attendance = frappe.get_doc(
        {
            "doctype": "Attendance",
            "employee": employee,
            "attendance_date": attendance_date,
            "status": status,
            "company": company,
            "shift": shift,
            "leave_type": leave_type,
            "late_entry": late_entry,
            "early_exit": early_exit,
        }
    )
    attendance.flags.ignore_validate = ignore_validate
    attendance.insert()
    attendance.submit()
    return attendance.name


############################################
############## Employee Checkin ############
############################################
def mark_attendance_and_link_log(
    logs,
    attendance_status,
    attendance_date,
    working_hours=None,
    late_entry=False,
    early_exit=False,
    in_time=None,
    out_time=None,
    shift=None,
):
    """Creates an attendance and links the attendance to the Employee Checkin.
    Note: If attendance is already present for the given date, the logs are marked as skipped and no exception is thrown.
    :param logs: The List of 'Employee Checkin'.
    :param attendance_status: Attendance status to be marked. One of: (Present, Absent, Half Day, Skip). Note: 'On Leave' is not supported by this function.
    :param attendance_date: Date of the attendance to be created.
    :param working_hours: (optional)Number of working hours for the given date.
    """

    log_names = [x.name for x in logs]
    employee = logs[0].employee
    if flt(working_hours) > 0 and shift and frappe.db.exists("Shift Type", shift):
        shift_doc = frappe.get_doc("Shift Type", shift)
        if flt(shift_doc.max_working_hours) > 0 and flt(working_hours) > flt(shift_doc.max_working_hours):
            working_hours = flt(shift_doc.max_working_hours)

    if attendance_status == "Skip":
        frappe.db.sql(
            """update `tabEmployee Checkin`
            set skip_auto_attendance = %s
            where name in %s""",
            ("1", log_names),
        )
        return None
    elif attendance_status in ("Present", "Absent", "Half Day"):
        employee_doc = frappe.get_doc("Employee", employee)
        duplicate = get_duplicate_attendance_record(employee, attendance_date, shift)
        overlapping = get_overlapping_shift_attendance(employee, attendance_date, shift)

        if not duplicate and not overlapping:
            doc_dict = {
                "doctype": "Attendance",
                "employee": employee,
                "attendance_date": attendance_date,
                "status": attendance_status,
                "working_hours": working_hours,
                "company": employee_doc.company,
                "shift": shift,
                "late_entry": late_entry,
                "early_exit": early_exit,
                "in_time": in_time,
                "out_time": out_time,
            }
            attendance = frappe.get_doc(doc_dict).insert()
            attendance.submit()
            frappe.db.sql(
                """update `tabEmployee Checkin`
                set attendance = %s
                where name in %s""",
                (attendance.name, log_names),
            )
            return attendance
        else:
            frappe.db.sql(
                """update `tabEmployee Checkin`
                set skip_auto_attendance = %s
                where name in %s""",
                ("1", log_names),
            )
            if duplicate:
                for dattendance in duplicate:
                    duplicate_att = frappe.get_doc("Attendance", dattendance.name)
                    duplicate_att.db_set("early_exit", early_exit, update_modified=False)
                    duplicate_att.db_set("late_entry", late_entry, update_modified=False)
                    duplicate_att.db_set("working_hours", working_hours, update_modified=False)
                    duplicate_att.db_set("in_time", in_time, update_modified=False)
                    duplicate_att.db_set("out_time", out_time, update_modified=False)
                    duplicate_att.db_set("status", attendance_status, update_modified=False)
            return None
    else:
        frappe.throw(_("{} is an invalid Attendance Status.").format(attendance_status))


def calculate_working_hours(logs, check_in_out_type, working_hours_calc_type):
    """Given a set of logs in chronological order calculates the total working hours based on the parameters.
    Zero is returned for all invalid cases.
    :param logs: The List of 'Employee Checkin'.
    :param check_in_out_type: One of: 'Alternating entries as IN and OUT during the same shift', 'Strictly based on Log Type in Employee Checkin'
    :param working_hours_calc_type: One of: 'First Check-in and Last Check-out', 'Every Valid Check-in and Check-out'
    """
    total_hours = 0
    in_time = out_time = None
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
                logs[first_in_log_index]
                if first_in_log_index or first_in_log_index == 0 
                else None
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
    return total_hours, in_time, out_time


def time_diff_in_hours(start, end):
    return round(float((end - start).total_seconds()) / 3600, 2)


def find_index_in_dict(dict_list, key, value):
    return next((index for (index, d) in enumerate(dict_list) if d[key] == value), None)

def regenerate_repayment_schedule(repayment , loan, cancel=0):
    loan_doc = frappe.get_doc("Loan", loan)
    self = frappe.get_doc("Loan Repayment", repayment)
    repayment_schedule_length = len(loan_doc.get("repayment_schedule"))

    repayment_amount = self.amount_paid
    if repayment_schedule_length:
        for row in loan_doc.repayment_schedule:
            if row.paid_amount >= row.principal_amount: continue
            if repayment_amount > row.principal_amount-row.paid_amount:
                diff = row.principal_amount - row.paid_amount
                row.paid_amount = row.paid_amount + diff
                repayment_amount = repayment_amount - diff
            else:
                row.paid_amount = row.paid_amount + repayment_amount 
                repayment_amount = 0
            if repayment_amount <= 0: break
        loan_doc.save(ignore_permissions=True)