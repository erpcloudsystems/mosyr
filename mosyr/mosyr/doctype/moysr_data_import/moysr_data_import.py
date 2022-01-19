# Copyright (c) 2022, AnvilERP and contributors
# For license information, please see license.txt

from cgitb import lookup
from operator import le
from signal import pthread_kill
import frappe
import requests
from frappe.model.document import Document
from datetime import datetime
from frappe import _


class MoysrDataImport(Document):
	@frappe.whitelist()
	def get_company_id(self):
		return frappe.conf.company_id or False


	@frappe.whitelist()
	def import_branches(self,company_id):
		errors=0
		sucess=0
		exists=0
		data=[]
		
		if not company_id:
			company_id = self.get_company_id()
		
		if not company_id:
			msg = _(f"Set Company id please")
			frappe.throw(f"{msg}.!")
			
		url = f'https://www.mosyr.io/ar/api/branches_api.json?list=branches_{company_id}'
		res = False
		try:
			res = requests.get(url)
			res.raise_for_status()

			if res.ok and res.status_code == 200:
				data = res.json()
		except Exception as e:
			status_code = ''
			errors += 1
			if res:
				status_code = res.status_code
				status_code = f"error code {status_code}"
			err = frappe.log_error(f"{e}", f'Import branches Faield. {status_code}!')
			err_msg = _('An Error occurred while Import branches  see')
			err_name_html = f' <a href="/app/error-log/{err.name}"><b>{err.name}</b></a>'
			frappe.msgprint(err_msg + err_name_html)
			data = []
		
		for d in data:
			d = self.get_clean_data(d)
			bn = d.get('branch_name','')
			if bn != '' :
				if not frappe.db.exists("Branch",bn):
					self.check_link_data('Branch',bn,'branch')
					sucess += 1
				else:
					exists += 1
		frappe.db.commit()

		msg = frappe.msgprint(f"""
		<table class="table table-bordered">
		<tbody>
			<tr>
			<th scope="row"><span class="indicator green"></span>Sucess</th>
			<td>{sucess}</td>
			</tr>
			<tr>
			<th scope="row"><span class="indicator orange"></span>Exists</th>
			<td>{exists}</td>
			</tr>
			<tr>
			<th scope="row"><span class="indicator red"></span>Errors</th>
			<td>{errors}</td>
			</tr>
		</tbody>
		</table>
		""",title=f'{len(data)} Branches Imported',indicator='Cs')


	@frappe.whitelist()
	def import_employees(self,company_id):
		errors=0
		error_msgs=''
		sucess=0
		exists=0
		data=[]
		values_lookup={
			'finalexit': 'Left',
			'leave': 'Inactive',
			'sponsorshiptrans': 'Suspended',
			'active': 'Active',
			'inactive': 'Inactive'
		}
		
		if not company_id:
			company_id = self.get_company_id()
		
		if not company_id:
			msg = _(f"Set Company id please")
			frappe.throw(f"{msg}.!")
			
		url = f'https://www.mosyr.io/en/api/migration-employees.json?company_id={company_id}'
		res = False
		try:
			res = requests.get(url)
			res.raise_for_status()

			if res.ok and res.status_code == 200:
				data = res.json()
		except Exception as e:
			status_code = ''
			errors += 1
			if res:
				status_code = res.status_code
				status_code = f"error code {status_code}"
			err = frappe.log_error(f"{e}", f'Import Employess Faield. {status_code}!')
			err_msg = _('An Error occurred while Import Employess  see')
			err_name_html = f' <a href="/app/error-log/{err.name}"><b>{err.name}</b></a>'
			frappe.msgprint(err_msg + err_name_html)
			data = []
		
		for d in data:
			d = self.get_clean_data(d)
			nid	= d.get('nid','')
			if not frappe.db.exists("Employee",d['employee_no']):
				if len(nid) > 0 and len(frappe.get_list('Employee', filters={'nid': nid }))>0:
					exists += 1
					continue

				date_of_birth = d.get('birth_date_g', False)
				employee_number = d.get('employee_no','')
				first_name = d.get('fullname_ar','')
				if not date_of_birth:
					msg = _('Missing Date Of Birth')
					error_msgs += f'<tr><th>{employee_number}</th><td>{first_name}</td><td>{msg}</td></tr>'
					errors += 1
					continue
				
				emp = frappe.new_doc("Employee")
				emp.date_of_birth = d.get('birth_date_g', '')
				emp.first_name = d.get('fullname_ar', '')
				emp.full_name_en = d.get('fullname_en', '')
				emp.employee_number = employee_number
				emp.salary_mode = 'Bank'
				emp.bank_name = d.get('Bank', '')
				emp.paymnet_type=d.get('payment_type', '')
				emp.current_address = d.get('employee_address', '')
				emp.bank_ac_no = d.get('IBAN', '')
				emp.birth_place = d.get('birth_place', '')
				emp.handicap = d.get('handicap', '')
				emp.marital_status = d.get('marital_status', '')
				emp.cell_number = d.get('mobile', '')
				emp.religion = d.get('religion', '')

				
				emp.health_insurance_no = d.get('insurance_card_number', '')
				emp.self_service = d.get('Self_service', '')

				emp.branch_working_place = d.get('branch_working_place', '')
				emp.direct_manager = d.get('direct_manager', '')
				emp.department = d.get('employee_class', '')
				emp.personal_email = d.get('employee_email', '')
				emp.employee_photo = d.get('employee_photo', '')
				emp.insurance_card_class = d.get('insurance_card_class', '')
				emp.insurance_card_expire = d.get('insurance_card_expire', '')
				emp.payroll_card_number = d.get('payroll_card_no', '')
				emp.health_certificate = d.get('health_certificate', '')

				emp.from_api = 1
				emp.valid_data = 0
				
				emp.flags.ignore_mandatory = True

				emp.birth_date_hijri = d.get('birth_date_h', '')
				emp.moyser_employee_status=d.get('employee_status', '')
				emp.status = 'Inactive' #values_lookup[d.get('employee_status','')]
				emp.nid = nid

				nationality = d.get('nationality', '')
				if nationality != '':
					emp.nationality = self.check_link_data('Nationality',nationality,'nationality')

				employee_branch = d.get('branch_name', '')
				if employee_branch != '':
					emp.branch = self.check_link_data("Branch",employee_branch,'branch')
				
				employee_class = d.get('employee_class', '')
				if employee_class != '':
					emp.department = self.check_link_data("Department",employee_class,'department_name')
				

				employee_health_insurance_provider = d.get('insurance_card_company', '')
				if employee_health_insurance_provider != '':
					emp.health_insurance_provider = self.check_link_data("Employee Health Insurance",employee_health_insurance_provider,'health_insurance_name')

				employee_designation = d.get('job_title', '')
				if employee_designation != '':
					emp.designation = self.check_link_data("Designation",employee_designation,'designation_name')
					
				employee_gender = d.get('gender', '')
				if employee_gender != '':
					emp.gender = self.check_link_data("Gender",employee_gender,'gender')
				
				emp.save()
				sucess += 1
			else:
				exists += 1
		frappe.db.commit()

		if len(error_msgs) > 0:
			error_msgs = f'''<table class="table table-bordered">
							<thead>
							<tr>
							<th>Employee No.</th>
							<th>Name</th>
							<th>Error</th>
							</tr></thead>
							<tbody>{error_msgs}</tbody></table>'''

		msg = frappe.msgprint(f"""
		<table class="table table-bordered">
		<tbody>
			<tr>
			<th scope="row"><span class="indicator green"></span>Sucess</th>
			<td>{sucess}</td>
			</tr>
			<tr>
			<th scope="row"><span class="indicator orange"></span>Exists</th>
			<td>{exists}</td>
			</tr>
			<tr>
			<th scope="row"><span class="indicator red"></span>Errors</th>
			<td>{errors}</td>
			</tr>
		</tbody>
		</table>
		{'' if error_msgs is None else error_msgs}
		""",title=f'{len(data)} Employess Imported',indicator='Cs')

	@frappe.whitelist()
	def import_employee_class(self,company_id):
		errors = 0
		sucess = 0
		data = []
		error_msgs = ''

		if not company_id:
			company_id = self.get_company_id()
		
		if not company_id:
			msg = _(f"Set Company id please")
			frappe.throw(f"{msg}.!")
		url = f'https://www.mosyr.io/en/api/migration-classes.json?company_id={company_id}'
		res = False
		try:
			res = requests.get(url)
			res.raise_for_status()

			if res.ok and res.status_code == 200:
				data = res.json()
		except Exception as e:
			status_code = ''
			errors += 1
			if res:
				status_code = res.status_code
				status_code = f"error code {status_code}"
			err = frappe.log_error(f"{e}", f'Import contracts Faield. {status_code}!')
			err_msg = _('An Error occurred while Import branches  see')
			err_name_html = f' <a href="/app/error-log/{err.name}"><b>{err.name}</b></a>'
			frappe.msgprint(err_msg + err_name_html)
			data = []

		for d in data:
			d = self.get_clean_data(d)
			debartment_class = d.get('name')
			mosyr_key = d.get('key')
			if mosyr_key :
				if debartment_class:
					self.check_link_data("Department",debartment_class,"department_name")
					sucess +=1
				else:
					msg = f"dosen't have Employee class"
					error_msgs += f'<tr><th>{mosyr_key}</th><td>{msg}</td></tr>'
					errors +=1
		if len(error_msgs) > 0:
			error_msgs = f'''<table class="table table-bordered">
								<thead>
								<tr>
								<th>Mosyr Key.</th>
								<th>Error</th>
								</tr></thead>
								<tbody>{error_msgs}</tbody></table>'''
		msg = frappe.msgprint(f"""
		<table class="table table-bordered">
		<tbody>
			<tr>
			<th scope="row"><span class="indicator green"></span>Sucess</th>
			<td>{sucess}</td>
			</tr>
			<tr>
			<th scope="row"><span class="indicator red"></span>Errors</th>
			<td>{errors}</td>
			</tr>
		</tbody>
		</table>
		{'' if error_msgs is None else error_msgs}
		""",title=f'{len(data)} Debartment Imported',indicator='Cs')

	@frappe.whitelist()
	def import_contracts(self,company_id):
		errors = 0
		sucess = 0
		exists = 0 
		error_msgs = ''

		values_lookup={
			'selfspouse1dep': 'Employee & Spouse',
			'travelticketsself': 'Employee Only',
			'selfspouse2dep': 'Family with 2 Dependant',
			'selfspouse3dep': 'Family with 3 Dependant',
			'no': 'No',
			'' : ''
		}
		
		if not company_id:
			company_id = self.get_company_id()
		
		if not company_id:
			msg = _(f"Set Company id please")
			frappe.throw(f"{msg}.!")
			
		url = f'https://www.mosyr.io/en/api/migration-contracts.json?company_id={company_id}'
		res = False
		try:
			res = requests.get(url)
			res.raise_for_status()

			if res.ok and res.status_code == 200:
				data = res.json()
		except Exception as e:
			status_code = ''
			errors += 1
			if res:
				status_code = res.status_code
				status_code = f"error code {status_code}"
			err = frappe.log_error(f"{e}", f'Import contracts Faield. {status_code}!')
			err_msg = _('An Error occurred while Import branches  see')
			err_name_html = f' <a href="/app/error-log/{err.name}"><b>{err.name}</b></a>'
			frappe.msgprint(err_msg + err_name_html)
			data = []
		for d in data:
			d = self.get_clean_data(d)
			if not frappe.db.exists("Employee Contract", {'nid':d.get('nid')}):
				contract = frappe.new_doc("Employee Contract")	
				### Info
				contract.hiring_start_date_g = d.get('hiring_start_date', '')
				contract.commision = d.get('commision', '').capitalize()
				contract.contract_type = d.get('contract_type', '').capitalize()
				contract.vacation_period = d.get('vacation_period', '')
				contract.contract_start_g = d.get('contract_start_date', '')
				contract.commision_at_end_of_contract = d.get('commision_at_end_of_contract', '').capitalize()
				contract.contract_status= d.get('contract_status', '')
				contract.vacation_travel_tickets = values_lookup[d.get('vacation_travel_tickets')]
				contract.contract_end_g = d.get('contract_end_date', '')
				contract.commision_precentage = d.get('commision_precentage', '')
				contract.leaves_consumer_balance = d.get('leaves_consumed_balance', '')
				contract.over_time_included = d.get('over_time_included', '').capitalize()
				contract.job_description_file = d.get('job_description_file', '')
				contract.notes = d.get('notes', '')
				contract.hiring_letter = d.get('hiring_letter', '')

				### Contract Financial Details
				contract.basic_salary = d.get('basic_salary', '')
				contract.allowance_transportations = d.get('allowance_trans', '').capitalize()
				contract.allowance_housing = d.get('allowance_housing', '').capitalize()
				contract.allowance_phone = d.get('allowance_phone', '').capitalize()
				contract.nature_of_work_allowance = d.get('allowance_worknatural', '').capitalize()
				contract.allowance_other = d.get('allowance_other', '').capitalize()
				contract.allowance_feeding = d.get('allowance_living', '').capitalize()#$$$

				### Allowance Transportations
				contract.trans_start_date_g = d.get('allowance_trans_start_date', '')
				contract.trans_end_date_g = d.get('allowance_trans_end_date', '')
				contract.allowance_period = d.get('allowance_period', '')
				contract.allowance_trans_schdl_1 == d.get('allowance_trans_schdl_1', '')
				contract.allowance_trans_schdl_2 == d.get('allowance_trans_schdl_2', '')
				contract.trans_amount_type = d.get('allowance_trans_amount_type', '').capitalize()
				contract.trans_amount_value = d.get('allowance_trans_value', '')

				### Allowance House
				contract.housing_start_g = d.get('allowance_housing_start_date', '')
				contract.housing_end_date_g = d.get('allowance_housing_end_date', '')
				contract.house_schdls = d.get('allowance_housing_schedule', '').capitalize()
				contract.allowance_house_schdl_1 == d.get('allowance_housing_schdl_1', '')
				contract.allowance_house_schdl_2 == d.get('allowance_housing_schdl_2', '')
				# contract.house_amount_type = d.get('allowance_housing_amount').capitalize()#$$$
				contract.house_amount_value = d.get('allowance_housing_value', '')

				### Allowance Phone
				contract.phone_start_date_g = d.get('allowance_phone_start_date', '')
				contract.phone_end_date_g = d.get('allowance_phone_end_date', '')
				contract.phone_schdls = d.get('allowance_phone_schedule', '').capitalize()
				contract.allowance_phone_schdl_1 == d.get('allowance_phone_schdl_1', '')
				contract.allowance_phone_schdl_1 == d.get('allowance_phone_schdl_1', '')
				contract.allowance_phone_schdl_2 == d.get('allowance_phone_schdl_2', '')
				contract.phone_amount_type = d.get('allowance_phone_amount_type', '').capitalize()
				contract.phone_amount_value = d.get('allowance_phone_value', '')

				### Allowance Natureow
				contract.natureow_start_date_g = d.get('allowance_worknatural_start_date', '')
				contract.natureow_end_date_g = d.get('allowance_worknatural_end_date', '')
				contract.natureow_schdls = d.get('allowance_worknatural_schedule').capitalize()
				contract.allowance_natow_schdl_1 == d.get('allowance_worknatural_schdl_1', '')
				contract.allowance_natow_schdl_2 == d.get('allowance_worknatural_schdl_2', '')
				contract.natureow_amount_type = d.get('allowance_worknatural_amount_type', '').capitalize()
				contract.natureow_amount_value = d.get('allowance_worknatural_value', '')

				### Allowance Feeding
				contract.feeding_start_date_g = d.get('allowance_living_start_date', '')#$$$
				contract.feeding_end_date_g = d.get('allowance_living_end_date', '')#$$$
				contract.feed_schdls = d.get('allowance_living_schedule', '').capitalize()#$$$
				contract.allowance_feed_schdl_1 == d.get('allowance_living_schdl_1', '')
				contract.allowance_feed_schdl_2 == d.get('allowance_living_schdl_2', '')
				# contract.feed_amount_type = d.get('allowance_living_amount', '')#$$$
				contract.feed_amount_value = d.get('allowance_living_value', '')#$$$

				### Allowance Other
				contract.other_start_date_g = d.get('allowance_other_start_date', '')
				contract.other_end_date_g = d.get('allowance_other_end_date', '')
				contract.other_schdls = d.get('allowance_other_schedule', '').capitalize()
				contract.allowance_other_schdl_1 == d.get('allowance_other_schdl_1', '')
				contract.allowance_other_schdl_1 == d.get('allowance_other_schdl_1', '')
				contract.allowance_other_schdl_2 == d.get('allowance_other_schdl_2', '')
				contract.other_amount_type = d.get('allowance_other_amount_type', '').capitalize()
				contract.other_amount_value = d.get('allowance_other_value', '')
				contract.from_api = 1
				contract.nid = d.get('nid', '')
				contract.comment = d.get('comments', '')

				msg = _('Employee is not defined in system')
				if not frappe.db.exists("Employee", {'nid': d.get('nid')}) :
					employee_name=d.get('name')
					error_msgs += f'<tr><th>{contract.nid}</th><td>{employee_name}</td><td>{msg}</td></tr>'
					errors += 1
					continue
				else:
					contract.save()
					sucess+=1
			else:
				exists += 1 
		frappe.db.commit()

		if len(error_msgs) > 0:
			error_msgs = f'''<table class="table table-bordered">
							<thead>
							<tr>
							<th>Employee NID.</th>
							<th>Name</th>
							<th>Error</th>
							</tr></thead>
							<tbody>{error_msgs}</tbody></table>'''

		msg = frappe.msgprint(f"""
		<table class="table table-bordered">
		<tbody>
			<tr>
			<th scope="row"><span class="indicator green"></span>Sucess</th>
			<td>{sucess}</td>
			</tr>
			<tr>
			<th scope="row"><span class="indicator orange"></span>Exists</th>
			<td>{exists}</td>
			</tr>
			<tr>
			<th scope="row"><span class="indicator red"></span>Errors</th>
			<td>{errors}</td>
			</tr>
		</tbody>
		</table>
		{'' if error_msgs is None else error_msgs}
		""",title=f'{len(data)} Contracts Imported',indicator='Cs')	

	@frappe.whitelist()
	def import_benefits(self,company_id):
		errors = 0
		sucess = 0
		data = []
		error_msgs = ''

		lookup_value={
			"backPay": "Back Pay",
			"bonus": "Bonus",
			"businessTrip": "Business Trip",
			"OverTime": "Overtime",
			"commission": "Commission"
		}
		if not company_id:
			company_id = self.get_company_id()
		
		if not company_id:
			msg = _(f"Set Company id please")
			frappe.throw(f"{msg}.!")
		url = f'https://www.mosyr.io/en/api/migration-benefits.json?company_id={company_id}'
		res = False
		try:
			res = requests.get(url)
			res.raise_for_status()

			if res.ok and res.status_code == 200:
				data = res.json()
		except Exception as e:
			status_code = ''
			errors += 1
			if res:
				status_code = res.status_code
				status_code = f"error code {status_code}"
			err = frappe.log_error(f"{e}", f'Import contracts Faield. {status_code}!')
			err_msg = _('An Error occurred while Import branches  see')
			err_name_html = f' <a href="/app/error-log/{err.name}"><b>{err.name}</b></a>'
			frappe.msgprint(err_msg + err_name_html)
			data = []

		for d in data:
			d = self.get_clean_data(d)
			employee_name = d.get('name')
			nid = d.get('nid')
			benefits = frappe.new_doc("Employee Benefits")	
			benefits.date = d.get('date')
			benefits.addition_type = lookup_value[d.get('addition_type')]
			benefits.payroll_month = d.get('payroll_month')
			benefits.amount = d.get('amount')
			benefits.details = d.get('details')
			benefits.notes = d.get('notes')
			benefits.nid = nid
			benefits.from_api = 1
			if frappe.db.exists("Employee", {'nid':d.get('nid')}):
				if frappe.db.exists("Employee Contract", {'nid': d.get('nid')}):
					benefits.save()
					sucess += 1
				else:
					msg = "Employee does not have Contract"
					error_msgs += f'<tr><th>{nid}</th><td>{employee_name}</td><td>{msg}</td></tr>'
					errors += 1 
			else:
				msg = "Employee is not defined in System"
				error_msgs += f'<tr><th>{nid}</th><td>{employee_name}</td><td>{msg}</td></tr>'
				errors += 1 
		
		frappe.db.commit()
		if len(error_msgs) > 0:
			error_msgs = f'''<table class="table table-bordered">
								<thead>
								<tr>
								<th>Employee NID.</th>
								<th>Name</th>
								<th>Error</th>
								</tr></thead>
								<tbody>{error_msgs}</tbody></table>'''

		msg = frappe.msgprint(f"""
		<table class="table table-bordered">
		<tbody>
			<tr>
			<th scope="row"><span class="indicator green"></span>Sucess</th>
			<td>{sucess}</td>
			</tr>
			<tr>
			<th scope="row"><span class="indicator red"></span>Errors</th>
			<td>{errors}</td>
			</tr>
		</tbody>
		</table>
		{'' if error_msgs is None else error_msgs}
		""",title=f'{len(data)} Benefits Imported',indicator='Cs')	

	@frappe.whitelist()
	def import_deductions(self,company_id):
		errors = 0
		sucess = 0
		data = []
		error_msgs = ''


		if not company_id:
			company_id = self.get_company_id()
		
		if not company_id:
			msg = _(f"Set Company id please")
			frappe.throw(f"{msg}.!")
		url = f'https://www.mosyr.io/en/api/migration-deductions.json?company_id={company_id}'
		res = False
		try:
			res = requests.get(url)
			res.raise_for_status()

			if res.ok and res.status_code == 200:
				data = res.json()
		except Exception as e:
			status_code = ''
			errors += 1
			if res:
				status_code = res.status_code
				status_code = f"error code {status_code}"
			err = frappe.log_error(f"{e}", f'Import contracts Faield. {status_code}!')
			err_msg = _('An Error occurred while Import branches  see')
			err_name_html = f' <a href="/app/error-log/{err.name}"><b>{err.name}</b></a>'
			frappe.msgprint(err_msg + err_name_html)
			data = []

		for d in data:
			d = self.get_clean_data(d)
			employee_name = d.get('name')
			nid = d.get('nid')
			deduction = frappe.new_doc("Employee Deductions")	
			deduction.date = d.get('date')
			deduction.payroll_month = d.get('payroll_month')
			deduction.amount = d.get('amount')
			deduction.details = d.get('details')
			deduction.notes = d.get('notes')
			deduction.date = d.get('date')
			deduction.days = d.get('days')
			deduction.hours = d.get('hours')
			deduction.minutes = d.get('minutes')
			deduction.nid = d.get('nid')
			deduction.from_api = 1

			if frappe.db.exists("Employee", {'nid':d.get('nid')}):
				if frappe.db.exists("Employee Contract", {'nid': d.get('nid')}):
					deduction.save()
					sucess += 1
				else:
					msg = "Employee does not have Contract"
					error_msgs += f'<tr><th>{nid}</th><td>{employee_name}</td><td>{msg}</td></tr>'
					errors += 1 
			else:
				msg = "Employee is not defined in System"
				error_msgs += f'<tr><th>{nid}</th><td>{employee_name}</td><td>{msg}</td></tr>'
				errors += 1 

		frappe.db.commit()

		if len(error_msgs) > 0:
			error_msgs = f'''<table class="table table-bordered">
								<thead>
								<tr>
								<th>Employee NID.</th>
								<th>Name</th>
								<th>Error</th>
								</tr></thead>
								<tbody>{error_msgs}</tbody></table>'''

		msg = frappe.msgprint(f"""
		<table class="table table-bordered">
		<tbody>
			<tr>
			<th scope="row"><span class="indicator green"></span>Sucess</th>
			<td>{sucess}</td>
			</tr>
			<tr>
			<th scope="row"><span class="indicator red"></span>Errors</th>
			<td>{errors}</td>
			</tr>
		</tbody>
		</table>
		{'' if error_msgs is None else error_msgs}
		""",title=f'{len(data)} Deductions Imported',indicator='Cs')


	@frappe.whitelist()
	def import_identity(self,company_id):
		errors = 0
		sucess = 0
		data = []
		error_msgs = ''
		if not company_id:
			company_id = self.get_company_id()
		
		if not company_id:
			msg = _(f"Set Company id please")
			frappe.throw(f"{msg}.!")
		url = f'https://www.mosyr.io/en/api/migration-ids.json?company_id={company_id}'
		res = False
		lookup_value = {
			'nationalid': 'National ID',
			'displacedtribalscard': 'Displaced tribals card',
			'gccstatesidentity': 'GCC States Identity',
			'bordersentrynumber': 'Borders Entry Number',
			'number': 'Number',
			'drivinglicense': 'Driving License',
			'iqama': 'Iqama'
		}
		try:
			res = requests.get(url)
			res.raise_for_status()
			if res.ok and res.status_code == 200:
				data = res.json()
		except Exception as e:
			status_code = ''
			errors += 1

			if res:
				status_code = res.status_code
				status_code = f"error code {status_code}"
			err = frappe.log_error(f"{e}", f'Import contracts Faield. {status_code}!')
			err_msg = _('An Error occurred while Import branches  see')
			err_name_html = f' <a href="/app/error-log/{err.name}"><b>{err.name}</b></a>'
			frappe.msgprint(err_msg + err_name_html)
			data = []
		for d in data:
			d = self.get_clean_data(d)
			nid = d.get('nid', '')
			api_key= d.get('key', '')
			first_name = d.get('name', '')
			if nid:
				employees = frappe.get_list("Employee",filters={"nid":nid})
				if len(employees) == 0:
					msg = "Employee is not exist in system"
					error_msgs += f'<tr><th>{nid}</th><td>{first_name}</td><td>{msg}</td></tr>'
					errors += 1
					continue
				employee = employees[0].name
				employee = frappe.get_doc('Employee', employee)

				api_key = d.get('key', '')
				api_key_exists = False
				api_key_exists_at = -1
				if api_key != '':
					for k in employee.identity:
						mosyr_key = k.key
						if mosyr_key:
							if api_key == mosyr_key:
								api_key_exists = True
								api_key_exists_at = k.idx
				if api_key_exists:
					if api_key_exists_at != -1:
						current_data = employee.identity[api_key_exists_at-1]
						current_data.id_type = lookup_value[d.get('id_type', '')] 
						current_data.nautional_id_number = d.get('id_number', '')
						current_data.id_issue_place_english = d.get('issue_place_english', '')
						current_data.status_date_g = d.get('issue_date', '')
						current_data.id_expire_date_g = d.get('expire_date', '')
						current_data.border_entry_port = d.get('border_entry_port', '')
						current_data.borders_entry_date_g = d.get('border_entry_date', '')
						current_data.border_entry_number = d.get('border_entry_number', '')
						current_data.id_photo = d.get('id_photo', '')
						sucess += 1
				else:
					employee.append('identity', {
						'id_type':lookup_value[d.get('id_type', '')] ,
						'nautional_id_number': d.get('id_number', ''),
						'id_issue_place_english': d.get('issue_place_english', ''),
						'id_issue_date_g':d.get('issue_date', ''),
						'id_expire_date_g':d.get('expire_date', ''),
						'border_entry_port':d.get('border_entry_port', ''),
						'borders_entry_date_g':d.get('border_entry_date', ''),
						'border_entry_number':d.get('border_entry_number', ''),
						'id_photo':d.get('id_photo', ''),
						'key': api_key
					})
					employee.flags.ignore_mandatory = True
					employee.save()
					sucess += 1
			else:
					msg = "Employee is not exist in system"
					error_msgs += f'<tr><th>{api_key}</th><td>{first_name}</td><td>{msg}</td></tr>'
					errors += 1
		frappe.db.commit()
		if len(error_msgs) > 0:
			error_msgs = f'''<table class="table table-bordered">
							<thead>
							<tr>
							<th>Employee Key.</th>
							<th>Name</th>
							<th>Error</th>
							</tr></thead>
							<tbody>{error_msgs}</tbody></table>'''	
		
		msg = frappe.msgprint(f"""
		<table class="table table-bordered">
		<tbody>
			<tr>
			<th scope="row"><span class="indicator green"></span>Sucess</th>
			<td>{sucess}</td>
			</tr>
			<tr>
			<th scope="row"><span class="indicator red"></span>Errors</th>
			<td>{errors}</td>
			</tr>
		</tbody>
		</table>
		{'' if error_msgs is None else error_msgs}
		""",title=f'{len(data)} Identity Imported',indicator='Cs')


	@frappe.whitelist()
	def import_passport(self,company_id):
		errors = 0
		sucess = 0
		data = []
		error_msgs = ''

		if not company_id:
			company_id = self.get_company_id()
		
		if not company_id:
			msg = _(f"Set Company id please")
			frappe.throw(f"{msg}.!")
		url = f'https://www.mosyr.io/en/api/migration-passports.json?company_id={company_id}'
		res = False
		try:
			res = requests.get(url)
			res.raise_for_status()
			if res.ok and res.status_code == 200:
				data = res.json()

		except Exception as e:
			status_code = ''
			errors += 1
			if res:
				status_code = res.status_code
				status_code = f"error code {status_code}"
			err = frappe.log_error(f"{e}", f'Import contracts Faield. {status_code}!')
			err_msg = _('An Error occurred while Import branches  see')
			err_name_html = f' <a href="/app/error-log/{err.name}"><b>{err.name}</b></a>'
			frappe.msgprint(err_msg + err_name_html)
			data = []
		for d in data:
			d = self.get_clean_data(d)
			nid = d.get('nid', '')
			api_key = d.get('key', '')
			first_name = d.get('name', '')
			if nid:
				employees = frappe.get_list("Employee",filters={"nid":nid})
				if len(employees) == 0:
					msg = "Employee is not exist in system"
					error_msgs += f'<tr><th>{nid}</th><td>{first_name}</td><td>{msg}</td></tr>'
					errors += 1
					continue
				employee = employees[0].name
				employee = frappe.get_doc('Employee', employee)
				api_key = d.get('key', '')
				
				api_key_exists = False
				api_key_exists_at = -1
				jop_title = d.get('jobtitle', '')
				if jop_title in ['_']:
					jop_title =''
				if api_key != '':
					for k in employee.passport:
						mosyr_key = k.key
						if mosyr_key:
							if api_key == mosyr_key:
								api_key_exists = True
								api_key_exists_at = k.idx
				if api_key_exists:
					if api_key_exists_at != -1:
						current_data = employee.passport[api_key_exists_at-1]
						current_data.passport_number = d.get('passport_number', '')
						current_data.passport_issue_place = d.get('passport_issue_place', '')
						current_data.passport_expire_date_g = d.get('passport_expire', '')
						current_data.job_in_passport = jop_title
						sucess += 1
				else:
					
					employee.append('passport', {
							'passport_number':d.get('passport_number', ''),
							'passport_issue_place': d.get('passport_issue_place', ''),
							'passport_expire_date_g': d.get('passport_expire', ''),
							'job_in_passport':jop_title,
							# 'passport_photo':d.get('passport_photo', ''),
							'key':api_key
						})
					employee.flags.ignore_mandatory = True
					employee.save()
					sucess += 1
			else:
				msg = "Employee is not exist in system"
				error_msgs += f'<tr><th>{api_key}</th><td>{first_name}</td><td>{msg}</td></tr>'
				errors += 1
					
		frappe.db.commit()
		if len(error_msgs) > 0:

			error_msgs = f'''<table class="table table-bordered">
							<thead>
							<tr>
							<th>Employee Key.</th>
							<th>Name</th>
							<th>Error</th>
							</tr></thead>
							<tbody>{error_msgs}</tbody></table>'''	

			msg = frappe.msgprint(f"""
		<table class="table table-bordered">
		<tbody>
			<tr>
			<th scope="row"><span class="indicator green"></span>Sucess</th>
			<td>{sucess}</td>
			</tr>
			<tr>
			<th scope="row"><span class="indicator red"></span>Errors</th>
			<td>{errors}</td>
			</tr>
		</tbody>
		</table>
		{'' if error_msgs is None else error_msgs}
		""",title=f'{len(data)} PassPort Imported',indicator='Cs')


	@frappe.whitelist()
	def import_dependents(self,company_id):
		errors = 0
		sucess = 0
		data = []
		error_msgs = ''
		if not company_id:
			company_id = self.get_company_id()
		
		if not company_id:
			msg = _(f"Set Company id please")
			frappe.throw(f"{msg}.!")
		url = f'https://www.mosyr.io/en/api/migration-employee-dependents.json?company_id={company_id}'
		res = False
		try:
			res = requests.get(url)
			res.raise_for_status()

			if res.ok and res.status_code == 200:
				data = res.json()
		except Exception as e:
			status_code = ''
			errors += 1
			if res:
				status_code = res.status_code
				status_code = f"error code {status_code}"
			err = frappe.log_error(f"{e}", f'Import contracts Faield. {status_code}!')
			err_msg = _('An Error occurred while Import branches  see')
			err_name_html = f' <a href="/app/error-log/{err.name}"><b>{err.name}</b></a>'
			frappe.msgprint(err_msg + err_name_html)
			data = []
		for d in data:
			d = self.get_clean_data(d)
			nid = d.get('nid','')
			api_key = d.get('key','')
			first_name = d.get('name', '')
			if nid:
				employees = frappe.get_list("Employee",filters={"nid":nid})
				if len(employees) == 0:
					msg = "Employee is not exist in system"
					error_msgs += f'<tr><th>{nid}</th><td>{first_name}</td><td>{msg}</td></tr>'
					errors += 1
					continue
				employee = employees[0].name
				employee = frappe.get_doc('Employee', employee)
				api_key = d.get('key', '')
				
				api_key_exists = False
				api_key_exists_at = -1

				if api_key != '':
					for k in employee.dependent:
						mosyr_key = k.key
						if mosyr_key:
							if api_key == mosyr_key:
								api_key_exists = True
								api_key_exists_at = k.idx
				if api_key_exists:
					if api_key_exists_at != -1:
						current_data = employee.dependent[api_key_exists_at-1]
						current_data.first_name_ar = d.get('fullname_ar', '')
						current_data.first_name_en = d.get('fullname_en', '')
						current_data.birth_date_g = d.get('birth_date_g', '')
						# current_data.attachement = d.get('attachement', '')
						current_data.dependant_relationship = d.get('relationship', '')
						sucess += 1 
				else:
					employee.append('dependent', {
							'first_name_ar':d.get('fullname_ar', ''),
							'first_name_en': d.get('fullname_en', ''),
							'birth_date_g': d.get('birth_date_g', ''),
							# 'attachement':d.get('attachement', ''),
							'dependant_relationship':d.get('relationship', ''),
							'key':api_key
						})
					employee.flags.ignore_mandatory = True
					employee.save()
					sucess += 1
			else:
				msg = "Employee is not exist in system"
				error_msgs += f'<tr><th>{api_key}</th><td>{first_name}</td><td>{msg}</td></tr>'
				errors += 1			
		frappe.db.commit()
		if len(error_msgs) > 0:
			error_msgs = f'''<table class="table table-bordered">
							<thead>
							<tr>
							<th>Employee Key.</th>
							<th>Name</th>
							<th>Error</th>
							</tr></thead>
							<tbody>{error_msgs}</tbody></table>'''	
		msg = frappe.msgprint(f"""
		<table class="table table-bordered">
		<tbody>
			<tr>
			<th scope="row"><span class="indicator green"></span>Sucess</th>
			<td>{sucess}</td>
			</tr>
			<tr>
			<th scope="row"><span class="indicator red"></span>Errors</th>
			<td>{errors}</td>
			</tr>
		</tbody>
		</table>
		{'' if error_msgs is None else error_msgs}
		""",title=f'{len(data)} Dependents Imported',indicator='Cs')


	@frappe.whitelist()
	def import_employee_status(self,company_id):
		errors = 0
		sucess = 0
		data = []
		error_msgs = ''
		if not company_id:
			company_id = self.get_company_id()
		
		if not company_id:
			msg = _(f"Set Company id please")
			frappe.throw(f"{msg}.!")
		url = f'https://www.mosyr.io/en/api/migration-employee-status.json?company_id={company_id}'
		res = False
		try:
			res = requests.get(url)
			res.raise_for_status()
			
			if res.ok and res.status_code == 200:
				data = res.json()
		except Exception as e:
			status_code = ''
			errors += 1
			if res:
				status_code = res.status_code
				status_code = f"error code {status_code}"
			err = frappe.log_error(f"{e}", f'Import contracts Faield. {status_code}!')
			err_msg = _('An Error occurred while Import branches  see')
			err_name_html = f' <a href="/app/error-log/{err.name}"><b>{err.name}</b></a>'
			frappe.msgprint(err_msg + err_name_html)
			data = []
		for d in data:
			d = self.get_clean_data(d)
			nid = d.get('nid','')
			first_name = d.get('name', '')
			api_key = d.get('key', '')
			if nid:
				employees = frappe.get_list("Employee",filters={"nid":nid})
				if len(employees) == 0:
					msg = "Employee is not exist in system"
					error_msgs += f'<tr><th>{nid}</th><td>{first_name}</td><td>{msg}</td></tr>'
					errors += 1
					continue
				employee = employees[0].name
				employee = frappe.get_doc('Employee', employee)

				api_key = d.get('key', '')
				api_key_exists = False
				api_key_exists_at = -1

				if api_key != '':
					for k in employee.mosyr_employee_status:
						mosyr_key = k.mosyr_key
						if mosyr_key:
							if api_key == mosyr_key:
								api_key_exists = True
								api_key_exists_at = k.idx
				if api_key_exists:
					if api_key_exists_at != -1:
						current_data = employee.mosyr_employee_status[api_key_exists_at-1]
						current_data.status_date_g = d.get('status_date', '')
						current_data.status_reason = d.get('status_reason', '')
						current_data.status1 = d.get('status', '')
						sucess += 1
				else:
					employee.append('mosyr_employee_status', {
							'status1': d.get('status', ''),
							'status_date_g': d.get('status_date', ''),
							'status_reason': d.get('status_reason', ''),
							# 'attachment':d.get('attachement', ''),
							'mosyr_key':d.get('key')
						})

					sucess += 1
					employee.flags.ignore_mandatory = True
					employee.save()
			else:
				msg = "Employee is not exist in system"
				error_msgs += f'<tr><th>{api_key}</th><td>{first_name}</td><td>{msg}</td></tr>'
				errors += 1
					
		frappe.db.commit()
		if len(error_msgs) > 0:
			error_msgs = f'''<table class="table table-bordered">
							<thead>
							<tr>
							<th>Employee Key.</th>
							<th>Name</th>
							<th>Error</th>
							</tr></thead>
							<tbody>{error_msgs}</tbody></table>'''	
		msg = frappe.msgprint(f"""
		<table class="table table-bordered">
		<tbody>
			<tr>
			<th scope="row"><span class="indicator green"></span>Sucess</th>
			<td>{sucess}</td>
			</tr>
			<tr>
			<th scope="row"><span class="indicator red"></span>Errors</th>
			<td>{errors}</td>
			</tr>
		</tbody>
		</table>
		{'' if error_msgs is None else error_msgs}
		""",title=f'{len(data)} Employee Imported',indicator='Cs')


	@frappe.whitelist()
	def import_employee_qualifications(self,company_id):
		errors = 0
		sucess = 0
		data = []
		error_msgs = ''
		if not company_id:
			company_id = self.get_company_id()
		
		if not company_id:
			msg = _(f"Set Company id please")
			frappe.throw(f"{msg}.!")
		url = f'https://www.mosyr.io/en/api/migration-employee-qualifications.json?company_id={company_id}'
		res = False
		try:
			res = requests.get(url)
			res.raise_for_status()

			if res.ok and res.status_code == 200:
				data = res.json()
		except Exception as e:
			status_code = ''
			errors += 1
			if res:
				status_code = res.status_code
				status_code = f"error code {status_code}"
			err = frappe.log_error(f"{e}", f'Import contracts Faield. {status_code}!')
			err_msg = _('An Error occurred while Import branches  see')
			err_name_html = f' <a href="/app/error-log/{err.name}"><b>{err.name}</b></a>'
			frappe.msgprint(err_msg + err_name_html)
			data = []
		for d in data:
			d = self.get_clean_data(d)
			nid = d.get('nid','')
			first_name = d.get('name', '')
			api_key = d.get('key', '')
			if nid:
				employees = frappe.get_list("Employee",filters={"nid":nid})
				if len(employees) == 0:
					msg = "Employee is not exist in system"
					error_msgs += f'<tr><th>{nid}</th><td>{first_name}</td><td>{msg}</td></tr>'
					errors += 1
					continue
				employee = employees[0].name
				employee = frappe.get_doc('Employee', employee)
				qualification_attendance_date = d.get('attendance_date', '')
				qualification_held_date = d.get('issue_date', '')
				attendance = datetime.strptime(qualification_attendance_date,("%d-%m-%Y"))
				held = datetime.strptime(qualification_held_date,("%d-%m-%Y"))
				attendance_date = attendance.strftime ("%Y-%m-%d")
				held_date = held.strftime ("%Y-%m-%d")
				api_key = d.get('key', '')
				lookup_value = {
					'training' : 'Training Certificate'
				}
				degree = d.get('degree', '')
				api_key_exists = False
				api_key_exists_at = -1

				if api_key != '':
					for k in employee.education:
						mosyr_key = k.key
						if mosyr_key:
							if api_key == mosyr_key:
								api_key_exists = True
								api_key_exists_at = k.idx
				if api_key_exists:	
					if api_key_exists_at != -1:
						current_data = employee.education[api_key_exists_at-1]
						current_data.qualification_degree = lookup_value[degree]
						current_data.specialty = d.get('specialization', '')
						current_data.qualification_attendance_date = attendance_date
						current_data.certificate_experience = d.get('certificate_experience', '')
						current_data.qualification_held_date = held_date
						current_data.qualification_mark = d.get('qualification_mark', '')
						current_data.gpa_rate = d.get('GPA_rate', '')
						current_data.qualification_institute = d.get('issue_institute', '')
						current_data.qualification_location = d.get('issue_place', '')
						sucess += 1
				else:	
					employee.append('education', {
							'qualification_degree':lookup_value[degree],
							'specialty': d.get('specialization', ''),
							'qualification_attendance_date': attendance_date,
							'certificate_experience':d.get('certificate_experience', ''),
							'qualification_held_date':held_date,
							'qualification_mark':d.get('qualification_mark', ''),
							'gpa_rate':d.get('GPA_rate', ''),
							'qualification_institute':d.get('issue_institute', ''),
							'qualification_location':d.get('issue_place', ''),
							# 'attachment':d.get('attachement', ''),
							'key':api_key
						})
				employee.flags.ignore_mandatory = True
				employee.save()
				sucess += 1
			else:
				msg = "Employee is not exist in system"
				error_msgs += f'<tr><th>{api_key}</th><td>{first_name}</td><td>{msg}</td></tr>'
				errors += 1
					
		frappe.db.commit()
		if len(error_msgs) > 0:
			error_msgs = f'''<table class="table table-bordered">
							<thead>
							<tr>
							<th>Employee Key.</th>
							<th>Name</th>
							<th>Error</th>
							</tr></thead>
							<tbody>{error_msgs}</tbody></table>'''	
		msg = frappe.msgprint(f"""
		<table class="table table-bordered">
		<tbody>
			<tr>
			<th scope="row"><span class="indicator green"></span>Sucess</th>
			<td>{sucess}</td>
			</tr>
			<tr>
			<th scope="row"><span class="indicator red"></span>Errors</th>
			<td>{errors}</td>
			</tr>
		</tbody>
		</table>
		{'' if error_msgs is None else error_msgs}
		""",title=f'{len(data)} qualifications Imported',indicator='Cs')


	@frappe.whitelist()
	def import_experiences(self,company_id):
		errors = 0
		sucess = 0
		data = []
		error_msgs = ''
		if not company_id:
			company_id = self.get_company_id()
		
		if not company_id:
			msg = _(f"Set Company id please")
			frappe.throw(f"{msg}.!")
		url = f'https://www.mosyr.io/en/api/migration-employee-experiences.json?company_id={company_id}'
		res = False
		try:
			res = requests.get(url)
			res.raise_for_status()

			if res.ok and res.status_code == 200:
				data = res.json()
		except Exception as e:
			status_code = ''
			errors += 1
			if res:
				status_code = res.status_code
				status_code = f"error code {status_code}"
			err = frappe.log_error(f"{e}", f'Import contracts Faield. {status_code}!')
			err_msg = _('An Error occurred while Import branches  see')
			err_name_html = f' <a href="/app/error-log/{err.name}"><b>{err.name}</b></a>'
			frappe.msgprint(err_msg + err_name_html)
			data = []
		for d in data:
			d = self.get_clean_data(d)
			nid = d.get('nid','')
			first_name = d.get('name', '')
			api_key = d.get('key', '')
			if nid:
				employees = frappe.get_list("Employee",filters={"nid":nid})
				if len(employees) == 0:
					msg = "Employee is not exist in system"
					error_msgs += f'<tr><th>{nid}</th><td>{first_name}</td><td>{msg}</td></tr>'
					errors += 1
					continue
				employee = employees[0].name
				employee = frappe.get_doc('Employee', employee)
				api_key = d.get('key', '')
				
				api_key_exists = False
				api_key_exists_at = -1

				if api_key != '':
					for k in employee.external_work_history:
						mosyr_key = k.key
						if mosyr_key:
							if api_key == mosyr_key:
								api_key_exists = True
								api_key_exists_at = k.idx
				if api_key_exists:
					if api_key_exists_at != -1:
						current_data = employee.external_work_history[api_key_exists_at-1]
						current_data.start_date_g = d.get('start_date_g', '')
						current_data.end_date_g = d.get('end_date_g', '')
						current_data.reason_of_termination = d.get('reason_of_termination', '')
						current_data.certificate_experience = d.get('certificate_experience', '')
						current_data.note = d.get('note', '')
						sucess += 1
				else:
					
					employee.append('external_work_history', {
							'start_date_g':d.get('start_date_g', ''),
							'end_date_g': d.get('end_date_g', ''),
							'reason_of_termination': d.get('reason_of_termination', ''),
							'certificate_experience':d.get('certificate_experience', ''),
							'note':d.get('note', ''),
							'key':api_key
						})
					employee.flags.ignore_mandatory = True
					employee.save()
					sucess += 1
			else:
				msg = "Employee is not exist in system"
				error_msgs += f'<tr><th>{api_key}</th><td>{first_name}</td><td>{msg}</td></tr>'
				errors += 1
					
		frappe.db.commit()
		if len(error_msgs) > 0:
			error_msgs = f'''<table class="table table-bordered">
							<thead>
							<tr>
							<th>Employee Key.</th>
							<th>Name</th>
							<th>Error</th>
							</tr></thead>
							<tbody>{error_msgs}</tbody></table>'''	
		
		msg = frappe.msgprint(f"""
		<table class="table table-bordered">
		<tbody>
			<tr>
			<th scope="row"><span class="indicator green"></span>Sucess</th>
			<td>{sucess}</td>
			</tr>
			<tr>
			<th scope="row"><span class="indicator red"></span>Errors</th>
			<td>{errors}</td>
			</tr>
		</tbody>
		</table>
		{'' if error_msgs is None else error_msgs}
		""",title=f'{len(data)} Experince Imported',indicator='Cs')


	def check_link_data(self,doctype,value,filed):
		
		company = frappe.defaults.get_global_default('company')
		company = frappe.get_doc('Company', company)
		abbr = company.abbr

		# check if dictype has abbr in the name
		value1 = value
		if doctype in ['Department']:
			value1 = f'{value} - {abbr}'
		
		exist = frappe.db.exists(doctype, value1)
		
		if not exist:
			args = {
				f'{filed}': value
			}
			# if dictype has company field
			if doctype in ['Department']:
				args.update({
					f'{filed}': value,
					'company': company.name
				})
			new_doc = frappe.new_doc(doctype)
			new_doc.update(args)
			new_doc.save()
			frappe.db.commit()
			exist=value
		return exist


	def get_clean_data(self,data):
		clear_data = {}
		for k, v in data.items():
			if isinstance(v, list):
				if len(v) == 1:
					if v[0] == '':
						clear_data[f'{k}'] = ''
				elif len(v) ==0:
					clear_data[f'{k}'] = ''

				else:
					clear_data[f'{k}'] = v
			else:
				clear_data[f'{k}'] = v
		return clear_data


	# def table_status_imported(self,data,sucess,exists, errors,doctype_name,error_msgs = None, child_table=False):
		# msg = frappe.msgprint(f"""
		# <table class="table table-bordered">
		# <tbody>
		# 	<tr>
		# 	<th scope="row"><span class="indicator green"></span>Sucess</th>
		# 	<td>{sucess}</td>
		# 	</tr>
		# 	<tr>
		# 	<th scope="row"><span class="indicator orange"></span>Exists</th>
		# 	<td>{exists}</td>
		# 	</tr>
		# 	<tr>
		# 	<th scope="row"><span class="indicator red"></span>Errors</th>
		# 	<td>{errors}</td>
		# 	</tr>
		# </tbody>
		# </table>
		# {'' if error_msgs is None else error_msgs}
		# """,title=f'{len(data)} {doctype_name} Imported',indicator='Cs')

		# return msg