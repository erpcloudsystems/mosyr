# Copyright (c) 2023, AnvilERP and contributors
# For license information, please see license.txt

import frappe
from frappe import _
import datetime
from frappe.utils import flt

def execute(filters=None):
	return get_columns(filters),get_data(filters)
	
def get_data(filters):
	# date range
	_from,to = filters.get('from'),filters.get('to')
	
	# conditions
	conditions = " 1=1 "
	if(filters.get("employee")):conditions += f" AND emp.name='{filters.get('employee')}'"
	if(filters.get("company")):conditions += f" AND emp.company='{filters.get('company')}'"
	data = []
	if filters.get("workflow_state") and len(filters.get("workflow_state")) != 0:
		employees = frappe.db.sql(f"""
		         SELECT emp.name as employee, emp.employee_name, emp.department, emp.company
			     FROM `tabEmployee` emp where {conditions}
			     """, as_dict=True)
		exits = frappe.db.sql(f"""
					SELECT SUM(CAST(exit_hours AS FLOAT)) as exit_hours, employee 
					FROM `tabExit Permission`
					WHERE date BETWEEN '{_from}' AND '{to}' and workflow_state='{filters.get("workflow_state")}'
					GROUP BY employee, workflow_state
					""", as_dict=True)
		for emp in employees:
			d = {}
			d.update(emp)
			for ex in exits:
				if ex.employee == emp.employee:
					d.update({
						'exit_hours': datetime.timedelta(hours = flt(ex.exit_hours, 2))
					})
			data.append(d)
	else:
		employees = frappe.db.sql(f"""
		         SELECT emp.name as employee, emp.employee_name, emp.department, emp.company
			     FROM `tabEmployee` emp where {conditions}
			     """, as_dict=True)
		exits = frappe.db.sql(f"""
					SELECT SUM(CAST(exit_hours AS FLOAT)) as exit_hours, workflow_state, employee 
					FROM `tabExit Permission`
					WHERE date BETWEEN '{_from}' AND '{to}'
					GROUP BY employee, workflow_state
					""", as_dict=True)
		for emp in employees:
			d = {}
			d.update(emp)
			for ex in exits:
				if ex.employee == emp.employee:
					if ex.workflow_state == 'Pending':
						d.update({
							'pendeing_hours': datetime.timedelta(hours = flt(ex.exit_hours, 2))
						})
					if ex.workflow_state == 'Approved by HR':
						d.update({
							'approved_hours': datetime.timedelta(hours = flt(ex.exit_hours, 2))
						})
					if ex.workflow_state == 'Rejected':
						d.update({
							'rejected_hours': datetime.timedelta(hours = flt(ex.exit_hours, 2))
						})
			data.append(d)
	return data

def get_columns(filters):

	cols = [
			{
				"label": _("Employee Name"),
				"fieldname": "employee_name",
				"fieldtype": "Data",
				"width": 200
			},
			{
				"label": _("Department"),
				"options":"department",
				"fieldname": "department",
				"fieldtype": "Link",
				"width": 140
			},
			{
				"label": _("Company"),
				"options":"Company",
				"fieldname": "company",
				"fieldtype": "Link",
				"width": 140
			},
	]

	if filters.get("workflow_state") and len(filters.get("workflow_state")) != 0:
		cols += [
			{
				"label": _("Total Hours"),
				"fieldname": "exit_hours",
				"fieldtype": "Time",
				"width": 150
			}
		]
	else:
		cols += [
			{
				"label": _("Pendeing Hours"),
				"fieldname": "pendeing_hours",
				"fieldtype": "Time",
				"width": 150
			},
			{
				"label": _("Approved Hours"),
				"fieldname": "approved_hours",
				"fieldtype": "Time",
				"width": 150
			},
			{
				"label": _("Rejected Hours"),
				"fieldname": "rejected_hours",
				"fieldtype": "Time",
				"width": 150
			},
		]
	return cols

