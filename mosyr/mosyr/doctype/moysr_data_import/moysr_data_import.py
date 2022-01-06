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
			if not frappe.db.exists("Employee",d['employee_no']):
				emp = frappe.new_doc("Employee")
				emp.first_name = d.get('fullname_ar','')
				emp.full_name_en = d.get('fullname_en','')
				emp.employee_number = d.get('employee_no','')
				emp.status = values_lookup[d.get('employee_status','')]
				emp.salary_mode = 'Bank'
				emp.bank_name = d.get('Bank','')
				emp.paymnet_type=d.get('payment_type','')
				emp.date_of_birth = d.get('birth_date_g') or '2021-01-02'
				emp.birth_date_hijri = d.get('birth_date_h','')
				emp.current_address = d.get('employee_address','')
				emp.bank_ac_no = d.get('IBAN','')
				emp.birth_place = d.get('birth_place','')
				emp.handicap = d.get('handicap','')
				emp.date_of_joining = '2022-01-02'
				emp.marital_status = d.get('marital_status','')
				emp.cell_number = d.get('mobile','')
				emp.religion = d.get('religion','')
				emp.nationality = d.get('nationality','')
				emp.health_insurance_no = d.get('insurance_card_number','')
				emp.nid	= d.get('nid','')
				emp.self_service = d.get('Self_service','')
				emp.moyser_employee_status=d.get('employee_status')

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
				emp.valid_data = 1

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
		""",title=f'{len(data)} Employess Imported',indicator='Cs')
		
	
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
				if len(v) == 1 or len(v) ==0:
					if v[0] == '':
						clear_data[f'{k}'] = ''
				else:
					clear_data[f'{k}'] = v
			else:
				clear_data[f'{k}'] = v
		return clear_data