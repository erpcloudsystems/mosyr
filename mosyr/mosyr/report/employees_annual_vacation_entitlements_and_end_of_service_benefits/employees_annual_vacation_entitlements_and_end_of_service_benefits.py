# Copyright (c) 2024, AnvilERP and contributors
# For license information, please see license.txt

from typing import Dict, List, Optional, Tuple
from datetime import datetime
import frappe
from frappe import _
from frappe.utils import getdate, nowdate, flt
from erpnext.hr.doctype.leave_application.leave_application import get_leave_details
# from erpnext.payroll.doctype.salary_structure_assignment.salary_structure_assignment import	get_assigned_salary_structure
def get_assigned_salary_structure(employee, on_date):
	if not employee or not on_date:
		return None
	salary_structure = frappe.db.sql(
		"""
		select salary_structure, base as base from `tabSalary Structure Assignment`
		where employee=%(employee)s
		and docstatus = 1
		and %(on_date)s >= from_date order by from_date desc limit 1""",
		{
			"employee": employee,
			"on_date": on_date,
		},
	)
	return salary_structure[0][0] if salary_structure else None, salary_structure[0][1] if salary_structure else None
def get_department_leave_approver_map(department: Optional[str] = None):
	# get current department and all its child
	department_list = frappe.get_list(
		"Department",
		filters={"disabled": 0},
		or_filters={"name": department, "parent_department": department},
		pluck="name",
	)
	# retrieve approvers list from current department and from its subsequent child departments
	approver_list = frappe.get_all(
		"Department Approver",
		filters={"parentfield": "leave_approvers", "parent": ("in", department_list)},
		fields=["parent", "approver"],
		as_list=True,
	)

	approvers = {}

	for k, v in approver_list:
		approvers.setdefault(k, []).append(v)

	return approvers

def execute(filters=None):
	leave_types = frappe.db.sql_list("select name from `tabLeave Type` WHERE allow_encashment=1 AND is_annual_leave=1 order by name asc")

	columns = get_columns()
	data = get_data(filters, leave_types)
	return columns, data


def get_columns():
	return [
		{
			"label": _("Employee ID"),
   		 	"fieldtype": "Link", 
			"options": "Employee", 
			"fieldname": "employee", 
			"width": 150
		},
		{
			"label": _("Employee Name"),
			"fieldtype": "Data",
			"fieldname": "employee_name",
			"width": 150,
		},
		{
			"label": _("Nationality"),
			"fieldtype": "Data",
			"fieldname": "nationality",
			"width": 200,
		},
		{
			"label": _("Monthly salary"), 
			"fieldtype": "Currency", 
			"fieldname": "monthly_salary", 
			"width": 150
		},
		{
			"label": _("Date Of Joining"), 
			"fieldtype": "Date", 
			"fieldname": "date_of_joining", 
			"width": 150
		},
		{
			"label": _("The number of working days"),
			"fieldtype": "Int",
			"fieldname": "working_days",
			"width": 150,
		},
		{
			"label": _("Holiday balance"),
			"fieldtype": "Int",
			"fieldname": "holiday_balance",
			"width": 150,
		},
		{
			"label": _("The amount due"),
			"fieldtype": "Currency",
			"fieldname": "amount_due",
			"width": 150,
		},
	]



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
		fields=["name", "employee_name", "department", "user_id", "leave_approver","custom_date_of_joining"],
	)

	department_approver_map = get_department_leave_approver_map(filters.get("department"))
	ss_date = filters.get('date', getdate(nowdate())) or getdate(nowdate())
	data = []
	for employee in active_employees:
		leave_approvers = department_approver_map.get(employee.department_name, [])
		salary_structure = get_assigned_salary_structure(employee['name'], ss_date)
		per_day_encashment = frappe.db.get_value("Salary Structure", salary_structure[0], "leave_encashment_amount_per_day")
		monthly_salary = salary_structure[1]
		custom_date_of_joining = datetime(employee.custom_date_of_joining.year, 
                                  employee.custom_date_of_joining.month, 
                                  employee.custom_date_of_joining.day)
		current_date = datetime.now()
		difference = current_date - custom_date_of_joining
		if employee.leave_approver:
			leave_approvers.append(employee.leave_approver)

		if (
			(len(leave_approvers) and user in leave_approvers)
			or (user in ["Administrator", employee.user_id])
			or ("HR Manager" in frappe.get_roles(user))
		):
			row = {"employee": employee.name, "employee_name": employee.employee_name ,"date_of_joining" : employee.custom_date_of_joining,
		  	"monthly_salary":monthly_salary,
		  		"holiday_balance": 0,
		  		"amount_due": 0,
				  "working_days":difference.days
		  	}
			available_leave = get_leave_details(employee.name, filters.date)
			total_leaves = 0
			remaining = 0
			remaining_amount = 0
			for leave_type in leave_types:
				if leave_type in available_leave["leave_allocation"]:
					remaining = available_leave["leave_allocation"][leave_type]["remaining_leaves"]
			remaining_amount = flt(per_day_encashment) * remaining
			row['holiday_balance'] += remaining
			row['amount_due'] = remaining_amount
		data.append(row)
	return data
