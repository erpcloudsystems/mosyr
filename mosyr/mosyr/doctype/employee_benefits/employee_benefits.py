# Copyright (c) 2022, AnvilERP and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class EmployeeBenefits(Document):
	def validate(self):
		if self.from_api:
			if self.nid:
				employee_number = frappe.get_value("Employee",{'nid':self.nid},'name')
				self.employee_number = employee_number
