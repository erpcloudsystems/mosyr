# Copyright (c) 2022, AnvilERP and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.model.naming import make_autoname
from frappe.utils import cint, flt

from erpnext.payroll.doctype.salary_structure_assignment.salary_structure_assignment import get_assigned_salary_structure

class PayrollRegisterTool(Document):
	
	@frappe.whitelist()
	def fetch_employees(self, company, department=None, branch=None, designation=None):
		conds = [" status='Active' "]
		if company and len(f"{company}") > 0:
			conds.append(" company='{}' ".format(company))
		else:
			return []
		if department and len(f"{department}") > 0:
			conds.append(" department='{}' ".format(department))
		if branch and len(f"{branch}") > 0:
			conds.append(" branch='{}' ".format(branch))
		if designation and len(f"{designation}") > 0:
			conds.append(" designation='{}' ".format(designation))
		if len(conds) > 0:
			conds = " AND ".join(conds)
			conds = "WHERE {}".format(conds)
		else:
			return []
		
		return frappe.db.sql("SELECT name, employee_name FROM `tabEmployee` {}".format(conds), as_dict=True)
	
	@frappe.whitelist()
	def prepare_salary_structures(self, company, from_date=frappe.utils.nowdate(), currency=None, frequency="Monthly", earnings=[], deductions=[], 
                                        based_on_timesheet=0, ts_component=None, hour_rate=0, encashment_per_day=0, max_benefits=0,
                                        base=0, employees=[],  variables=0,):
		
		company_doc = frappe.db.exists("Company", company)
		if not company_doc:
			frappe.throw(_("Company {} dose not exists".format(company)))
			return
		
		company_doc = frappe.get_doc("Company", company_doc)
		if not currency:
			currency = company_doc.default_currency
		else:
			currency_doc = frappe.db.exists("Currency", currency)
			if not currency_doc:
				currency = company_doc.default_currency
			else:
				currency = currency_doc
		ts_component_doc = frappe.db.exists("Salary Component", ts_component)
		if not ts_component_doc:
			ts_component = ''
			based_on_timesheet = 0
		else:
			ts_component = ts_component_doc
			based_on_timesheet = 0

		valid_employees = []
		not_active_emps = []
		has_salary_structure = []
		different_comp = []

		# Check Employee Data
		for employee in employees:
			employee_doc = frappe.db.exists("Employee", employee.get('employee_name', None))
			if not employee_doc:
				not_active_emps.append(employee.get('employee_name', None))
				continue
			
			employee_doc = frappe.get_doc("Employee", employee_doc)
			if employee_doc.status != "Active":
				not_active_emps.append(employee_doc.name)
				continue

			if employee_doc.company != company:
				different_comp.append(employee_doc.name)
				continue

			salary_structure = get_assigned_salary_structure(employee_doc.name, from_date)
			if salary_structure:
				has_salary_structure.append(employee_doc.name)
				continue
			
			valid_employees.append(employee_doc.name)
		
		if len(valid_employees) > 0:
			ss_name = "PRT-{}-.#####".format(from_date)
			ss_name = make_autoname(ss_name)
			ss_doc = frappe.new_doc("Salary Structure")
			ss_doc.update({
				"__newname": ss_name,
				"is_active": "Yes",
				"payroll_frequency": frequency,
				"company": company_doc.name,
				"currency": currency,
				"salary_slip_based_on_timesheet": cint(based_on_timesheet),
				"salary_component": ts_component,
				"hour_rate": flt(hour_rate),
				"leave_encashment_amount_per_day": flt(encashment_per_day),
				"max_benefits": flt(max_benefits),
			})
			ss_doc.__newname = ss_name
			for salary_component in earnings:
				ss_doc.append("earnings", salary_component)
			for salary_component in deductions:
				ss_doc.append("deductions", salary_component)
			ss_doc.save()
			ss_doc.submit()
			for emp in valid_employees:
				sa = frappe.new_doc("Salary Structure Assignment")
				sa.employee = emp
				sa.salary_structure = ss_doc.name
				sa.from_date = from_date
				sa.base = flt(base)
				sa.variable = flt(variables)
				sa.insert()
				sa.submit()
		msg = _("<h5>Salary Structure Prepared for {} Employees</h5>".format(len(valid_employees)))
		ss_status = True
		msg_str = []
		if len(has_salary_structure) > 0:
			ss_status = False
			for hss in has_salary_structure:
				msg_str.append("<li>{}</li>".format(hss))
		if len(msg_str) > 0:
			msg_str = "".join(msg_str)
			msg_str = "<p>{}</p><ul>{}</ul>".format(_("Employees Assigned to salary structure"), msg_str)
		else:
			msg_str = ""
		msg += msg_str

		msg_str = []
		if len(different_comp) > 0:
			ss_status = False
			for hss in different_comp:
				msg_str.append("<li>{}</li>".format(hss))
		if len(msg_str) > 0:
			msg_str = "".join(msg_str)
			msg_str = "<p>{}</p><ul>{}</ul>".format(_("Employees belong to different companies"), msg_str)
		else:
			msg_str = ""
		msg += msg_str

		msg_str = []
		if len(not_active_emps) > 0:
			ss_status = False
			for hss in not_active_emps:
				msg_str.append("<li>{}</li>".format(hss))
		if len(msg_str) > 0:
			msg_str = "".join(msg_str)
			msg_str = "<p>{}</p><ul>{}</ul>".format(_("In active / not found employees"), msg_str)
		else:
			msg_str = ""
		msg += msg_str
		if len(not_active_emps) > 0 or len(different_comp) > 0 or len(has_salary_structure) > 0:
			pass

		frappe.msgprint(msg, _("Salary Structure Status"))
		return { "status": ss_status }
	
	def get_employees_payroll_details(self, payroll):
		earnings = [sc.name for sc in frappe.db.sql("select name from `tabSalary Component` where type='Earning'", as_dict=True)]
		deductions = [sc.name for sc in frappe.db.sql("select name from `tabSalary Component` where type='Deduction'", as_dict=True)]
		
		zeros_earnings =   [True for i in range(len(earnings))]
		zeros_deductions = [True for i in range(len(deductions))]
		
		data = []
		
		payroll = frappe.get_doc("Payroll Entry", payroll)
		
		for sr, employee in enumerate(payroll.employees, 1):
			result_dict = frappe._dict()
			result_dict.update({
				"sr": sr,
				"employee": employee.employee,
				"employee_name": employee.employee_name,
				"department": employee.department,
				"designation": employee.designation,
			})
			slip = frappe.get_doc("Salary Slip", {
				"payroll_entry": payroll.name, "employee": employee.employee
			})
			emp_earnings = [0 for i in range(len(earnings))]
			emp_deductions = [0 for i in range(len(deductions))]
			result_dict.update({
				"sr": sr,
				"employee": employee.employee,
				"employee_name": employee.employee_name,
				"department": employee.department,
				"designation": employee.designation,
				"net_pay": 0
			})
			if slip:
				for e in slip.earnings:
					try:
						idx = earnings.index(e.salary_component)
						amount = flt(e.amount)
						if amount > 0:
							zeros_earnings[idx] = False
						emp_earnings[idx] = amount
					except: pass
				for d in slip.deductions:
					try:
						idx = deductions.index(d.salary_component)
						amount = flt(d.amount)
						if amount > 0:
							zeros_deductions[idx] = False
						emp_deductions[idx] = amount
					except: pass
				result_dict.update({
					"net_pay": flt(slip.net_pay)
				})
			result_dict.update({
				"earnings": emp_earnings,
				"deductions": emp_deductions,
			})
			data.append(result_dict)
		return self.get_clean_data(zeros_earnings, zeros_deductions, earnings, deductions, data)

	def get_clean_data(self, ezeros, dzeros, erns, dedcs, data):
		earnings = []
		deductions = []
		for idx, e in enumerate(ezeros):
			if not e: earnings.append(erns[idx])
		for idx, d in enumerate(dzeros): 
			if not d: deductions.append(dedcs[idx])
		
		final_data = []
		for d in data:
			row = [
				d.get("sr", '-'), d.get("employee", ''), d.get("employee_name", ''),
				d.get("department", ''), d.get("designation", '')
			]
			erns = d.get("earnings", [])
			for idx, e in enumerate(ezeros):
				if not e: row.append(erns[idx])
			dedcs = d.get("deductions", [])
			for idx, de in enumerate(dzeros): 
				if not de: row.append(dedcs[idx])
			row.append(d.get("net_pay", 0))
			final_data.append(row)
		return {
			"earnings": earnings,
			"len_earnings": len(earnings),
			"deductions": deductions,
			"len_deductions": len(deductions),
			"data": final_data
		}