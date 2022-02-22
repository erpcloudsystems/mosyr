# Copyright (c) 2022, AnvilERP and contributors
# For license information, please see license.txt

import datetime

import frappe
from frappe import _
from frappe.utils import flt

from frappe.model.document import Document

class EmployeeBenefit(Document):

	def validate(self):
		try:
			datetime.datetime.strptime(self.payroll_month, '%Y-%m')
		except ValueError:
			frappe.throw(_("Incorrect data format, should be YYYY-MM"))
			return
	
	@frappe.whitelist()
	def apply_in_system(self):
		# adds = frappe.get_list('Additional Salary', filters={'employee_deduction': self.name})
		# if len(adds) > 0:
		# 	frappe.throw(_('{} Applied in the System see <a href="/app/additional-salary/EB-2022-02-01">Additional Salary<a/>'.format(self.name, adds[0])))

		eadd = frappe.new_doc('Additional Salary')
		eadd.employee = self.employee
		eadd.amount = flt(self.amount)
		eadd.salary_component = self.addition_type
		eadd.payroll_date = datetime.datetime.strptime(f'{self.payroll_month}-01', '%Y-%m-%d')
		eadd.reason = self.notes
		eadd.employee_benefit = self.name
		eadd.save()
		eadd.submit()
		self.db_set('status', 'Applied In System', update_modified=False)
		frappe.db.commit()
		return 'Applied In System'
