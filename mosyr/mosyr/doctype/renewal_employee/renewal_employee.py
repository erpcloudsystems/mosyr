# Copyright (c) 2024, AnvilERP and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import getdate, today
import datetime
class RenewalEmployee(Document):
	@frappe.whitelist()
	def get_employee_will_be_expired(self):
		filters ={}
		if self.employee:
			filters['name'] = self.employee
		filters['status'] = self.status
		employees = []
		emps = frappe.db.get_list("Employee", filters=filters, order_by='name')
		for emp in emps:
			emp_doc = frappe.get_doc("Employee", emp.name)
			end_date = emp_doc.get('contract_end_date')
    
			if end_date:  # Check if end_date exists
				# Calculate the difference in days
				diff_days = end_date - datetime.date.today()
				if diff_days.days <= 30:
					employees.append({
						"employee": emp_doc.name,
						"employee_name": emp_doc.employee_name,
						"end_of_contract": end_date,
					})
		return employees
	@frappe.whitelist()
	def update_end_contract(self):
		employees = []
		leaves = []
		for emp in self.employees:
			emp_doc = frappe.get_doc("Employee", emp.employee)
			emp_end_of_contract = emp.end_of_contract
			if isinstance(emp.end_of_contract, str):
				emp_end_of_contract = datetime.datetime.strptime(emp.end_of_contract, "%Y-%m-%d").date()
			else:
				emp_end_of_contract = emp.end_of_contract
			if emp_doc.contract_end_date > emp_end_of_contract:
				frappe.msgprint(f"Renewal End Contract Date must be large Employee Contract")
				continue
			emp_doc.contract_end_date = emp.end_of_contract
			emp_doc.status = "Active"
			employees.append(emp_doc)
		for emp in employees:
			emp.save()
		for emp in employees:
			leave_policy_assignment = frappe.db.get_list("Leave Policy Assignment", filters={"employee":emp.name, "assignment_based_on": "Joining Date"},
    			page_length=1)
			for leave in leave_policy_assignment:
				frappe.db.set_value("Leave Policy Assignment", leave.name, "effective_to", emp.contract_end_date)

		pass
	pass
