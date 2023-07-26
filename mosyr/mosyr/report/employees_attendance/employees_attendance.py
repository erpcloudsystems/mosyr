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
            "label": _("Overtime In"),
            "fieldname": "overtime_in",
            "fieldtype": "Data",
            "default": "0",
            "width": 80,
        },
        {
            "label": _("Overtime Out"),
            "fieldname": "overtime_out",
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
    checkin_time = 0
    checkout_time = 0
    actual_hrs = ""
    
    if checkin:
        checkin_doc = frappe.get_doc("Employee Checkin", checkin.get("name"))
        time_in = checkin_doc.time.time()
        overtime_in = ""
        late_entry = ""

        # Calculate Checkin time's
        shift_start = datetime.datetime.strptime(str(shift_doc.start_time), "%H:%M:%S")
        start_dt1 = checkin_doc.time.time()
        checkin_time = checkin_doc.time.time()
        start_dt2 = shift_start.time()

        if start_dt2 > start_dt1:
            # this mean's Overtime IN
            # Calculate Overtime IN
            start_time_diff = datetime.timedelta(hours=start_dt2.hour - start_dt1.hour, minutes=start_dt2.minute - start_dt1.minute, seconds=start_dt2.second - start_dt1.second)
            overtime_in = start_time_diff

        if start_dt2 < start_dt1:
            # this mean's Late Entry
               # Calculate Late Entry
            start_time_difference = datetime.timedelta(hours=start_dt1.hour - start_dt2.hour, minutes=start_dt1.minute - start_dt2.minute, seconds=start_dt1.second - start_dt2.second)
            late_entry = start_time_difference
        

    if checkout:
        checkout_doc = frappe.get_doc("Employee Checkin", checkout.get("name"))
        time_out = checkout_doc.time.time()
        early_exit = ""
        overtime_out = ""
        
        # Calculate Checkout time's
        shift_end = datetime.datetime.strptime(str(shift_doc.end_time), "%H:%M:%S")
        time2 = shift_end.time()
        time1 = checkout_doc.time.time()
        checkout_time = checkout_doc.time.time()
        
        if time2 > time1:
            # this mean's Early Exit
            # Calculate Early Exit
            time_difference = datetime.timedelta(hours=time2.hour - time1.hour, minutes=time2.minute - time1.minute, seconds=time2.second - time1.second)
            early_exit = time_difference
        
        if time2 < time1:
            # this mean's Overtime OUT
            # Calculate Overtime OUT
            time_difference = datetime.timedelta(hours=time1.hour - time2.hour, minutes=time1.minute - time2.minute, seconds=time1.second - time2.second)
            overtime_out = time_difference
            
    # Calculate Actual Working hours
    if checkin_time and checkout_time:
        actual_hrs = datetime.timedelta(hours=checkout_time.hour - checkin_time.hour, minutes=checkout_time.minute - checkin_time.minute, seconds=checkout_time.second - checkin_time.second)

    result = {
        "time_in": time_in if checkin else "",
        "late_entry": late_entry if checkin else "",
        "overtime_in": overtime_in if checkin else "",
        "time_out": time_out if checkout else "",
        "early_exit": early_exit if checkout else "",
        "overtime_out": overtime_out if checkout else "",
        "actual_hours": actual_hrs
    }
    
    return result
