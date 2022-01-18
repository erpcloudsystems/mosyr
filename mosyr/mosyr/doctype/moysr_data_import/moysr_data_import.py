# Copyright (c) 2022, AnvilERP and contributors
# For license information, please see license.txt

from cgitb import lookup
from operator import le
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

		self.table_status_imported(data,sucess,exists,errors,"Branches",False)


	def check_link_data(self,doctype,value,filed):
		""" Check if the records in the system
		if there is no value we creat a new value
		else return the name of the docype in the system

		doctype: Frappe Doctype Name
		value: record that we check
		field: field name in the doctype
		"""
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


	def table_status_imported(self,data,sucess,exists, errors,doctype_name,error_msgs = None, child_table=False):
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
		""",title=f'{len(data)} {doctype_name} Imported',indicator='Cs')

		return msg