# Copyright (c) 2022, AnvilERP and contributors
# For license information, please see license.txt

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
			company_id = frappe.conf.company_id or False
		
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
		frappe.msgprint(f"""
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
			company_id = frappe.conf.company_id or False
		
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
				emp.date_of_birth = d.get('birth_date_g')
				emp.first_name = d.get('fullname_ar','')
				emp.full_name_en = d.get('fullname_en','')
				emp.employee_number = employee_number
				emp.salary_mode = 'Bank'
				emp.bank_name = d.get('Bank','')
				emp.paymnet_type=d.get('payment_type','')
				emp.current_address = d.get('employee_address','')
				emp.bank_ac_no = d.get('IBAN','')
				emp.birth_place = d.get('birth_place','')
				emp.handicap = d.get('handicap','')
				emp.marital_status = d.get('marital_status','')
				emp.cell_number = d.get('mobile','')
				emp.religion = d.get('religion','')
				emp.nationality = d.get('nationality','')
				emp.health_insurance_no = d.get('insurance_card_number','')
				emp.self_service = d.get('Self_service','')

				emp.branch_working_place = d.get('branch_working_place')
				emp.direct_manager = d.get('direct_manager')
				emp.employee_class = d.get('employee_class')
				emp.personal_email = d.get('employee_email')
				emp.employee_photo = d.get('employee_photo')
				emp.insurance_card_class = d.get('insurance_card_class')
				emp.insurance_card_expire = d.get('insurance_card_expire')
				emp.payroll_card_number = d.get('payroll_card_no')
				emp.health_certificate = d.get('health_certificate')

				emp.from_api = 1
				emp.valid_data = 0
				
				# emp.date_of_joining = '2022-01-02'
				emp.flags.ignore_mandatory = True

				emp.birth_date_hijri = d.get('birth_date_h','')
				emp.moyser_employee_status=d.get('employee_status', '')
				emp.status = 'Inactive' #values_lookup[d.get('employee_status','')]
				emp.nid = nid

				employee_branch = d.get('branch_name', '')
				if employee_branch != '':
					emp.branch = self.check_link_data("Branch",employee_branch,'branch')
				
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
			<thead><tr><th>Employee No.</th><th>Name</th><th>Error</th></tr></thead>
			<tbody>{error_msgs}</tbody></table>'''
		frappe.msgprint(f"""
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
		{error_msgs}
		""",title=f'{len(data)} Employess Imported',indicator='Cs')
	

	@frappe.whitelist()
	def import_contracts(self,company_id):
		errors=0
		sucess=0
		exists=0

		values_lookup={
			'selfspouse1dep': 'Employee & Spouse',
			'travelticketsself': 'Employee Only',
			'selfspouse2dep': 'Family with 2 Dependant',
			'selfspouse3dep': 'Family with 3 Dependant',
			'no': 'No',
			'' : ''
		}
		
		if not company_id:
			company_id = frappe.conf.company_id or False
		
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
			if not frappe.db.exists("Employee Contract",{'nid':d.get('nid')}):
				contract = frappe.new_doc("Employee Contract")	
				### Info
				contract.hiring_start_date_g = d.get('hiring_start_date')###
				contract.commision = d.get('commision').capitalize()###
				contract.contract_type = d.get('contract_type').capitalize()###
				contract.vacation_period = d.get('vacation_period')###
				contract.contract_start_g = d.get('contract_start_date')###
				contract.commision_at_end_of_contract = d.get('commision_at_end_of_contract').capitalize()###
				contract.contract_status_section = d.get('contract_status')###
				contract.vacation_travel_tickets = values_lookup[d.get('vacation_travel_tickets')]###
				contract.contract_end_g = d.get('contract_end_date')###
				contract.commision_precentage = d.get('commision_precentage')###
				contract.leaves_consumer_balance = d.get('leaves_consumed_balance')###
				contract.over_time_included = d.get('over_time_included').capitalize()###
				contract.job_description_file = d.get('job_description_file')###
				contract.notes = d.get('notes')###
				contract.hiring_letter = d.get('hiring_letter')###

				### Contract Financial Details
				contract.basic_salary = d.get('basic_salary')###
				contract.allowance_transportations = d.get('allowance_trans').capitalize()###
				contract.allowance_housing = d.get('allowance_housing').capitalize()###
				contract.allowance_phone = d.get('allowance_phone').capitalize()###
				contract.nature_of_work_allowance = d.get('allowance_worknatural').capitalize()###
				contract.allowance_other = d.get('allowance_other').capitalize()###
				contract.allowance_feeding = d.get('allowance_living').capitalize()#$$$

				### Allowance Transportations
				contract.trans_start_date_g = d.get('allowance_trans_start_date')###
				contract.trans_end_date_g = d.get('allowance_trans_end_date')###
				contract.allowance_period = d.get('allowance_period')###
				if contract.allowance_period == 'One Time':
					contract.allowance_trans_schdl_1 == d.get('allowance_trans_schdl_1')
				elif contract.allowance_period == 'Two Time':
					contract.allowance_trans_schdl_1 == d.get('allowance_trans_schdl_1')
					contract.allowance_trans_schdl_2 == d.get('allowance_trans_schdl_2')
				contract.trans_amount_type = d.get('allowance_trans_amount_type').capitalize()###
				contract.trans_amount_value = d.get('allowance_trans_value')###

				### Allowance House
				contract.housing_start_g = d.get('allowance_housing_start_date')###
				contract.housing_end_date_g = d.get('allowance_housing_end_date')###
				contract.house_schdls = d.get('allowance_housing_schedule').capitalize()###
				if contract.house_schdls == 'One Time':
					contract.allowance_house_schdl_1 == d.get('allowance_housing_schdl_1')
				elif contract.house_schdls == 'Two Time':
					contract.allowance_house_schdl_1 == d.get('allowance_housing_schdl_1')
					contract.allowance_house_schdl_2 == d.get('allowance_housing_schdl_2')
				# contract.house_amount_type = d.get('allowance_housing_amount').capitalize()#$$$
				contract.house_amount_value = d.get('allowance_housing_value')###

				### Allowance Phone
				contract.phone_start_date_g = d.get('allowance_phone_start_date')###
				contract.phone_end_date_g = d.get('allowance_phone_end_date')###
				contract.phone_schdls = d.get('allowance_phone_schedule').capitalize()###
				if contract.phone_schdls == 'One Time':
					contract.allowance_phone_schdl_1 == d.get('allowance_phone_schdl_1')
				elif contract.phone_schdls == 'Two Time':
					contract.allowance_phone_schdl_1 == d.get('allowance_phone_schdl_1')
					contract.allowance_phone_schdl_2 == d.get('allowance_phone_schdl_2')
				contract.phone_amount_type = d.get('allowance_phone_amount_type').capitalize()###
				contract.phone_amount_value = d.get('allowance_phone_value')###

				### Allowance Natureow
				contract.natureow_start_date_g = d.get('allowance_worknatural_start_date')###
				contract.natureow_end_date_g = d.get('allowance_worknatural_end_date"')###
				contract.natureow_schdls = d.get('allowance_worknatural_schedule').capitalize()###
				if contract.natureow_schdls == 'One Time':
					contract.allowance_natow_schdl_1 == d.get('allowance_worknatural_schdl_1')
				elif contract.natureow_schdls == 'Two Time':
					contract.allowance_natow_schdl_1 == d.get('allowance_worknatural_schdl_1')
					contract.allowance_natow_schdl_2 == d.get('allowance_worknatural_schdl_2')
				contract.natureow_amount_type = d.get('allowance_worknatural_amount_type').capitalize()###
				contract.natureow_amount_value = d.get('allowance_worknatural_value')###

				### Allowance Feeding
				contract.feeding_start_date_g = d.get('allowance_living_start_date')#$$$
				contract.feeding_end_date_g = d.get('allowance_living_end_date')#$$$
				contract.feed_schdls = d.get('allowance_living_schedule').capitalize()#$$$
				if contract.feed_schdls == 'One Time':
					contract.allowance_feed_schdl_1 == d.get('allowance_living_schdl_1')
				elif contract.feed_schdls == 'Two Time':
					contract.allowance_feed_schdl_1 == d.get('allowance_living_schdl_1')
					contract.allowance_feed_schdl_2 == d.get('allowance_living_schdl_2')
				# contract.feed_amount_type = d.get('allowance_living_amount')#$$$
				contract.feed_amount_value = d.get('allowance_living_value')#$$$

				### Allowance Other
				contract.other_start_date_g = d.get('allowance_other_start_date')###
				contract.other_end_date_g = d.get('allowance_other_end_date')###
				contract.other_schdls = d.get('allowance_other_schedule').capitalize()###
				if contract.other_schdls == 'One Time':
					contract.allowance_other_schdl_1 == d.get('allowance_other_schdl_1')
				elif contract.other_schdls == 'Two Time':
					contract.allowance_other_schdl_1 == d.get('allowance_other_schdl_1')
					contract.allowance_other_schdl_2 == d.get('allowance_other_schdl_2')
				contract.other_amount_type = d.get('allowance_other_amount_type').capitalize()###
				contract.other_amount_value = d.get('allowance_other_value')###
				contract.from_api = 1
				contract.nid = d.get('nid')###
				contract.comment = d.get('comments')###


				employee_number = frappe.get_value("Employee",{'nid':contract.nid},'name')
				if employee_number != None:
					contract.save()
					sucess += 1
				else:
					errors += 1
			else:
				exists += 1 
		frappe.db.commit()

		frappe.msgprint(f"""
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
		""",title=f'{len(data)} Contracts Imported',indicator='Cs')
	

	@frappe.whitelist()
	def import_benefits(self,company_id):
		errors=0
		sucess=0
		exists=0
		data=[]

		lookup_value={
			"backPay": "Back Pay",
			"bonus": "Bonus",
			"businessTrip": "Business Trip",
			"OverTime": "Overtime",
			"commission": "Commission"

		}

		if not company_id:
			company_id = frappe.conf.company_id or False
		
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
			if not frappe.db.exists("Employee Benefits",{'nid':d.get('nid')}):
				benefits = frappe.new_doc("Employee Benefits")	
				benefits.date = d.get('date')
				benefits.addition_type = lookup_value[d.get('addition_type')]
				benefits.payroll_month = d.get('payroll_month')
				benefits.amount = d.get('amount')
				benefits.details = d.get('details')
				benefits.notes = d.get('notes')
				benefits.nid = d.get('nid')
				benefits.from_api = 1

				employee_number = frappe.get_value("Employee",{'nid':d.get('nid')},'name')
				print(d.get('nid'))
				if employee_number != None:
					benefits.save()
					sucess += 1
				else:
					errors += 1 
			else:
				exists +=1

		frappe.db.commit()

		frappe.msgprint(f"""
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
		""",title=f'{len(data)} Benefits Imported',indicator='Cs')


	def check_link_data(self,doctype,value,filed):
		exist = frappe.db.exists(doctype, value)
		if not exist:
			new_doc = frappe.new_doc(doctype)
			new_doc.update({
				f'{filed}': value
			})
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