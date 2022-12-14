# Copyright (c) 2022, AnvilERP and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import getdate, nowdate, flt
from erpnext.hr.doctype.leave_application.leave_application import get_leave_details
from erpnext.hr.report.employee_leave_balance.employee_leave_balance import get_department_leave_approver_map
from erpnext.payroll.doctype.salary_structure_assignment.salary_structure_assignment import	get_assigned_salary_structure

def execute(filters=None):
    leave_types = frappe.db.sql_list("select name from `tabLeave Type` WHERE allow_encashment=1 AND is_annual_leave=1 order by name asc")

    columns = get_columns(leave_types)
    data = get_data(filters, leave_types)

    return columns, data


def get_columns(leave_types):
    columns = [
        _("Employee") + ":Link.Employee:150",
        _("Employee Name") + "::200",
        _("Department") + "::150",
    ]

    for leave_type in leave_types:
        columns.append(_(leave_type) + " " + _("Total") + ":Float:160")
        columns.append(_(leave_type) + " " + _("Remaining") + ":Float:160")
        columns.append(_(leave_type) + " " + _("Balance") + ":Float:160")

    return columns


def get_conditions(filters):
    conditions = {
        "company": filters.company,
    }
    if filters.get("employee_status"):
        conditions.update({"status": filters.get("employee_status")})
    if filters.get("department"):
        conditions.update({"department": filters.get("department")})
    if filters.get("employee"):
        conditions.update({"employee": filters.get("employee")})

    return conditions


def get_data(filters, leave_types):
    user = frappe.session.user
    conditions = get_conditions(filters)

    active_employees = frappe.get_all(
        "Employee",
        filters=conditions,
        fields=["name", "employee_name", "department", "user_id", "leave_approver"],
    )

    department_approver_map = get_department_leave_approver_map(filters.get("department"))
    ss_date = filters.get('date', getdate(nowdate())) or getdate(nowdate())
    data = []
    for employee in active_employees:
        leave_approvers = department_approver_map.get(employee.department_name, [])
        salary_structure = get_assigned_salary_structure(employee['name'], ss_date)
        per_day_encashment = frappe.db.get_value("Salary Structure", salary_structure, "leave_encashment_amount_per_day")
        
        if employee.leave_approver:
            leave_approvers.append(employee.leave_approver)

        if (
            (len(leave_approvers) and user in leave_approvers)
            or (user in ["Administrator", employee.user_id])
            or ("HR Manager" in frappe.get_roles(user))
        ):
            row = [employee.name, employee.employee_name, employee.department]
            available_leave = get_leave_details(employee.name, filters.date)
            for leave_type in leave_types:
                total_leaves = 0
                remaining = 0
                remaining_amount = 0
                if leave_type in available_leave["leave_allocation"]:
                    # opening balance
                    total_leaves = available_leave["leave_allocation"][leave_type]["total_leaves"]
                    remaining = available_leave["leave_allocation"][leave_type]["remaining_leaves"]
                    remaining_amount = flt(per_day_encashment) * remaining

                row += [total_leaves]
                row += [remaining]
                row += [remaining_amount]

            data.append(row)

    return data
