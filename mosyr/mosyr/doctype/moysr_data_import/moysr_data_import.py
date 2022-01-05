# Copyright (c) 2022, AnvilERP and contributors
# For license information, please see license.txt

import frappe
import requests
from frappe.model.document import Document
from datetime import datetime


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
			if not frappe.db.exists("Branch",d['branch_name']):
				branch = frappe.new_doc("Branch")
				branch.branch=d['branch_name']
				branch.save()
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
			if not frappe.db.exists("Employee",d['employee_no']):
				emp = frappe.new_doc("Employee")
				emp.first_name = d['fullname_ar']
				emp.employee_number = d['employee_no']
				emp.status = values_lookup[d['employee_status']]
				emp.branch = d['branch_name']
				emp.salary_mode = 'Bank'
				emp.bank_name = d['Bank']	
				emp.date_of_birth = '2021-01-02'
				# emp.birth_date_h = d['birth_date_h']
				emp.current_address = d['employee_address']
				emp.bank_ac_no = d['IBAN']
				emp.birth_place = d['birth_place']
				emp.gender = d['gender']
				emp.handicap = d['handicap']
				emp.date_of_joining = '2022-01-02'
				# emp.designation = d['job_title']
				emp.marital_status = d['marital_status']
				emp.cell_number = d['mobile']
				emp.religion = d['religion']
				emp.nationality = d['nationality']
				print(values_lookup[d['employee_status']])
				print("______________________________________________________________")
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
		
