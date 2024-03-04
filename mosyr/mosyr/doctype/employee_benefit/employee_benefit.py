# Copyright (c) 2022, AnvilERP and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import flt
from frappe.model.document import Document

class EmployeeBenefit(Document):
	def on_submit(self):
		query = """
			SELECT name 
			FROM `tabAdditional Salary` 
			WHERE 
				MONTH(payroll_date) = MONTH(%s) 
				AND YEAR(payroll_date) = YEAR(%s) 
				AND employee = %s 
				AND salary_component = %s 
				AND docstatus = 1
		"""
		exist_additional_salary = frappe.db.sql(query, (self.payroll_month, self.payroll_month, self.employee, self.addition_type), as_dict=True)
		if exist_additional_salary:
			addtional_salary = frappe.get_doc('Additional Salary', exist_additional_salary[0]['name'])
			addtional_salary.amount += flt(self.amount)
			if self.notes:
				addtional_salary.reason += "/ "+ self.notes
			# addtional_salary.employee_benefit += "," + self.name
			addtional_salary.save('update')
		else:
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
		query = """
			SELECT name 
			FROM `tabAdditional Salary` 
			WHERE 
				MONTH(payroll_date) = MONTH(%s) 
				AND YEAR(payroll_date) = YEAR(%s) 
				AND employee = %s 
				AND salary_component = %s 
				AND docstatus = 1
		"""
		exist_additional_salary = frappe.db.sql(query, (self.payroll_month, self.payroll_month, self.employee, self.addition_type), as_dict=True)
		if exist_additional_salary:
			for ea in exist_additional_salary:
				doc = frappe.get_doc("Additional Salary", ea["name"])
				doc.amount -= flt(self.amount)
				doc.save()
				if doc.amount <= 0:
					doc.cancel()
