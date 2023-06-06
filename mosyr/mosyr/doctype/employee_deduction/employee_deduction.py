# Copyright (c) 2022, AnvilERP and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import flt, cint
from frappe.model.document import Document

class EmployeeDeduction(Document):
	def on_submit(self):
		eadd = frappe.new_doc('Additional Salary')
		eadd.employee = self.employee
		eadd.amount = flt(self.amount)
		eadd.salary_component = 'Deduction'
		eadd.payroll_date = self.payroll_month
		eadd.reason = self.notes
		eadd.employee_deduction = self.name
		eadd.save()
		eadd.submit()

	def on_cancel(self):
		eadd = frappe.get_list("Additional Salary", {"employee_deduction":self.name})
		if eadd:
			for ea in eadd:
				doc = frappe.get_doc("Additional Salary", ea["name"])
				doc.cancel()

	@frappe.whitelist()
	def get_salary_per_day(self, employee):
		base = 0
		months_days = 22

		lst = frappe.get_list(
			"Salary Structure Assignment",
			filters={"employee": employee, "docstatus": 1},
			fields=["from_date", "base", "company"],
			order_by="from_date desc",
		)
		if len(lst) > 0:
			base = flt(lst[0].base)
			company = lst[0].company
			mdays = frappe.get_list(
				"Company",
				filters={"name": company},
				fields=["month_days"]
			)
			if len(mdays) > 0:
				months_days = cint(mdays[0].month_days)
				if months_days not in [22, 28, 29, 30]:
					months_days = 22
			base = base / months_days
		return base
