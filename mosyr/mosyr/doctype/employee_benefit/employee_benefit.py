# Copyright (c) 2022, AnvilERP and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import flt
from frappe.model.document import Document

class EmployeeBenefit(Document):
	def on_submit(self):
		eadd = frappe.new_doc('Additional Salary')
		eadd.employee = self.employee
		eadd.amount = flt(self.amount)
		eadd.salary_component = self.addition_type
		eadd.payroll_date = self.payroll_month
		eadd.reason = self.notes
		eadd.employee_benefit = self.name
		eadd.save()
		eadd.submit()

	def on_cancel(self):
		eadd = frappe.get_list("Additional Salary", {"employee_benefit":self.name})
		if eadd:
			for ea in eadd:
				doc = frappe.get_doc("Additional Salary", ea["name"])
				doc.cancel()
