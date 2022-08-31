# Copyright (c) 2022, AnvilERP and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import nowdate, flt, cint, get_date_str, getdate, today
from mosyr.install import create_salary_components
from erpnext.payroll.doctype.payroll_entry.payroll_entry import get_start_end_dates

from mosyr.tasks import update_status_for_contracts
class EmployeeContract(Document):
	def validate(self):
		if self.contract_start_date >= self.contract_end_date:
			frappe.throw(_("The end date of the contract must be after the start date"))
			return
		
		# previous_contracts = frappe.get_list('Employee Contract', 
		# 									 filters={
		# 										'employee': self.employee, 
		# 										'docstatus' :1, 
		# 										'status': 'Approved', 
		# 										'contract_status': 'Valid', 
		# 										'contract_start_date': ["<=", self.contract_end_date]})
		
		previous_contracts = frappe.db.sql("""
						SELECT name, contract_start_date, contract_end_date
						FROM `tabEmployee Contract`
						WHERE docstatus=1 AND status='Approved' AND contract_status='Valid'
						AND employee='{0}' AND (contract_start_date BETWEEN '{1}' AND '{2}' OR contract_end_date BETWEEN '{1}' AND '{2}') """
				.format(self.employee, get_date_str(self.contract_start_date), get_date_str(self.contract_end_date)), as_dict=1)

		if len(previous_contracts) > 0:
			frappe.throw(_("Employee {} has Valid contract within {} and {}".format(self.employee_name, self.contract_start_date, self.contract_end_date)))
			return
		
		if self.hiring_start_date < self.contract_start_date or self.hiring_start_date > self.contract_end_date:
			frappe.msgprint(_("Hiring Date in contract {} is out of range {} and {}".format(self.name, self.contract_start_date, self.contract_end_date)))

	def on_submit(self):
		if getdate(today()) > getdate(self.contract_end_date):
			update_status_for_contracts()
	
	@frappe.whitelist()
	def create_employee_salary_structure(self):
		if(self.docstatus != 1): return
		ss_name = "{}-{}-{}".format(self.name, self.name, nowdate())
		ss_doc = frappe.db.exists("Salary Structure", ss_name)
		if ss_doc:
			frappe.throw(_("Employee has Salary Structure {}").format(ss_name))
			return
		self.validate_dates()
		# Make sure that all components are in the system
		create_salary_components()
		employee = frappe.get_doc("Employee", self.employee)
		
		employee.from_api = 0
		employee.valid_data = 1
		employee.status = "Active"
		if not employee.date_of_joining: employee.date_of_joining = self.hiring_start_date
		if not employee.date_of_birth: get_date_str(getdate("01-01-2000"))
		employee.save()
		frappe.db.commit()
		company = frappe.get_doc('Company', employee.company)
		# bsc = frappe.get_doc('Salary Component', 'Basic')
		
		salary_components = [
			{
				"salary_component": "Basic",
				"amount_based_on_formula": 1,
				"formula": "base * 1"
			},
			{
				"salary_component": "Variable",
				"amount_based_on_formula": 1,
				"formula": "variable * 1"
			}
		]

		is_sauid = False

		# Saudi Employee
		e_insurance_formula = "base * pension_on_employee / 100"
		c_insurance_formula = "base * pension_on_company / 100"

		# Non Saudi Employee
		e_risk_formula = "base * risk_on_employee / 100"
		c_risk_formula = "base * risk_on_company / 100"

		# Allowance Housing component
		if self.allowance_housing == "Cash":
			if cint(employee.include_housing) == 0:
				args = {
					"salary_component": "Allowance Housing"
				}
				if self.allowance_housing_schedule == "Monthly":
					if self.house_amount_type == "Percentage":
						args.update({
							'amount_based_on_formula': 1,
							'formula': "base * {}".format(flt(self.allowance_housing_value/100, 2))
						})

						if employee.social_insurance_type == "Saudi":
							e_insurance_formula = "base + ( base * {} ) )  * pension_on_employee / 100".format(flt(self.allowance_housing_value/100, 2))
							c_insurance_formula = "base + ( base * {} ) )  * pension_on_company / 100".format(flt(self.allowance_housing_value/100, 2))
						else:
							e_risk_formula = "base + ( base * {} ) )  * risk_on_employee / 100".format(flt(self.allowance_housing_value/100, 2))
							c_risk_formula = "base + ( base * {} ) )  * risk_on_company / 100".format(flt(self.allowance_housing_value/100, 2))
					else:
						args.update({
							'amount_based_on_formula': 0,
							"amount": self.allowance_housing_value
						})

						if employee.social_insurance_type == "Saudi":
							e_insurance_formula = "( base + {} )  * pension_on_employee / 100".format(flt(self.allowance_housing_value, 2))
							c_insurance_formula = "( base + {} )  * pension_on_company / 100".format(flt(self.allowance_housing_value, 2))
						else:
							e_risk_formula = "( base + {} )  * risk_on_employee / 100".format(flt(self.allowance_housing_value, 2))
							c_risk_formula = "( base + {} ) * risk_on_company / 100".format(flt(self.allowance_housing_value, 2))
								
				salary_components.append(args)

		# Allowance Transportations component
		if self.allowance_trans == "Cash":
			args = {
				"salary_component": "Allowance Trans"
			}
			if self.allowance_period == "Monthly":
				if self.allowance_trans_amount_type == "Percentage" and flt(self.allowance_trans_value) != 0:
					args.update({
						'amount_based_on_formula': 1,
						'formula': "base * {}".format(flt(self.allowance_trans_value/100, 2))
					})
				else:
					args.update({
						'amount_based_on_formula': 0,
						"amount": self.allowance_trans_value
					})
			salary_components.append(args)
		
		# Allowance Phone component
		if self.allowance_phone == "Cash":
			args = {
				"salary_component": "Allowance Phone"
			}
			if self.allowance_phone_schedule == "Monthly":
				if self.allowance_phone_amount_type == "Percentage" and flt(self.allowance_phone_value) != 0:
					args.update({
						'amount_based_on_formula': 1,
						'formula': "base * {}".format(flt(self.allowance_phone_value/100, 2))
					})
				else:
					args.update({
						'amount_based_on_formula': 0,
						"amount": self.allowance_phone_value
					})
			salary_components.append(args)
		
		# Allowance Nature of Work component
		if self.allowance_worknatural == "Cash":
			args = {
				"salary_component": "Allowance Worknatural"
			}
			if self.allowance_worknatural_schedule == "Monthly":
				if self.allowance_worknatural_amount_type == "Percentage" and flt(self.allowance_worknatural_value) != 0:
					args.update({
						'amount_based_on_formula': 1,
						'formula': "base * {}".format(flt(self.allowance_worknatural_value/100, 2))
					})
				else:
					args.update({
						'amount_based_on_formula': 0,
						"amount": self.allowance_worknatural_value
					})
			salary_components.append(args)
		
		# Allowance Living component
		if self.allowance_living == "Cash":
			args = {
				"salary_component": "Allowance Living"
			}
			if self.allowance_living_schedule == "Monthly":
				if self.field_allowance_feed_amount_typ == "Percentage" and flt(self.allowance_living_value) != 0:
					args.update({
						'amount_based_on_formula': 1,
						'formula': "base * {}".format(flt(self.allowance_living_value/100, 2))
					})
				else:
					args.update({
						'amount_based_on_formula': 0,
						"amount": self.allowance_living_value
					})
			salary_components.append(args)
		
		# Allowance Other component
		if self.allowance_other == "Cash":
			args = {
				"salary_component": "Allowance Other"
			}
			if self.allowance_other_schedule == "Monthly":
				if self.allowance_other_amount_type == "Percentage" and flt(self.allowance_other_value) != 0:
					args.update({
						'amount_based_on_formula': 1,
						'formula': "base * {}".format(self.allowance_other_value)
					})
				else:
					args.update({
						'amount_based_on_formula': 0,
						"amount": self.allowance_other_value
					})
			salary_components.append(args)
		
		ss_doc = frappe.new_doc("Salary Structure")
		ss_doc.update({
			"__newname": "{}-{}-{}".format(self.name, employee.name, nowdate()),
			"is_active": "Yes",
			"payroll_frequency": "Monthly",
			"company": company.name,
			"currency": company.default_currency
		})

		for salary_component in salary_components:
			ss_doc.append("earnings", salary_component)

		ss_doc.append("deductions", { "salary_component": "Other Deductions" })
		if employee.social_insurance_type == "Saudi":
			ss_doc.append("deductions", 
							{
								"salary_component": "Employee Pension Insurance",
								"amount_based_on_formula": 1,
								"formula": e_insurance_formula
							})
			ss_doc.append("deductions", 
							{
								"salary_component": "Company Pension Insurance",
								"amount_based_on_formula": 1,
								"formula": c_insurance_formula,
								"do_not_include_in_total": 1,
								"statistical_component": 1
							})

		else:
			ss_doc.append("deductions", 
							{
								"salary_component": "Risk On Employee",
								"amount_based_on_formula": 1,
								"formula": e_risk_formula
							})
			ss_doc.append("deductions", 
							{
								"salary_component": "Risk On Company",
								"amount_based_on_formula": 1,
								"formula": c_risk_formula,
								"do_not_include_in_total": 1,
								"statistical_component": 1
							})

		ss_doc.save()
		ss_doc.submit()

		ssa_doc = frappe.new_doc("Salary Structure Assignment")
		ssa_doc.employee = self.employee
		ssa_doc.salary_structure = ss_doc.name
		dates = get_start_end_dates("Monthly", self.contract_start_date)
		ssa_doc.from_date = dates.start_date
		ssa_doc.base = self.basic_salary
		ssa_doc.save()
		ssa_doc.submit()
		return {
			"ss": ss_doc.name,
			"ssa": ssa_doc.name
		}

	def validate_dates(self):
		class DuplicateAssignment(frappe.ValidationError): pass

		if self.contract_start_date:
			if frappe.db.exists(
				"Salary Structure Assignment",
				{"employee": self.employee, "from_date": self.contract_start_date, "docstatus": 1},
			):
				frappe.throw(_("Salary Structure Assignment for Employee already exists"), DuplicateAssignment)
