
import json

import frappe 
from frappe.utils import getdate
from frappe import _
from json import loads
from six import string_types
from erpnext.hr.doctype.leave_policy_assignment.leave_policy_assignment import show_assignment_submission_status
@frappe.whitelist()
def create_assignment_for_multiple_employees(employees, data):
	if isinstance(employees, string_types):
		employees = json.loads(employees)

	if isinstance(data, string_types):
		data = frappe._dict(json.loads(data))

	docs_name = []
	failed = []

	for employee in employees:
		data_of_employee = None
		if data.assignment_based_on == "Joining Date":
			data_of_employee = frappe.get_doc("Employee", employee)
		assignment = frappe.new_doc("Leave Policy Assignment")
		assignment.employee = employee
		assignment.assignment_based_on = data.assignment_based_on or None
		assignment.leave_policy = data.leave_policy 
		assignment.effective_from = data_of_employee.date_of_joining or getdate(data.effective_from)
		assignment.effective_to = data_of_employee.contract_end_date or getdate(data.effective_to)
		assignment.leave_period = data.leave_period or None
		assignment.carry_forward = data.carry_forward
		assignment.save()

		savepoint = "before_assignment_submission"

		try:
			frappe.db.savepoint(savepoint)
			assignment.submit()
		except Exception as e:
			frappe.db.rollback(save_point=savepoint)
			frappe.log_error(title=f"Leave Policy Assignment submission failed for {assignment.name}")
			failed.append(assignment.name)

		docs_name.append(assignment.name)

	if failed:
		show_assignment_submission_status(failed)

	return docs_name