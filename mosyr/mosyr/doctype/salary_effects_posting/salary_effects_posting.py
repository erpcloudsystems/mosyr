from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import cint, cstr, date_diff, flt, formatdate, getdate, get_link_to_form, get_fullname, add_days, nowdate, get_datetime, time_diff, time_diff_in_hours, time_diff_in_seconds
# from erpnext.hr.utils import set_employee_name, get_leave_period, share_doc_with_approver
# from erpnext.hr.doctype.leave_block_list.leave_block_list import get_applicable_block_dates
# from erpnext.hr.doctype.employee.employee import get_holiday_list_for_employee
# from erpnext.buying.doctype.supplier_scorecard.supplier_scorecard import daterange
# from erpnext.hr.doctype.leave_ledger_entry.leave_ledger_entry import create_leave_ledger_entry
from frappe.model.document import Document

from datetime import timedelta, datetime

class SalaryEffectsPosting(Document):

	def on_submit(self):
		self.calculate_salary_effects()
	def before_cancel(self):
		self.unlink_extra_salary()
	def calculate_salary_effects(self):
		all_active_employees = frappe.db.sql(""" select name as name from tabEmployee where status ='Active'  """,as_dict=1)
		for emp in all_active_employees:
			emp_name = emp.name
			start_date = self.start_date
			end_date = self.end_date
			salary_comp = frappe.db.sql(""" select distinct salary_component as salary_component, company from `tabExtra Salary` where docstatus=1 and employee= '{emp_name}' and payroll_date between '{start_date}' and '{end_date}' """.format(
					emp_name=emp_name, start_date=start_date, end_date=end_date), as_dict=1)
			for sal_co in salary_comp:
				soso = sal_co.salary_component
				company = sal_co.company
				amounte = 0
				amountw = frappe.db.sql(
					""" select ifnull(sum(amount),0) as amount from `tabExtra Salary` where docstatus=1 and `tabExtra Salary`.posted = 0 and payroll_date between '{start_date}' and '{end_date}' and salary_component = '{soso}' and employee= '{emp_name}' """.format(
						emp_name=emp_name, start_date=start_date, end_date=end_date, soso=soso), as_dict=1)
				for v in amountw:
					amounte += v.amount
				exist_addtional_salary = frappe.db.sql("""SELECT name from `tabAdditional Salary` where payroll_date = '{payroll_date}' and employee= '{emp_name}' and salary_component='{soso}' and docstatus= 1  """.format(payroll_date=self.end_date, emp_name= emp_name, soso=soso), as_dict = 1)
				if exist_addtional_salary:
					addtional_salary = frappe.get_doc('Additional Salary', exist_addtional_salary[0]['name'])
					addtional_salary.amount += amounte
					addtional_salary.salary_effects_posting = addtional_salary
					addtional_salary.save('update')
				else:
					new_doc = frappe.get_doc(dict(
						doctype='Additional Salary',
						employee=emp_name,
						company=company,
						salary_component=soso,
						currency='EGP',
						amount=amounte,
						payroll_date=self.end_date,
						salary_effects_posting=self.name,
						overwrite_salary_structure_amount=1
					))
					new_doc.insert()
					new_doc.submit()
				mark = frappe.db.sql(
					""" select name as name from `tabExtra Salary` where docstatus=1 and `tabExtra Salary`.posted = 0 and payroll_date between '{start_date}' and '{end_date}' and salary_component = '{soso}' and employee= '{emp_name}' """.format(
						emp_name=emp_name, start_date=start_date, end_date=end_date, soso=soso), as_dict=1)
				for m in mark:
					frappe.db.set_value('Extra Salary', m.name, 'posted', '1', update_modified=False)
					frappe.db.set_value('Extra Salary', m.name, 'ref_doctype', 'Salary Effects Posting', update_modified=False)
					frappe.db.set_value('Extra Salary', m.name, 'ref_docname', self.name, update_modified=False)

	def unlink_extra_salary(self):
		extras = frappe.db.sql(""" select name as name from `tabExtra Salary` where ref_docname = '{name}'""".format(name=self.name), as_dict=1)
		for x in extras:
			frappe.db.set_value('Extra Salary', x.name, 'posted', '0', update_modified=False)
			frappe.db.set_value('Extra Salary', x.name, 'ref_doctype', '', update_modified=False)
			frappe.db.set_value('Extra Salary', x.name, 'ref_docname', '', update_modified=False)
			frappe.db.commit()
	pass
