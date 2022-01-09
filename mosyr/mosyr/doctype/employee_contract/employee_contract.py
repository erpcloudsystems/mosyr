# Copyright (c) 2022, AnvilERP and contributors
# For license information, please see license.txt

# import frappe
import frappe
from frappe.model.document import Document

class EmployeeContract(Document):
	def validate(self):
		if self.from_api:
			if self.nid:
				employee_number = frappe.get_value("Employee",{'nid':self.nid},'name')
				self.employee = employee_number



