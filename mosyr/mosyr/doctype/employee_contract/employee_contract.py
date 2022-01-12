# Copyright (c) 2022, AnvilERP and contributors
# For license information, please see license.txt

# import frappe
import frappe
from frappe.model.document import Document
from frappe.utils import cint

class EmployeeContract(Document): pass
	# def validate(self):
	# 	if self.from_api:
	# 		if self.nid:
	# 			emo_name = frappe.get_value("Employee", {'nid':self.nid}, 'name') or False
	# 			if emo_name: self.employee = emo_name
	
	# def on_submit(self):
	# 	if self.from_api:
	# 		employee = frappe.get_doc('Employee', self.employee)
	# 		if self.hiring_start_date_g and cint(employee.from_api) == 1:
	# 			employee.date_of_joining = self.hiring_start_date_g
	# 			employee.valid_data = 1
	# 			employee.from_api = 0
	# 			employee.status = employee.moyser_employee_status
