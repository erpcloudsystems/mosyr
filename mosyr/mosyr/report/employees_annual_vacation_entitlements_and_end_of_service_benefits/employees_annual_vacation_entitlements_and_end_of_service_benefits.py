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
			"label": _("Working Days"),
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
			"label": _("Amount Due"),
			"fieldtype": "Currency",
			"fieldname": "amount_due",
			"width": 150,
		},
		{
			"label": _("End of Service <br> Before 5 years"),
			"fieldtype": "Currency",
			"fieldname": "before_year",
			"width": 150,
		},
		{
			"label": _("End of Service <br> After 5 years"),
			"fieldtype": "Currency",
			"fieldname": "after_year",
			"width": 150,
		},

		{
			"label": _("Cash Custody"),
			"fieldtype": "Currency",
			"fieldname": "cash_custody",
			"width": 150,
		},
		{
			"label": _("Custody"),
			"fieldtype": "Data",
			"fieldname": "custody",
			"width": 150,
		},
		{
			"label": _("Custody Value"),
			"fieldtype": "Currency",
			"fieldname": "custody_value",
			"width": 150,
		},
		{
			"label": _("Loan"),
			"fieldtype": "Currency",
			"fieldname": "total_amount_remaining",
			"width": 150,
		},
		{
			"label": _("Total"),
			"fieldtype": "Currency",
			"fieldname": "total",
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
		emp = frappe.get_doc("Employee",  employee.name)
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
			row = {
				"employee": employee.name, "employee_name": employee.employee_name ,"date_of_joining" : employee.custom_date_of_joining,
				"nationality": emp.identity[0].nationality if emp.identity else _("No data to show"),
				"monthly_salary":monthly_salary,
		  		"holiday_balance": 0,
		  		"amount_due": 0,
				"working_days":difference.days
		  	}
			diff_years = difference.days / 365
			before_year = diff_years
			after_year = 0
			if diff_years >= 5:
				before_year = 5
				after_year = diff_years - before_year
			
			available_leave = get_leave_details(employee.name, filters.date)
			total_leaves = 0
			remaining = 0
			remaining_amount = 0
			for leave_type in leave_types:
				if leave_type in available_leave["leave_allocation"]:
					remaining = available_leave["leave_allocation"][leave_type]["remaining_leaves"]
			salary_slip = frappe.db.sql(f"""
				SELECT gross_pay From `tabSalary Slip` where employee = '{employee.name}'	and docstatus = 1 ORDER by  creation DESC LIMIT 1
			""",as_dict = 1)
		
			# gross_pay = frappe.get_last_doc('Salary Slip', filters={"employee": employee.name}).gross_pay
			row['before_year'] = 0
			if salary_slip:
				row['before_year'] = (salary_slip[0]['gross_pay']/ 2) * before_year
			row['after_year'] = 0
			if salary_slip:
				row['after_year'] = salary_slip[0]['gross_pay'] * after_year
			remaining_amount = flt(per_day_encashment) * remaining
			row['holiday_balance'] += remaining
			row['amount_due'] = remaining_amount
			estimated_value = frappe.db.sql(f"""
				SELECT estimated_value From `tabCash Custody` where recipient_employee = '{employee.name}'	
			""",as_dict = 1)
			row['cash_custody'] = 0
			if estimated_value:
				row['cash_custody'] = estimated_value[0]['estimated_value']
			custody = frappe.db.sql(f"""
				SELECT type, custody_value From `tabCustody` where recipient = '{employee.name}' and status != 'Returned'
			""",as_dict = 1)
			custody_devices= []
			custody_value = 0
			for type_device in custody:
				custody_value += type_device['custody_value']
				custody_devices.append(type_device['type'])
			row['custody'] = _("No data to show")
			row['custody_value'] = custody_value
			if custody_devices:
				row['custody'] = "/ ".join(custody_devices)
			loans = frappe.db.sql(f"""
				SELECT 	total_amount_remaining From `tabLoan` where applicant = '{employee.name}' and total_amount_remaining != 0
			""",as_dict = 1)
			total_amount_remaining = 0
			for loan in loans:
				total_amount_remaining += loan['total_amount_remaining']
			row['total_amount_remaining'] = total_amount_remaining
			monthly_salary = row['monthly_salary'] if row['monthly_salary'] is not None else 0.0
			amount_due = row['amount_due'] if row['amount_due'] is not None else 0.0
			cash_custody = row['cash_custody'] if row['cash_custody'] is not None else 0.0
			custody_value = row['custody_value'] if row['custody_value'] is not None else 0.0
			total_amount_remaining = row['total_amount_remaining'] if row['total_amount_remaining'] is not None else 0.0
			
			after_year = row['after_year'] if row['after_year'] is not None else 0.0
			before_year = row['before_year'] if row['before_year'] is not None else 0.0
			row['total'] = monthly_salary + after_year + before_year + amount_due - cash_custody  - total_amount_remaining

		
		data.append(row)
	return data
