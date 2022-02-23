# Copyright (c) 2022, AnvilERP and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import cint, flt
import erpnext

class EmployeeContract(Document):
	def validate(self):
		if self.contract_start_date > self.contract_end_date:
			frappe.throw(_("The end date of the contract must be after the start date"))
			return
		
		previous_contracts = frappe.get_list('Employee Contract', filters={'employee': self.employee, 'docstatus' :1, 'contract_status': 'Valid', 'contract_start_date': ["<=", self.contract_end_date]})
		if len(previous_contracts) > 0:
			frappe.throw(_("Employee {} has Valid contract within {} and {}".format(self.employee_name, self.contract_start_date, self.contract_end_date)))
			return
		
		if self.hiring_start_date < self.contract_start_date or self.hiring_start_date > self.contract_end_date:
			if self.key:
				frappe.msgprint(_("Hiring Date in contract {} is out of range {} and {}".format(self.key, self.contract_start_date, self.contract_end_date)))
			elif self.name:
				frappe.msgprint(_("Hiring Date in contract {} is out of range {} and {}".format(self.name, self.contract_start_date, self.contract_end_date)))
			else:
				frappe.msgprint(_("Hiring Date is out of range {} and {}".format(self.contract_start_date, self.contract_end_date)))

	
	@frappe.whitelist()
	def apply_in_system(self):
		employee = frappe.get_doc('Employee', self.employee)
		lookup_value = {
			"active" : "Active",
			"inactive" : "Inactive",
			"leave" : "Left",
			"sponsorshiptrans" : "Suspended",
			"finalexit" : "Left"
		}
		if self.hiring_start_date and cint(employee.from_api) == 1:
			# Check  Employee Data
			
			employee.date_of_joining = self.hiring_start_date
			employee.status = 'Active'
			employee.save()
			frappe.db.commit()

		ss = self.create_salary_structure(employee.first_name)
		self.create_salary_structure_assignment(ss)
		self.db_set('status', 'Applied In System', update_modified=False)
		employee.status = lookup_value.get(employee.api_employee_status, 'Inactive')
		employee.valid_data = 1
		employee.from_api = 0
		employee.save()
		frappe.db.commit()
		return 'Applied In System'
	
	def create_salary_structure_assignment(self, ss):
		ssa = frappe.new_doc('Salary Structure Assignment')
		ssa.employee = self.employee
		ssa.company = ss.company
		ssa.salary_structure = ss.name
		ssa.from_date = self.contract_start_date
		ssa.base = flt(self.allowance_trans_value)
		ssa.save()
		ssa.submit()
		frappe.db.commit()
		
	
	def create_salary_structure(self, employee):
		
		earnings = [{
			'salary_component' : 'Basic',
			'abbr': 'B',
			'amount_based_on_formula': 1,
			'formula': f'base'
		}]
		
		if self.over_time_included == 'Yes':
			earnings.append({
				'salary_component' : 'Overtime',
				'abbr': 'OT'
			})
		
		if self.allowance_trans != 'None' and self.allowance_period == 'Monthly':
			comp = {
				'salary_component' : 'Allowance Trans',
				'abbr': 'AT',
			}
			if self.allowance_trans_amount_type == 'Fixed':
				comp.update({
					'amount': flt(self.allowance_trans_value)
				})
			else:
				if flt(self.allowance_trans_value) != 0:
					comp.update({
						'amount_based_on_formula': 1,
						'formula': f'B * {flt(self.allowance_trans_value)}'
					})
			earnings.append(comp)
		
		if self.allowance_housing != 'None' and self.allowance_housing_schedule == 'Monthly':
			comp = {
				'salary_component' : 'Allowance Housing',
				'abbr': 'AH',
			}
			if self.house_amount_type == 'Fixed':
				comp.update({
					'amount': flt(self.allowance_housing_value)
				})
			else:
				if flt(self.allowance_housing_value) != 0:
					comp.update({
						'amount_based_on_formula': 1,
						'formula': f'B * {flt(self.allowance_housing_value)}'
					})
			earnings.append(comp)
		
		if self.allowance_phone != 'None' and self.allowance_phone_schedule == 'Monthly':
			comp = {
				'salary_component' : 'Allowance Phone',
				'abbr': 'AP',
			}
			if self.allowance_phone_amount_type == 'Fixed':
				comp.update({
					'amount': flt(self.allowance_phone_value)
				})
			else:
				if flt(self.allowance_phone_value) != 0:
					comp.update({
						'amount_based_on_formula': 1,
						'formula': f'B * {flt(self.allowance_phone_value)}'
					})
			earnings.append(comp)
		
		if self.allowance_worknatural != 'None' and self.allowance_worknatural_schedule == 'Monthly':
			comp = {
				'salary_component' : 'Allowance Worknatural',
				'abbr': 'AW',
			}
			if self.allowance_worknatural_amount_type == 'Fixed':
				comp.update({
					'amount': flt(self.allowance_worknatural_value)
				})
			else:
				if flt(self.allowance_worknatural_value) != 0:
					comp.update({
						'amount_based_on_formula': 1,
						'formula': f'B * {flt(self.allowance_worknatural_value)}'
					})
			earnings.append(comp)
			
		if self.allowance_other != 'None' and self.allowance_other_schedule == 'Monthly':
			comp = {
				'salary_component' : 'Allowance Other',
				'abbr': 'AO',
			}
			if self.allowance_other_amount_type == 'Fixed':
				comp.update({
					'amount': flt(self.allowance_other_value)
				})
			else:
				if flt(self.allowance_other_value) != 0:
					comp.update({
						'amount_based_on_formula': 1,
						'formula': f'B * {flt(self.allowance_other_value)}'
					})
			earnings.append(comp)
		
		if self.allowance_living != 'None' and self.allowance_living_schedule == 'Monthly':
			comp = {
				'salary_component' : 'Allowance Living',
				'abbr': 'AL',
			}
			if self.field_allowance_feed_amount_typ == 'Fixed':
				comp.update({
					'amount': flt(self.allowance_living_value)
				})
			else:
				if flt(self.allowance_living_value) != 0:
					comp.update({
						'amount_based_on_formula': 1,
						'formula': f'base * {flt(self.allowance_living_value)}'
					})
			earnings.append(comp)
		
		details = {
			"doctype": "Salary Structure",
			"name":  f'{employee}',
			"company": erpnext.get_default_company(),
			# "earnings": make_earning_salary_component(setup=True,  test_tax=test_tax, company_list=["_Test Company"]),
			# "deductions": make_deduction_salary_component(setup=True, test_tax=test_tax, company_list=["_Test Company"]),
			"payroll_frequency": 'Monthly',
			"currency": erpnext.get_default_currency()
		}
		
		salary_structure_doc = frappe.get_doc(details)
		for er in earnings:
			salary_structure_doc.append('earnings', er)
		
		salary_structure_doc.insert()
		salary_structure_doc.submit()
		# frappe.db.commit()
		return salary_structure_doc

