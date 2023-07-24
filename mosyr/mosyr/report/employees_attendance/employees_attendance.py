# Copyright (c) 2023, AnvilERP and contributors
# For license information, please see license.txt

import frappe
from frappe import _

from frappe.utils import time_diff_in_hours, time_diff

import datetime

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data


def get_columns():
    columns = [
        {
            "label": _("Employee"),
            "fieldname": "employee_name",
            "fieldtype": "Link",
            "options": "Employee",
            "width": 230,
        },
        {
            "label": _("Date"),
            "fieldname": "attendance_date",
            "fieldtype": "Date",
            "width": 100,
        },
        {
            "label": _("In"),
            "fieldname": "time_in",
            "fieldtype": "Data",
            "default": "0",
            "width": 80,
        },
        {
            "label": _("Out"),
            "fieldname": "time_out",
            "fieldtype": "Data",
            "default": "0",
            "width": 80,
        },
        {
            "label": _("Extra In"),
            "fieldname": "extra_time_in",
            "fieldtype": "Data",
            "default": "0",
            "width": 80,
        },
        {
            "label": _("Extra Out"),
            "fieldname": "extra_time_out",
            "fieldtype": "Data",
            "default": "0",
            "width": 80,
        },
        {
            "label": _("Late Entry"),
            "fieldname": "late_entry",
            "fieldtype": "Data",
            "default": "0",
            "width": 80,
        },
        {
            "label": _("Early Exit"),
            "fieldname": "early_exit",
            "fieldtype": "Data",
            "default": "0",
            "width": 80,
        },
        {
            "label": _("Extra Early"),
            "fieldname": "extra_early",
            "fieldtype": "Data",
            "default": "0",
            "width": 80,
        },
        {
            "label": _("Overtime"),
            "fieldname": "overtime",
            "fieldtype": "Data",
            "default": "0",
            "width": 80,
        },
        {
            "label": _("Required hours"),
            "fieldname": "reqd_hours",
            "fieldtype": "Data",
            "default": "0",
            "width": 100,
        },
        {
            "label": _("Actual hours"),
            "fieldname": "actual_hours",
            "fieldtype": "Data",
            "default": "0",
            "width": 100,
        },
        {
            "label": _("Status"),
            "fieldname": "status",
            "fieldtype": "Data",
            "default": "0",
            "width": 120,
        }
    ]

    return columns


def get_data(filters):
    conds = get_conditions(filters)
    sql = """
        SELECT
            emp.name, emp.first_name as employee_name, at.name as attendance_name, at.shift, at.status as status,
            at.attendance_date
        FROM
            `tabEmployee` as emp
        LEFT JOIN
            `tabAttendance` at
        ON
            at.employee = emp.name
        WHERE
            {0}
    """.format(
        conds
    )
    data = frappe.db.sql(sql, as_dict=1)
    print("****************************************************************************")
    print(data)
    print("****************************************************************************")
    # Get Attendance Details
    # data = [{'employee_name': 'محمد احمد الكاف', 'status': 'Absent'}]
    for row in data:
        if row.get("shift") and frappe.db.exists("Shift Type", row.get("shift")):
            shift_doc = frappe.get_doc("Shift Type", row.get("shift"))
            reqd_hours = time_diff_in_hours(
                shift_doc.end_time, shift_doc.start_time)
            row.update({"reqd_hours": reqd_hours})

            if row.get("status") != "Absent":
                # GET Checkin Details
                res = get_checkin_details(row.get("shift"), row.get(
                    "name"), row.get("attendance_date"))
                
                row.update(res)

    print("*99999999999")
    print(data)
    print("*99999999999")
    return data


def get_conditions(filters):
    conditions = "1=1"
    if filters.get("employee"):
        conditions += " and emp.name = '{0}'".format(filters.get("employee"))

    if filters.get("from_date"):
        conditions += " and at.attendance_date >= '{0}'".format(
            filters.get("from_date"))

    if filters.get("to_date"):
        conditions += " and at.attendance_date <= '{0}'".format(
            filters.get("to_date"))

    if filters.get("company"):
        conditions += " and emp.company = '{0}'".format(filters.get("company"))

    return conditions


def get_checkin_details(shift, employee, date):
    shift_doc = frappe.get_doc("Shift Type", shift)
    checkin_list = frappe.db.sql("""
        SELECT name
        FROM `tabEmployee Checkin`
        WHERE shift = '{0}' and employee = '{1}' and DATE(time) = '{2}' and log_type = 'IN'
    """.format(shift, employee, date), as_dict=1)

    checkout_list = frappe.db.sql("""
        SELECT name
        FROM `tabEmployee Checkin`
        WHERE shift = '{0}' and employee = '{1}' and DATE(time) = '{2}' and log_type = 'OUT'
    """.format(shift, employee, date), as_dict=1)

    checkin = checkin_list[0] if checkin_list else ""
    checkout = checkout_list[-1] if checkout_list else ""
    
    if checkin:
        checkin_doc = frappe.get_doc("Employee Checkin", checkin.get("name"))
        time_in = checkin_doc.time.time()
        # Calculate Late Entry
        shift_start = datetime.datetime.strptime(str(shift_doc.start_time), "%H:%M:%S")
        start_dt1 = checkin_doc.time.time()
        start_dt2 = shift_start.time()
        start_time_difference = datetime.timedelta(hours=start_dt1.hour - start_dt2.hour, minutes=start_dt1.minute - start_dt2.minute, seconds=start_dt1.second - start_dt2.second)
        late_entry = start_time_difference
    
    if checkout:
        checkout_doc = frappe.get_doc("Employee Checkin", checkout.get("name"))
        time_out = checkout_doc.time.time()
        # Calculate Early Exit
        shift_end = datetime.datetime.strptime(str(shift_doc.end_time), "%H:%M:%S")
        time2 = shift_end.time()
        time1 = checkout_doc.time.time()
        time_difference = datetime.timedelta(hours=time2.hour - time1.hour, minutes=time2.minute - time1.minute, seconds=time2.second - time1.second)
        early_exit = time_difference
        
    result = {
        "time_in": checkin_doc.time.time() if checkin else "",
        "time_out": checkout_doc.time.time() if checkout else "",
        "late_entry": late_entry if checkin else "",
        "early_exit": early_exit if checkout else "",
    }
    
    return result
    print("mmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmm")
    print(shift, employee, date)
    print(checkin_list)
    print("mmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmm")
