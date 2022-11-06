# Copyright (c) 2022, AnvilERP and contributors
# For license information, please see license.txt

import datetime

import frappe
from frappe import _
from frappe.utils import flt
from frappe.model.document import Document

class EmployeeDeduction(Document):
	def validate(self):
		try:
			datetime.datetime.strptime(self.payroll_month, '%Y-%m')
		except ValueError:
			frappe.throw(_("Incorrect data format, should be YYYY-MM"))
			return

	def on_submit(self):
		eadd = frappe.new_doc('Additional Salary')
		eadd.employee = self.employee
		eadd.amount = flt(self.amount)
		eadd.salary_component = 'Deduction'
		eadd.payroll_date = datetime.datetime.strptime(f'{self.payroll_month}-01', '%Y-%m-%d')
		eadd.reason = self.notes
		eadd.employee_deduction = self.name
		eadd.save()
		eadd.submit()
		
	def on_cancel(self):
		eadd = frappe.get_list('Additional Salary' ,{"employee_deduction":self.name})
		if eadd:
			for ea in eadd:
				doc = frappe.get_doc("Additional Salary",ea['name'])
				doc.cancel()