# Copyright (c) 2022, AnvilERP and contributors
# For license information, please see license.txt

# import frappe
import frappe
from frappe.model.document import Document
from frappe.utils import cint

class EmployeeContract(Document): 	
	def validate(self):
		if self.from_api:
			if self.nid:
				emp_name = frappe.get_value("Employee", {'nid':self.nid}) or False
				if emp_name: self.employee = emp_name
	
	def on_submit(self):
		if self.from_api:
			employee = frappe.get_doc('Employee', self.employee)
			if self.hiring_start_date_g and cint(employee.from_api) == 1:
				lookup_value = {
					"active" : "Active",
					"inactive" : "Inactive",
					"leave" : "Left",
					"sponsorshiptrans" : "Suspended",
					"finalexit" : "Left"
				}
				employee.date_of_joining = self.hiring_start_date_g
				employee.valid_data = 1
				employee.from_api = 0
				employee.status = lookup_value[employee.moyser_employee_status]

				trans_amount_type = self.trans_amount_type
				trans_amount_value = self.trans_amount_value
				trans_abbr = 'AT'

				house_amount_type = self.house_amount_type
				house_amount_value = self.house_amount_value
				house_abbr = 'AH'

				phone_amount_type = self.phone_amount_type
				phone_amount_value = self.phone_amount_value
				phone_abbr = 'AP'

				natureow_amount_type = self.natureow_amount_type
				natureow_amount_value = self.natureow_amount_value
				natur_abbr = 'AW'

				feed_amount_type = self.feed_amount_type
				feed_amount_value = self.feed_amount_value
				feed_abbr = 'AL'

				other_amount_type= self.other_amount_type
				other_amount_value = self.other_amount_value
				other_abbr = 'AO'

				components = []
				if cint(trans_amount_value) != 0:
					components.append({'component': 'Allowance Trans','abbr':trans_abbr, 'type':trans_amount_type, 'value': self.trans_amount_value})
				if cint(house_amount_value) != 0:
					components.append({'component': 'Allowance Housing','abbr':house_abbr, 'type':house_amount_type, 'value': self.house_amount_value})
				if cint(phone_amount_value) != 0:
					components.append({'component': 'Allowance Phone','abbr':phone_abbr, 'type':phone_amount_type, 'value': self.phone_amount_value})
				if cint(natureow_amount_value) != 0:
					components.append({'component': 'Allowance Worknatural','abbr':natur_abbr, 'type':natureow_amount_type, 'value': self.natureow_amount_value})
				if cint(feed_amount_value) != 0:
					components.append({'component': 'Allowance Living','abbr':feed_abbr, 'type':feed_amount_type, 'value': self.feed_amount_value})
				if cint(other_amount_value) != 0:
					components.append({'component': 'Allowance Other','abbr':other_abbr, 'type':other_amount_type, 'value': self.other_amount_value})


				salary_structure_doc = frappe.new_doc('Salary Structure')
				company = frappe.defaults.get_global_default('company')
				company = frappe.get_doc('Company', company)
				salary_structure_doc.update({
					'__newname': f"{employee.get('name')} - {employee.get('first_name')}",
					'is_active': 'Yes',
					'payroll_frequency': 'Monthly',
					'company': company.name,
					'currency': company.default_currency
				})
				for component in components:
					if component.get('type') == 'Fixed':
						salary_structure_doc.append('earnings', {
							'salary_component': component.get('component'),
							'abbr': component.get('abbr'),
							'amount': component.get('value')
												})
					elif component.get('type') == 'Percentage':
						salary_structure_doc.append('earnings', {
							'salary_component': component.get('component'),
							'abbr': component.get('abbr'),
							'amount_based_on_formula': 1,
							'formula': f"basic * {component.get('value')}"
												})
					salary_structure_doc.save()
				salary_structure_doc.submit()
				self.set_indicator()
				self.set_status()
				employee.save()
				frappe.db.commit()

	# def set_indicator(self):
	# 	if self.contract_status == "Valid":
	# 		self.indicator_color = "green"
	# 	elif self.contract_status == "Not Valid":
	# 		self.indicator_color = "gray"
	# 	else:
	# 		self.contract_status = "Pinding"
	# 		self.indicator_color = "Orange"
	
	# def set_status(self, update=False, status=None, update_modified=True):
	# 	if self.contract_status == "Valid":
	# 		self.docstatus = 1
	# 		self.status = 'Valid'
	# 	elif self.contract_status == "Not Valid":
	# 		self.docstatus = 2
	# 		self.status = 'Not Valid'
	# 	return
