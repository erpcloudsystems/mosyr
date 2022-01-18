# Copyright (c) 2022, AnvilERP and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class EmployeeDeductions(Document):
	def validate(self):
		if self.from_api:
			if self.nid:
				if frappe.db.exists("Employee", {'nid':self.nid}):
					employee_number = frappe.get_value("Employee",{'nid':self.nid},['name','first_name']) or False
					self.employee_number = employee_number[0]
					self.name1 = employee_number[1]

