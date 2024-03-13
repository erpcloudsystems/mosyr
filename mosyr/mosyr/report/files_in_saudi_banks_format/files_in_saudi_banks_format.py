# Copyright (c) 2022, AnvilERP and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from random import randint
import datetime
from six import string_types
import json
from frappe.desk.query_report import run,get_columns_dict,handle_duration_fieldtype_values,build_xlsx_data
from frappe.utils import cstr
from io import StringIO
from frappe.utils import flt
from mosyr.api import convert_date

@frappe.whitelist()
def export_query(date=frappe.utils.today()):
	"""export from query reports"""
	data = frappe._dict(frappe.local.form_dict)
	data.pop("cmd", None)
	data.pop("csrf_token", None)

	if isinstance(data.get("filters"), string_types):
		filters = json.loads(data["filters"])
	if data.get("report_name"):
		report_name = data["report_name"]
		frappe.permissions.can_export(
			frappe.get_cached_value("Report", report_name, "ref_doctype"),
			raise_exception=True,
		)
	
	file_format_type = data.get("file_format_type")
	custom_columns = frappe.parse_json(data.get("custom_columns", "[]"))
	include_indentation = data.get("include_indentation")
	visible_idx = data.get("visible_idx")

	if isinstance(visible_idx, string_types):
		visible_idx = json.loads(visible_idx)

	if file_format_type == "Excel":
		data = run(report_name, filters, custom_columns=custom_columns)
		data = frappe._dict(data)
		if not data.columns:
			frappe.respond_as_web_page(
				_("No data to export"),
				_("You can try changing the filters of your report."),
			)
			return
		columns = get_columns_dict(data.columns)
		from frappe.utils.xlsxutils import make_xlsx
		data["result"] = handle_duration_fieldtype_values(data.get("result"), data.get("columns"))
		xlsx_data, column_widths = build_xlsx_data(columns, data, visible_idx, include_indentation)
		xlsx_data.pop(0)
		xlsx_data[0][7] = (frappe.utils.getdate(date)).strftime("%d%m%Y")
		xlsx_file = make_xlsx(xlsx_data, "Query Report", column_widths=column_widths)
		bank = get_bank()[0]
		frappe.response["filename"] = bank + ".xlsx"
		frappe.response["filecontent"] = xlsx_file.getvalue()
		frappe.response["type"] = "binary"

	elif file_format_type == "Txt":
		data = run(report_name, filters, custom_columns=custom_columns)
		data = frappe._dict(data)
		if not data.columns:
			frappe.respond_as_web_page(
				_("No data to export"),
				_("You can try changing the filters of your report."),
			)
			return
		columns = get_columns_dict(data.columns)
		frappe.response["filename"] = report_name + ".txt"
		import csv
		from frappe.utils.xlsxutils import handle_html
		f = StringIO()
		writer = csv.writer(f)
		q=[]
		if get_bank()[0] == 'Al Rajhi Bank' and get_bank()[1] == "Payroll":
			doc = frappe.get_doc({
				'doctype': 'Rajhi',
				'rajhi_date': frappe.utils.today()
			})
			doc.insert(
				ignore_permissions=True,
				ignore_links=True,
				ignore_if_duplicate=True,
				ignore_mandatory=True 
			)
			file_name = doc.name[-2:]
			data["result"][0]['file_seq'] = file_name
		if get_bank()[0] == 'Al Rajhi Bank'and get_bank()[1] != "Payroll Cards":	
			company = frappe.get_doc("Company" , get_bank()[2])
			if company.calendar_accreditation == "Hijri":
				if company.disbursement_type == "Payroll":
					data["result"][0]['bank_acc_no'] = convert_date(frappe.utils.today()).replace("-" , "")
					data["result"][0]['emp_name'] = convert_date(date).replace("-" , "")
				elif company.disbursement_type == "Interchange":
					data["result"][0]['bank_acc_no'] = convert_date(frappe.utils.today()).replace("-" , "")
					data["result"][0]['emp_name'] = convert_date(date).replace("-" , "")
			else :
				data["result"][0]['bank_acc_no'] = frappe.utils.today().replace("-" , "")
				data["result"][0]['emp_name'] = date.replace("-" , "")
		if get_bank()[0] == 'Riyadh Bank' and get_bank()[1] == "WPS":
			company = frappe.get_doc("Company" , get_bank()[2])
			data["result"][0]['y'] = date.replace("-" , "")

			doc = frappe.get_doc({
				'doctype': 'Riyadh Bank',
				'today': frappe.utils.today()
			})
			doc.insert(
				ignore_permissions=True,
				ignore_links=True,
				ignore_if_duplicate=True,
				ignore_mandatory=True)
			file_name =  doc.name
			for d in data["result"]:
				if d.get('row_num_riad'):
					if d.get("riad_num") == 111:
						continue
					d.update({'row_num_riad':file_name + d.get('row_num_riad')})

		for n in data["result"]:
			if n.get('gross_pay'):
				del n['gross_pay']
			q.append(n.values())
		for r in q:
			# encode only unicode type strings and not int, floats etc.
			writer.writerow([handle_html(frappe.as_unicode(v)) if isinstance(v, str) else v for v in r])
		f.seek(0)
		res = cstr(f.read())
		frappe.response["result"] =  res.replace(",",'')
		frappe.response["type"] = "txt"
		bank = get_bank()[0]
		frappe.response["doctype"] = bank

@frappe.whitelist()
def get_bank():
	company = frappe.get_doc("Global Defaults").default_company
	bank_name = frappe.get_doc("Company" , company).bank_name
	disbursement_type = frappe.get_doc("Company" , company).disbursement_type
	return bank_name ,disbursement_type, company

def execute(filters=None):
	if not filters.get('company'): return [], []
	co = frappe.get_list("Company")
	if len(co)>0:
		company = frappe.get_doc("Company" , filters.get('company'))
		disbursement_type = company.disbursement_type
		bank_name = company.bank_name
		if bank_name == "Al Inma Bank" and disbursement_type == 'Payroll':
			return get_columns_inma_payroll(),get_data_inma_payroll(filters)
		elif bank_name == "Al Inma Bank" and disbursement_type == 'WPS':
			return get_columns_inma_wps(),get_data_inma_wps(filters)
		elif bank_name == "Riyadh Bank" and disbursement_type == 'WPS':
			return get_columns_riad(),get_data_riad(filters)
		elif bank_name == "The National Commercial Bank" and (disbursement_type == 'Payroll'):
			return get_columns_ahly(),get_data_ahly(filters)
		elif bank_name == "Samba Financial Group" and disbursement_type == 'WPS':
			return get_columns_sumba(),get_data_sumba(filters)
		elif bank_name == "Al Rajhi Bank" and disbursement_type == 'Payroll':
			return get_columns_alrajhi_payroll(),get_data_alrajhi_payroll(filters)
		elif bank_name == "Al Rajhi Bank" and disbursement_type == 'Interchange':
			return get_columns_alrajhi_interchange(),get_data_alrajhi_interchange(filters)
		elif bank_name == "Al Rajhi Bank" and disbursement_type == 'Payroll Cards':
			return get_columns_alrajhi_payroll_card(),get_data_alrajhi_payroll_card(filters)
		elif bank_name == "Al Araby Bank" and disbursement_type == 'WPS':
			return get_columns_alaraby(),get_data_alaraby(filters)
		else :
			return [] , []
	else :
		return [] , []

def get_data_inma_payroll(filters):
	condition='1=1 '
	if filters.get("month"):
		monthes = ['January','February','March','April','May','June','July','August','September','October','November','December']
		date = filters.get("month")
		if date in monthes:
			idx = monthes.index(date) + 1
			condition += f""" AND Month (sl.start_date)={idx}"""
	if(filters.get('bank')):condition += f" AND emp.employee_bank='{filters.get('bank')}'"
	if(filters.get('company')):condition += f" AND emp.company='{filters.get('company')}'"
	if(filters.get('year')):condition += f" AND year(sl.start_date) ='{filters.get('year')}'"
	data = frappe.db.sql(f"""
		SELECT
			1 as one1,
			emp.employee_number as emp_num,
			ROW_NUMBER() OVER (ORDER BY emp_num)  row_num ,
			IFNULL(emp.full_name_en , emp.first_name) as name,
			emp.bank_ac_no,
			'Yes' as yes,
			b.swift_number,
			'SA' as sa,
			sl.month_to_date,
			'SAR' as sar,
			1 as one2,
			'/PAYROLL/' as payrol,
			IF(emp.employee_bank="Al Inma Bank", 'BANK ACCOUNT', "SARIE") as inma,
			'' as id_number,
			emp.name as empname
		FROM `tabEmployee` emp  
		LEFT JOIN `tabSalary Slip` sl ON sl.employee=emp.name and sl.status='Submitted' 
		LEFT JOIN `tabBank` b ON b.name=emp.employee_bank
		WHERE emp.status ='Active' and  {condition}
		ORDER BY emp_num
		""",as_dict=1)
	company = filters.get('company') or frappe.get_doc("Global Defaults").default_company
	company = frappe.get_doc("Company" ,company)
	salary_slip_list = frappe.get_list("Salary Slip")
	if not salary_slip_list: return []
	salary=[]
	for d in data:
		id = ''
		employee = frappe.get_doc("Employee", d.get("empname"))
		if len(employee.identity):
			for identity in employee.identity:
				if identity.id_type == 'National ID':
					id = identity.id_number
		d.update({"id_number":id})
		del d['empname']
		salary.append(d.get("month_to_date"))
	total_salary = sum(salary)
	if not data: return []
	data.insert(0,
		{'one1': 0,
		'row_num': company.company_id,
		'emp_num': company.bank_account_number,
		'name':company.english_name_in_bank,
		'bank_ac_no':frappe.utils.getdate(frappe.utils.today()).strftime("%Y%m%d"),
		# 'yes':salary_slip.posting_date.strftime("%Y%m%d"),
		'swift_number':'',
		'sa':len(data),
		'month_to_date':total_salary,
		'sar':'SAR',
		})
	return data

def get_data_inma_wps(filters):
	condition='1=1 '
	if filters.get("month"):
		monthes = ['January','February','March','April','May','June','July','August','September','October','November','December']
		date = filters.get("month")
		if date in monthes:
			idx = monthes.index(date) + 1
			condition += f""" AND Month (sl.start_date)={idx}"""
	if(filters.get('bank')):condition += f" AND emp.employee_bank='{filters.get('bank')}'"
	if(filters.get('company')):condition += f" AND emp.company='{filters.get('company')}'"
	if(filters.get('year')):condition += f" AND year(sl.start_date) ='{filters.get('year')}'"
	data = frappe.db.sql(f"""
		SELECT
			1 as one1,
			emp.employee_number as emp_num,
			emp.name,
			ROW_NUMBER() OVER (ORDER BY emp_num)  row_num ,
			IFNULL(emp.full_name_en , emp.first_name) as name,
			emp.bank_ac_no,
			'Yes' as yes,
			b.swift_number,
			'SA' as sa,
			sl.month_to_date,
			IF(sl.gross_pay , sl.gross_pay,0) as gross_pay,
			'SAR' as sar,
			1 as one2,
			'/PAYROLL/' as payrol,
			IF(emp.employee_bank="Al Inma Bank", 'BANK ACCOUNT', "SARIE") as inma,
			'' as id_number,
			emp.name as empname,
			IF(sd.amount , sd.amount,0) as basic,
			IF(sde.amount , sde.amount,0) as housing_allowance,
			IF(sade.amount , sade.amount,0) as allowance_trans,
			sl.total_deduction as dedactions
		FROM `tabEmployee` emp  
		LEFT JOIN `tabSalary Slip` sl ON sl.employee=emp.name and sl.status='Submitted'
		LEFT JOIN `tabBank` b ON b.name=emp.employee_bank
		LEFT JOIN `tabSalary Detail` sd ON sd.parent=sl.name and sd.salary_component="Basic"
		LEFT JOIN `tabSalary Detail` sde ON sde.parent=sl.name and sde.salary_component="Allowance Housing"
		LEFT JOIN `tabSalary Detail` sade ON sade.parent=sl.name and sade.salary_component="Allowance Trans"
		WHERE emp.status ='Active' and {condition}
		GROUP BY emp.name
		ORDER BY emp_num
		""",as_dict=1)
	# for d in data:
	# 	other_earnings = d.get("gross_pay" or 0) - d.get("basic" or 0) - d.get("housing_allowance" or 0)
	# 	d.update({"other_earnings":other_earnings})
	company = filters.get('company') or frappe.get_doc("Global Defaults").default_company
	company = frappe.get_doc("Company" ,company)
	salary_slip_list = frappe.get_list("Salary Slip")
	if not salary_slip_list: return []
	salary=[]
	for d in data:
		id = ''
		employee = frappe.get_doc("Employee", d.get("empname"))
		if len(employee.identity):
			for identity in employee.identity:
				if identity.id_type == 'National ID':
					id = identity.id_number
		d.update({"id_number":id})
		del d['empname']
		salary.append(d.get("month_to_date"))
	total_salary = sum(salary)
	if not data: return []
	for d in data:
		if d.get("basic") == 0:
			d.update({"basic":"0"})
		if d.get("housing_allowance") == 0:
			d.update({"housing_allowance":"0"})
		if d.get("allowance_trans") == 0:
			d.update({"allowance_trans":"0"})
		if d.get("dedactions") == 0:
			d.update({"dedactions":"0"})
	data.insert(0,
		{'one1': "WPS",
		'row_num': company.company_id,
		'emp_num': company.bank_account_number,
		'name':company.english_name_in_bank,
		'bank_ac_no':frappe.utils.getdate(frappe.utils.today()).strftime("%Y%m%d"),
		# 'yes':salary_slip.posting_date.strftime("%Y%m%d"),
		'swift_number':'',
		'sa':len(data),
		'month_to_date':total_salary,
		'sar':'SAR',
		'one2': company.labors_office_file_number
		})
	return data

def get_data_riad(filters):
	condition='1=1 '
	if filters.get("month"):
		monthes = ['January','February','March','April','May','June','July','August','September','October','November','December']
		date = filters.get("month")
		if date in monthes:
			idx = monthes.index(date) + 1
			condition += f""" AND Month (sl.start_date)={idx}"""
	if(filters.get('bank')):condition += f" AND emp.employee_bank='{filters.get('bank')}'"
	if(filters.get('company')):condition += f" AND emp.company='{filters.get('company')}'"
	if(filters.get('year')):condition += f" AND year(sl.start_date) ='{filters.get('year')}'"
	company = filters.get('company') or frappe.get_doc("Global Defaults").default_company
	agreement_symbol = frappe.get_value("Company" , company , 'agreement_symbol') or '0'
	num = ""
	for c in agreement_symbol:
		if c.isdigit():
			num = num + c
	data = frappe.db.sql(f"""
		SELECT
			'112' as riad_num,
			LPAD(emp.employee_number, 6, 0) as emp_num,
			'Y' as y,
			LPAD({num}, 5, 0) as agreament_s,
			LPAD(ROW_NUMBER() OVER (ORDER BY emp_num) + 00000 ,5,'0') row_num_riad,
			'' AS id_number_riad ,
			' ' as spaces13,
			LPAD(emp.bank_ac_no, 24, 0) as bank_acc_riad,
			' ' as sar_header,
			LPAD(FORMAT(sl.month_to_date,2), 16, 0 ) as salary,
			'SAR' as sar,
			' ' as spaces239,
			RPAD(emp.first_name,50,' ') as emp_name,
			' ' as spaces90,
			IFNULL(RPAD(emp.full_name_en,50,' ') , RPAD(emp.first_name,50,' ') ) as emp_name,
			RPAD(b.swift_number,11, ' ') as emp_bank,
			' ' as spaces129,
			IF(sl.gross_pay , sl.gross_pay,0) as gross_pay,
			LPAD(FORMAT(sd.amount,2),13,0) as basic,
			LPAD(FORMAT(sde.amount,2),12,0) as housing_allowance,
			"0" as other_earnings,
			LPAD(FORMAT(sl.total_deduction,2),13 ,0) as dedactions,
			' ' as spaces33,
			emp.name as empname
		FROM `tabEmployee` emp  
		LEFT JOIN `tabSalary Slip` sl ON sl.employee=emp.name and sl.status='Submitted' 
		LEFT JOIN `tabBank` b ON b.name=emp.employee_bank
		LEFT JOIN `tabSalary Detail` sd ON sd.parent=sl.name and sd.salary_component="Basic"
		LEFT JOIN `tabSalary Detail` sde ON sde.parent=sl.name and sde.salary_component="Allowance Housing"
		WHERE emp.status ='Active' and {condition}
		Group BY emp.name
		ORDER BY emp_num
		""",as_dict=1)
	for d in data:
		id = '0000000000'
		employee = frappe.get_doc("Employee", d.get("empname"))
		if len(employee.identity):
			for identity in employee.identity:
				if identity.id_type == 'National ID':
					id = identity.id_number
			id = str(id).zfill(10)
		d.update({"id_number_riad":id})
		del d['empname']
		other_earnings = flt(d.get("gross_pay" or '0')) - flt(d.get("basic" or '0')) - flt(d.get("housing_allowance" or '0'))
		other_earnings = "%.2f" % other_earnings
		d.update({"other_earnings":(str(other_earnings).zfill(12))})
	if not data: return []
	if not data[0].get("emp_name"): return []
	salary_slip_list = frappe.get_list("Salary Slip")
	if not salary_slip_list: return []
	salary=[]
	for d in data:
		salary.append(flt(d.get("salary")))
	total_salary = sum(salary)
	for d in data :
		d.update({'spaces13':' ' * 13})
		d.update({'sar_header':' ' * 10})
		d.update({'spaces239':' ' * 239})
		d.update({'spaces90':' ' * 90})
		d.update({'spaces129':' ' * 129})
		d.update({'spaces33':' ' * 33})
		if d.get('salary', False):
			sl_total = d.get('salary').replace(',','')
			d.update({'salary':sl_total})
		if d.get('basic', False):
			sl_basic =  d.get('basic').replace(',','')
			d.update({'basic':sl_basic})
		if d.get('housing_allowance', False):
			sl_housing_allowance =  d.get('housing_allowance').replace(',','')
			d.update({'housing_allowance':sl_housing_allowance})
		if d.get('other_earnings' ,0):
			sl_other_earnings =  str(d.get('other_earnings')).replace(',','')
			d.update({'other_earnings':sl_other_earnings})
		if d.get('dedactions', False):
			sl_dedactions =  d.get('dedactions').replace(',','')
			d.update({'dedactions':sl_dedactions})

	company = frappe.get_doc("Company" ,company)
	

	if company.labors_office_file_number:
		labors_office_file_number = (company.labors_office_file_number).zfill(9)
	else :
		labors_office_file_number = 000000000
	for d in data:
		if not d.get("basic"):
			d.update({"basic":"000000000.00"})
		if not d.get("housing_allowance"):
			d.update({"housing_allowance":"000000000.00"})
		if not d.get("other_earnings"):
			d.update({"other_earnings":"000000000.00"})
		if not d.get("dedactions"):
			d.update({"dedactions":"000000000.00"})
	data.append(
		{
			'riad_num':999,
			'emp_num':(str("%.2f" % total_salary).zfill(18)),
			'y':(str(len(data)).zfill(6))
		}
	)
	if company.establishment_number:
		establishment_number = (str(company.establishment_number).zfill(9))
	else :
		establishment_number = (str('').zfill(9))

	if company.bank_account_number:
		bank_account_number = (str(company.bank_account_number).zfill(13))
	else :
		bank_account_number = (str(' ').zfill(13))
	data.insert(0,
		{
		'riad_num':  111,
		'emp_num' : company.agreement_symbol,
		'y':frappe.utils.today(),
		'agreament_s':'PAYROLLREF-PR-0001-'+ str(randint(100, 10000000000000000)),
		'row_num_riad' :establishment_number,
		'id_number_riad':"RIBL",
		'spaces13': bank_account_number,
		'bank_acc_riad' : ' ' * 11 , # 11 spaces
		'sar_header' : 'SAR',
		'salary':company.labors_office_file_number,
		'sar':' ' * 9  # 9 spaces
		})

	return data

def get_data_ahly(filters):
	condition='1=1 '
	if filters.get("month"):
		monthes = ['January','February','March','April','May','June','July','August','September','October','November','December']
		date = filters.get("month")
		if date in monthes:
			idx = monthes.index(date) + 1
			condition += f""" AND Month (sl.start_date)={idx}"""
	if(filters.get('bank')):condition += f" AND emp.employee_bank='{filters.get('bank')}'"
	if(filters.get('company')):condition += f" AND emp.company='{filters.get('company')}'"
	if(filters.get('year')):condition += f" AND year(sl.start_date) ='{filters.get('year')}'"
	data = frappe.db.sql(f"""
		SELECT
			b.swift_number as emp_bank_ahly,
			emp.bank_ac_no as bank_acc_ahly,
			sl.month_to_date as salary_ahly,
			LPAD(MONTHNAME(sl.start_date),3) AS Month,
			IFNULL(emp.full_name_en , emp.first_name) as emp_name,
			'' as id_number,
			emp.permanent_address ,
			emp.name as empname
		FROM `tabEmployee` emp  
		LEFT JOIN `tabSalary Slip` sl ON sl.employee=emp.name and sl.status='Submitted' 
		LEFT JOIN `tabBank` b ON b.name=emp.employee_bank
		WHERE emp.status ='Active' and {condition}
		""",as_dict=1)
	for d in data:
		id = ''
		employee = frappe.get_doc("Employee", d.get("empname"))
		if len(employee.identity):
			for identity in employee.identity:
				if identity.id_type == 'National ID':
					id = identity.id_number
		d.update({"id_number":id})
		del d['empname']
	return data

def get_data_sumba(filters):
	today = datetime.date.today()
	condition='1=1 '
	if filters.get("month"):
		monthes = ['January','February','March','April','May','June','July','August','September','October','November','December']
		date = filters.get("month")
		if date in monthes:
			idx = monthes.index(date) + 1
			condition += f""" AND Month (sl.start_date)={idx}"""
	if(filters.get('bank')):condition += f" AND emp.employee_bank='{filters.get('bank')}'"
	if(filters.get('company')):condition += f" AND emp.company='{filters.get('company')}'"
	if(filters.get('year')):condition += f" AND year(sl.start_date) ='{filters.get('year')}'"
	company = filters.get('company') or frappe.get_doc("Global Defaults").default_company
	company = frappe.get_doc("Company" ,company)

	def _samba_wps_checksum(myCompanyCode, mySid, myXname, myXamount) :
		CmpyCode = myCompanyCode
		AP1 = int(str(CmpyCode)[:1]) * 27
		AP2 = int(str(CmpyCode)[1:2]) * 26
		AP3 = int(str(CmpyCode)[2:3]) * 25
		AP4 = int(str(CmpyCode)[3:4]) * 24
		AP5 = int(str(CmpyCode)[4:5]) * 23
		AP6 = AP1 + AP2 + AP3 + AP4 + AP5
		Fld03 = mySid

		BP1 = int(str(Fld03)[:1])  * 22
		BP2 = int(str(Fld03)[1:2])  * 21
		BP3 = int(str(Fld03)[2:3])  * 20
		BP4 = int(str(Fld03)[3:4])  * 19
		BP5 = int(str(Fld03)[4:5])  * 18
		BP6 = int(str(Fld03)[5:6])  * 17
		BP7 = int(str(Fld03)[6:7])  * 16
		BP8 = int(str(Fld03)[7:8])  * 15
		BP9 = int(str(Fld03)[8:9])  * 14
		BP10 = int(str(Fld03)[9:10])  * 13
		BP11 = BP1 + BP2 + BP3 + BP4 + BP5 + BP6 + BP7 + BP8 + BP9 + BP10

		Fld06 = myXname
		ArAlp1 = "ABCDEFGHIJKLMNOPQRSTUVWXYZ "
		ArAlp2 = Fld06[0:0 + 1]
		CP1 = ArAlp1.find(ArAlp2) + 1
		if CP1==0:CP1+=1
		ArAlp3 = Fld06[10:10 + 1]
		CP2 = ArAlp1.find(ArAlp3) + 1
		ArAlp4 = Fld06[20:20 + 1]
		CP3 = ArAlp1.find(ArAlp4) + 1
		CPP1 = CP1 * 12
		CPP2 = CP2 * 11
		CPP3 = CP3 * 10
		CP4 = CPP1 + CPP2 + CPP3
		AmtFld7 = str(myXamount)
		DP1 = int(str(AmtFld7)[:1]) * 9
		DP2 = int(str(AmtFld7)[1:2]) * 8
		DP3 = int(str(AmtFld7)[2:3]) * 7
		DP4 = int(str(AmtFld7)[3:4]) * 6
		DP5 = int(str(AmtFld7)[4:5]) * 5
		DP6 = int(str(AmtFld7)[5:6]) * 4
		DP7 = int(str(AmtFld7)[6:7]) * 3
		DP8 = int(str(AmtFld7)[7:8]) * 2
		# DP9 = int(str(AmtFld7)[8:9]) * 1
		DP10 = DP1 + DP2 + DP3 + DP4 + DP5 + DP6 + DP7 + DP8 
		# + DP9
		ChkTot = AP6 + BP11 + CP4 + DP10
		ChkTot1 = int(ChkTot/97)
		ChkTot2 = 97 * ChkTot1
		ChkTot3 = int(ChkTot) - ChkTot2
		ChkTot4 = 97 - ChkTot3
		DOCHICKUP = str(ChkTot4).zfill(2)
		#00
		return DOCHICKUP
	data = frappe.db.sql(f"""
		SELECT
			'00207' as num,
			LPAD(emp.employee_number,12,0) as emp_num,
			IFNULL(RPAD(emp.full_name_en,45,' ') , RPAD(emp.first_name,45,' ') ) as emp_name,
			LPAD(FORMAT(sl.month_to_date,2),13,0) as salary,
			NULL as checksum,
			LPAD(b.swift_number,4,' ') as emp_bank,
			LPAD(emp.bank_ac_no,24,0) as bank_acc_no,
			'00000000000' as zero,
			IF(iden.nationality="Saudi", '1', "2") as nationality ,
			' ' as id_number,
			LPAD(emp.departement_location, 20 ,' ') as departement_location,
			' ' as spaces19,
			IF(sl.gross_pay , sl.gross_pay,0) as gross_pay,
			LPAD(FORMAT(sd.amount,2), 13 , 0) as basic,
			LPAD(FORMAT(sde.amount ,2) , 12 , 0) as housing_allowance,
			LPAD(FORMAT('0' ,2) , 12 , 0) as other_earnings,
			LPAD(FORMAT(sl.total_deduction,2), 13 , 0)  as dedactions,
			emp.name as name
		FROM `tabEmployee` emp
		LEFT JOIN `tabSalary Slip` sl ON sl.employee=emp.name and sl.status='Submitted' 
		LEFT JOIN `tabBank` b ON b.name=emp.employee_bank
		LEFT JOIN `tabIdentity` iden ON iden.parent=emp.name
		LEFT JOIN `tabSalary Detail` sd ON sd.parent=sl.name and sd.salary_component="Basic"
		LEFT JOIN `tabSalary Detail` sde ON sde.parent=sl.name and sde.salary_component="Allowance Housing"
		WHERE emp.status ='Active' and  {condition}
		Group BY emp.name
		ORDER BY emp_num
		""",as_dict=1)
	for d in data:
		id = '0000000000'
		employee = frappe.get_doc("Employee", d.get("name"))
		if len(employee.identity):
			for identity in employee.identity:
				if identity.id_type == 'National ID':
					id = identity.id_number
			id = str(id).zfill(10)
		d.update({"id_number":id})
	salary_total = []
	for d in data:
		salary_total.append(flt(d.get("salary")))

	company = filters.get('company') or frappe.get_doc("Global Defaults").default_company
	salary_slip_list = frappe.get_list("Salary Slip")
	if not salary_slip_list: return []
	total_salary = sum(salary_total)
	if not company: return []
	company = frappe.get_doc("Company", company)
	for d in data:
		if not d.get("departement_location"):d.update({"departement_location": ' ' *20})
		del d['name']
		other_earnings = flt(d.get("gross_pay" or '0')) - flt(d.get("basic" or '0')) - flt(d.get("housing_allowance" or '0'))
		d.update({"other_earnings":(str(("%.2f" % other_earnings)).zfill(12))})
		sl_other_earnings =  d.get('other_earnings').replace(',','').replace('.','')
		d.update({'other_earnings':sl_other_earnings})
		d.update({'spaces19':' ' * 19})
		if d.get('salary', False):
			salary = d.get('salary').replace(',','').split('.')[0][1:]
		else :salary = d.get('salary').split('.')[0][1:]
		checksum =_samba_wps_checksum(company.company_id,d.get('id_number'),d.get('emp_name'),salary)
		d.update({'checksum':checksum})
		if d.get('salary', False):
			sl_total = d.get('salary').replace(',','').replace('.','')
			d.update({'salary':sl_total})
		if d.get('basic', False):
			sl_basic =  d.get('basic').replace(',','').replace('.','')
			d.update({'basic':sl_basic})
		else :d.update({'basic':'00000000000'})
		if d.get('housing_allowance', False):
			sl_housing_allowance =  d.get('housing_allowance').replace(',','').replace('.','')
			d.update({'housing_allowance':sl_housing_allowance})
		else :d.update({'housing_allowance':'00000000000'})
		if d.get('dedactions', False):
			sl_dedactions =  d.get('dedactions').replace(',','').replace('.','')
			d.update({'dedactions':sl_dedactions})
		else :d.update({'dedactions':'00000000000'})
	if company.organization_english:
		organization_english = company.organization_english.ljust(40)
	else:
		organization_english = ' ' * 40
	if not data: return []

	data.append(
		{
			'num':'003',
			'emp_num':str(len(data)).zfill(6),
			'emp_name':str("%.2f" % total_salary).zfill(18).replace(',','').replace('.',''),
			'salary':' ' * 181  # 181 spaces
		}
	)
	data.insert(0,
		{
		'num': '0011',
		'emp_num' : str(today.month).zfill(2),
		'emp_name' : str(today.day).zfill(2),
		'salary':today.strftime("%Y%m%d"),
		'checksum':organization_english,
		'emp_bank' : company.company_id.ljust(152)
		})
	return data

def get_data_alrajhi_payroll(filters):
	condition='1=1 '
	if filters.get("month"):
		monthes = ['January', 'February', 'March', 'April','May', 'June', 'July', 'August', 'September', 'October', 'November','December']
		date = filters.get("month")
		if date in monthes:
			idx = monthes.index(date) + 1
			condition += f""" AND Month (sl.start_date)={idx}"""
	if(filters.get('bank')):condition += f" AND emp.employee_bank='{filters.get('bank')}'"
	if(filters.get('company')):condition += f" AND emp.company='{filters.get('company')}'"
	if(filters.get('year')):condition += f" AND year(sl.start_date) ='{filters.get('year')}'"
	data = frappe.db.sql(f"""
		SELECT
			LPAD(emp.employee_number,12,0) as emp_num,
			LPAD(b.swift_number , 4,' ') as bank_code,
			LPAD(emp.bank_ac_no,24,0) as bank_acc_no,
			RPAD(emp.full_name_en ,50 ,' ') as emp_name,
			IFNULL(RPAD(emp.full_name_en,50,' ') , RPAD(emp.first_name,50,' ') ) as emp_name,
			LPAD(FORMAT(sl.month_to_date,2) , 17, 0) as salary,
			'' as id_number,
			'0' as zero,
			' ' as onespace,
			emp.name as empname
		FROM `tabEmployee` emp  
		LEFT JOIN `tabSalary Slip` sl ON sl.employee=emp.name and sl.status='Submitted' 
		LEFT JOIN `tabBank` b ON b.name=emp.employee_bank
		WHERE emp.status ='Active' and {condition}
		ORDER BY emp_num
		""",as_dict=1)
	salary=[]
	for d in data :
		d.update({"onespace" : " " * 14})
		salary.append(flt(d.get("salary")))
		if d.get('salary', False):
			sl_total = d.get('salary').replace(',','').replace('.','')
			d.update({'salary':sl_total})
	default_company = filters.get('company') or frappe.get_doc("Global Defaults").default_company
	company = frappe.get_doc("Company" ,default_company)
	salary_slip_list = frappe.get_list("Salary Slip")
	if not salary_slip_list: return []
	total_salary = sum(salary)
	cal = ''
	if company.calendar_accreditation == 'Gregorian': cal = 'G'
	if company.calendar_accreditation == 'Hijri': cal = 'H'

	# get hour now
	date=datetime.datetime.now()
	if date.hour <= 14:
		today =  datetime.date.today()
	elif date.hour > 14:
		today = datetime.date.today() + datetime.timedelta(days=1)

	if (str("%.2f" % total_salary).zfill(16)): 
		salary=(str("%.2f" % total_salary).zfill(16)).replace(',','').replace('.','')
	else:
		salary=(str("%.2f" % total_salary).zfill(16))
	if not data: return []
	if company.bank_account_number:
		bank_account_number = (str(company.bank_account_number).zfill(15))
	else :
		bank_account_number = (str('').zfill(15))
	for d in data:
		id = '000000000000000'
		employee = frappe.get_doc("Employee", d.get("empname"))
		if len(employee.identity):
			for identity in employee.identity:
				if identity.id_type == 'National ID':
					id = identity.id_number
			id = str(id).zfill(15)
		d.update({"id_number":id})
		del d['empname']
	data.insert(0,
		{
		'emp_num': '000000000000',
		'bank_code' : cal,
		# 'bank_acc_no' : today.strftime("%Y%m%d"),
		'bank_acc_no' : frappe.utils.today(),
		'emp_name': '0',
		'salary':salary,
		'id_number' : str(len(data)).zfill(8),
		"zero":bank_account_number,
		"onespace" :" ",
		"space65":" " * 65 ,
		})
	return data

def get_data_alrajhi_interchange(filters):
	condition='1=1 '
	if filters.get("month"):
		monthes = ['January', 'February', 'March', 'April','May', 'June', 'July', 'August', 'September', 'October', 'November','December']
		date = filters.get("month")
		if date in monthes:
			idx = monthes.index(date) + 1
			condition += f""" AND Month (sl.start_date)={idx}"""
	if(filters.get('bank')):condition += f" AND emp.employee_bank='{filters.get('bank')}'"
	if(filters.get('company')):condition += f" AND emp.company='{filters.get('company')}'"
	if(filters.get('year')):condition += f" AND year(sl.start_date) ='{filters.get('year')}'"
	data = frappe.db.sql(f"""
		SELECT
			LPAD(emp.employee_number,12,0) as emp_num,
			LPAD(b.swift_number,4,' ') as bank_code,
			RPAD(emp.bank_ac_no,24,' ') as bank_acc_no,
			IFNULL(LPAD(emp.full_name_en,50,' ') , LPAD(emp.first_name,50,' ') ) as emp_name,
			LPAD(FORMAT(sl.month_to_date,2),17,0) as salary,
			'' as id_number,
			'0' as zero,
			'000' as zero3,
			' ' as  i,
			emp.name as empname
		FROM `tabEmployee` emp  
		LEFT JOIN `tabSalary Slip` sl ON sl.employee=emp.name and sl.status='Submitted' 
		LEFT JOIN `tabBank` b ON b.name=emp.employee_bank
		WHERE emp.status ='Active' and  {condition}
		ORDER BY emp_num
		""",as_dict=1)
	salary=[]
	for d in data:
		id = '000000000000000'
		employee = frappe.get_doc("Employee", d.get("empname"))
		if len(employee.identity):
			for identity in employee.identity:
				if identity.id_type == 'National ID':
					id = identity.id_number
			id = str(id).zfill(15)
		d.update({"id_number":id})
		del d['empname']
		salary.append(flt(d.get("salary")))
		d.update({'i': ' ' * 11 })
		if  d.get('salary', False):
			sl_total = d.get('salary').replace(',','').replace('.','')
			d.update({'salary':sl_total})
	default_company = filters.get('company') or frappe.get_doc("Global Defaults").default_company
	company = frappe.get_doc("Company" ,default_company)
	salary_slip_list = frappe.get_list("Salary Slip")
	if not salary_slip_list: return []
	# get total salary
	salary_slip = frappe.get_last_doc("Salary Slip",filters={'company':default_company,'docstatus':1}) 
	total_salary = sum(salary)
	cal = ''
	if company.calendar_accreditation == 'Gregorian': cal = 'G' 
	if company.calendar_accreditation == 'Hijri': cal = 'H' 

	# get hour now
	date=datetime.datetime.now()
	if date.hour < 14:
		today =  datetime.date.today()
	elif date.hour >= 14:
		today = datetime.date.today() + datetime.timedelta(days=1)
		if today.strftime("%A") == 'Friday' :
			today = datetime.date.today() + datetime.timedelta(days=2)
		elif today.strftime("%A") == 'Saturday':
			today = datetime.today() + datetime.timedelta(days=1)
	if (str("%.2f" % total_salary).zfill(16)): 
		salary=(str("%.2f" % total_salary).zfill(16)).replace(',','').replace('.','')
	else:
		salary=(str("%.2f" % total_salary).zfill(16))
	if not data: return []
	if company.bank_account_number:
		bank_account_number = (str(company.bank_account_number).zfill(15))
	else :
		bank_account_number = (' ' *15)
	data.insert(0,
		{
		'emp_num': '000000000000',
		'bank_code' : cal,
		'bank_acc_no' : today,
		'emp_name': '0',
		'salary':salary,
		'id_number' : str(len(data)).zfill(8),
		"zero":bank_account_number,
		"zero3":" " * 67,
		"i":"I",
		})
	return data

def get_data_alrajhi_payroll_card(filters):
	condition='1=1 '
	if filters.get("month"):
		monthes = ['January', 'February', 'March', 'April','May', 'June', 'July', 'August', 'September', 'October', 'November','December']
		date = filters.get("month")
		if date in monthes:
			idx = monthes.index(date) + 1
			condition += f""" AND Month (sl.start_date)={idx}"""
	if(filters.get('bank')):condition += f" AND emp.employee_bank='{filters.get('bank')}'"
	if(filters.get('company')):condition += f" AND emp.company='{filters.get('company')}'"
	if(filters.get('year')):condition += f" AND year(sl.start_date) ='{filters.get('year')}'"
	today=datetime.datetime.today().strftime('%Y%m%d')
	data = frappe.db.sql(f"""
		SELECT
			LPAD(emp.employee_number,12,0) as emp_num,
			'00000' as zero5,
			IFNULL(LPAD(emp.payroll_card_number,19,0),'0000000000000000000') as payroll_card_number,
			IFNULL(RPAD(emp.full_name_en,50,' ') ,
			RPAD(emp.first_name,50,' ') ) as emp_name,
			'' AS id_number_rajhi,
			LPAD(FORMAT(sl.month_to_date,2), 17, 0 )as salary,
			IF(sl.gross_pay , sl.gross_pay,0) as gross_pay,
			{today} as date,
			'2' as op_type,
			'000000' as zero6,
			' ' as spaces10,
			CASE WHEN emp.cell_number <> '' THEN LPAD(emp.cell_number,10,0)
			ELSE '0000000000'
			END AS phone,
			LPAD(FORMAT(sd.amount, 2),14,0) as basic ,
			IFNULL(LPAD(FORMAT(sde.amount, 2),14,0) , '00000000000.00' ) as housing_allowance,
			'0' as other_earnings,
			LPAD(FORMAT(sl.total_deduction, 2),14,0) as dedactions,
			emp.name as empname
		FROM `tabEmployee` emp  
		LEFT JOIN `tabSalary Slip` sl ON sl.employee=emp.name and sl.status='Submitted' 
		LEFT JOIN `tabSalary Detail` sd ON sd.parent=sl.name and sd.salary_component="Basic"
		LEFT JOIN `tabSalary Detail` sde ON sde.parent=sl.name and sde.salary_component="Allowance Housing"
		WHERE emp.status ='Active' and  {condition}
		Group BY emp.name
		ORDER BY emp_num
		""",as_dict=1)
	for d in data:
		id = '0000000000'
		employee = frappe.get_doc("Employee", d.get("empname"))
		if len(employee.identity):
			for identity in employee.identity:
				if identity.id_type == 'National ID':
					id = identity.id_number
			id = str(id).zfill(10)
		d.update({"id_number_rajhi":id})
		del d['empname']
		d.update({"spaces10": ' ' * 10 })
		other_earnings = flt(d.get("gross_pay" or '0')) - flt(d.get("basic" or '0')) - flt(d.get("housing_allowance" or '0'))
		other_earnings = "%.2f" % other_earnings
		d.update({"other_earnings":(str(other_earnings).zfill(12))})
		if d.get('salary', False):
			sl_total = d.get('salary').replace(',','').replace('.','')
			d.update({'salary':sl_total})
		if d.get('basic', False):
			sl_basic =  d.get('basic').replace(',','').replace('.','')
			d.update({'basic':sl_basic})
		if d.get('housing_allowance', False):
			sl_housing_allowance =  d.get('housing_allowance').replace(',','').replace('.','')
			d.update({'housing_allowance':sl_housing_allowance})
		if d.get('other_earnings', False):
			sl_other_earnings =  d.get('other_earnings').replace(',','').replace('.','')
			d.update({'other_earnings':sl_other_earnings})
		if d.get('dedactions', False):
			sl_dedactions =  d.get('dedactions').replace(',','').replace('.','')
			d.update({'dedactions':sl_dedactions})
		
	return data

def get_data_alaraby(filters):
	if not filters.get("month"):return []
	condition='1=1 '
	monthes = ['January', 'February', 'March', 'April','May', 'June', 'July', 'August', 'September', 'October', 'November','December']
	date = filters.get("month")
	if date in monthes:
		idx = monthes.index(date) + 1
		condition += f""" AND Month (sl.start_date)={idx}"""
	if(filters.get('bank')):condition += f" AND emp.employee_bank='{filters.get('bank')}'"
	if(filters.get('company')):condition += f" AND emp.company='{filters.get('company')}'"
	if(filters.get('year')):condition += f" AND year(sl.start_date) ='{filters.get('year')}'"
	year = filters.get("year")
	month = filters.get("month")
	data = frappe.db.sql(f"""
		SELECT
			'D' as d,
			sl.month_to_date,
			IF(sl.gross_pay , sl.gross_pay,0) as gross_pay,
			emp.bank_ac_no,
			IFNULL(emp.full_name_en , emp.first_name) as first_name,
			b.swift_number as swift_number,
			"salaries for {month} {year}" as month,
			IF(sd.amount , sd.amount,0) as basic,
			IF(sde.amount , sde.amount,0) as housing_allowance,
			0 as other_earnings,
			sl.total_deduction as dedactions,
			'' as id_number,
			null as co_number,
			emp.name as empname
		FROM `tabEmployee` emp
		LEFT JOIN `tabSalary Slip` sl ON sl.employee=emp.name and sl.status='Submitted' 
		LEFT JOIN `tabBank` b ON b.name=emp.employee_bank
		LEFT JOIN `tabSalary Detail` sd ON sd.parent=sl.name and sd.salary_component="Basic"
		LEFT JOIN `tabSalary Detail` sde ON sde.parent=sl.name and sde.salary_component="Allowance Housing"
		WHERE emp.status ='Active' and {condition}
		Group BY emp.name
		""",as_dict=1)
	for d in data:
		other_earnings = d.get("gross_pay" or 0) - d.get("basic" or 0) - d.get("housing_allowance" or 0)
		d.update({"other_earnings":other_earnings})
	default_company = filters.get('company') or frappe.get_doc("Global Defaults").default_company
	company = frappe.get_doc("Company" ,default_company)
	salary=[]
	for d in data:
		salary.append(flt(d.get("month_to_date")))
	total_salary=sum(salary)
	if not data: return []
	today =  datetime.date.today()
	
	for d in data:
		id = ''
		employee = frappe.get_doc("Employee", d.get("empname"))
		if len(employee.identity):
			for identity in employee.identity:
				id = identity.id_number
		d.update({"id_number":id})
		del d['empname']
	data.insert(0,
		{'d': 'H',
		'month_to_date': "ARNB",
		'bank_ac_no': company.agreement_number_for_customer,
		'first_name':"N",
		'swift_number':today.strftime("%d%m%Y") + ".EX1",
		'month':company.bank_account_number,
		'basic':"SAR",
		'housing_allowance': '0',
		'other_earnings' :total_salary,
		'dedactions':today.strftime("%d%m%Y"),
		'id_number':company.company_id,
		'co_number':f"salaries for {month} {year}"
		})
	return data

def get_columns_inma_payroll():
		return [
				{
					
					"fieldname": "one1",
					"fieldtype": "Data",
					"width": 10,
				},
				{
					
					"fieldname": "row_num",
					"fieldtype": "Data",
					"width": 100,
				},
				{
					
					"fieldname": "emp_num",
					"fieldtype": "Data",
					"width": 150
				},
				{
					
					"fieldname": "name",
					"fieldtype": "Data",
					"width": 100
				},
				{
					
					"fieldname": "bank_ac_no",
					"fieldtype": "Data",
					"width": 100
				},
				{
					
					"fieldname": "yes",
					"fieldtype": "Data",
					"width": 100,
				},
				{
					
					"fieldname": "swift_number",
					"fieldtype": "Data",
					"width": 100
				},
				{
					
					"fieldname": "sa",
					"fieldtype": "Data",
					"width": 50,
				},
				{
					
					"fieldname": "month_to_date",
					"fieldtype": "Data",
					"width": 100
				},
				{
					
					"fieldname": "sar",
					"fieldtype": "Data",
					"width": 50,
				},
				{
					
					"fieldname": "one2",
					"fieldtype": "Data",
					"width": 100,
				},
				{
					
					"fieldname": "payrol",
					"fieldtype": "Data",
					"width": 100,
				},
				{
					
					"fieldname": "inma",
					"fieldtype": "Data",
					"width": 200,
				},
				{
					
					"fieldname": "",
					"fieldtype": "Data",
					"width": 10,
				},
				{
					
					"fieldname": "",
					"fieldtype": "Data",
					"width": 10,
				},
				{
					
					"fieldname": "",
					"fieldtype": "Data",
					"width": 10,
				},
				{
					
					"fieldname": "",
					"fieldtype": "Data",
					"width": 10,
				},
				{
					
					"fieldname": "",
					"fieldtype": "Data",
					"width": 10,
				},
				{
					
					"fieldname": "",
					"fieldtype": "Data",
					"width": 10,
				},
				{
					
					"fieldname": "",
					"fieldtype": "Data",
					"width": 10,
				},
				{
					
					"fieldname": "",
					"fieldtype": "Data",
					"width": 10,
				},
				{
					
					"fieldname": "",
					"fieldtype": "Data",
					"width": 10,
				},
				{
					
					"fieldname": "",
					"fieldtype": "Data",
					"width": 10,
				},
				{
					
					"fieldname": "",
					"fieldtype": "Data",
					"width": 10,
				},
				{
					
					"fieldname": "",
					"fieldtype": "Data",
					"width": 10,
				},
				{
					
					"fieldname": "id_number",
					"fieldtype": "Data",
					"width": 100
				},
			]

def get_columns_inma_wps():

	return [
			{
				
				"fieldname": "one1",
				"fieldtype": "Data",
				"width": 100,
			},
			{
				
				"fieldname": "row_num",
				"fieldtype": "Data",
				"width": 100,
			},
			{
				
				"fieldname": "emp_num",
				"fieldtype": "Data",
				"width": 150
			},
			{
				
				"fieldname": "name",
				"fieldtype": "Data",
				"width": 200
			},
			{
				
				"fieldname": "bank_ac_no",
				"fieldtype": "Data",
				"width": 100
			},
			{
				
				"fieldname": "yes",
				"fieldtype": "Data",
				"width": 100,
			},
			{
				
				"fieldname": "swift_number",
				"fieldtype": "Data",
				"width": 100
			},
			{
				
				"fieldname": "sa",
				"fieldtype": "Data",
				"width": 50,
			},
			{
				
				"fieldname": "month_to_date",
				"fieldtype": "",
				"width": 100
			},
			{
				
				"fieldname": "sar",
				"fieldtype": "Data",
				"width": 50,
			},
			{
				
				"fieldname": "one2",
				"fieldtype": "Data",
				"width": 100,
			},
			{
				
				"fieldname": "payrol",
				"fieldtype": "Data",
				"width": 100,
			},
			{
				
				"fieldname": "inma",
				"fieldtype": "Data",
				"width": 150,
			},
			{
				
				"fieldname": "",
				"fieldtype": "Data",
				"width": 10,
			},
			{
				
				"fieldname": "",
				"fieldtype": "Data",
				"width": 10,
			},
			{
				
				"fieldname": "",
				"fieldtype": "Data",
				"width": 10,
			},
			{
				
				"fieldname": "",
				"fieldtype": "Data",
				"width": 10,
			},
			{
				
				"fieldname": "",
				"fieldtype": "Data",
				"width": 10,
			},
			{
				
				"fieldname": "",
				"fieldtype": "Data",
				"width": 10,
			},
			{
				
				"fieldname": "",
				"fieldtype": "Data",
				"width": 10,
			},
			{
				
				"fieldname": "",
				"fieldtype": "Data",
				"width": 10,
			},
			{
				
				"fieldname": "",
				"fieldtype": "Data",
				"width": 10,
			},
			{
				
				"fieldname": "",
				"fieldtype": "Data",
				"width": 10,
			},
			{
				
				"fieldname": "",
				"fieldtype": "Data",
				"width": 10,
			},
			{
				
				"fieldname": "",
				"fieldtype": "Data",
				"width": 10,
			},
			{
				
				"fieldname": "",
				"fieldtype": "Data",
				"width": 10,
			},
			{
				
				"fieldname": "id_number",
				"fieldtype": "Data",
				"width": 100
			},
			{
				
				"fieldname": "",
				"fieldtype": "Data",
				"width": 10,
			},
			{
				
				"fieldname": "basic",
				"fieldtype": "Data",
				"width": 100
			},
			{
				
				"fieldname": "housing_allowance",
				"fieldtype": "Data",
				"width": 100
			},
			{
				
				"fieldname": "allowance_trans",
				"fieldtype": "Data",
				"width": 100
			},
			{
				
				"fieldname": "dedactions",
				"fieldtype": "Data",
				"width": 100
			},
		]

def get_columns_riad():
	return [
		{
			
			"fieldname": "riad_num",
			"fieldtype": "Data",
			"width": 100,
		},
		{
			
			"fieldname": "emp_num",
			"fieldtype": "Data",
			"width": 200,
		},
		{
			
			"fieldname": "y",
			"fieldtype": "Data",
			"width": 100,
		},
		{
			
			"fieldname": "agreament_s",
			"fieldtype": "Data",
			"width": 300,
		},
		{
			
			"fieldname": "row_num_riad",
			"fieldtype": "Data",
			"width": 100,
		},
		{
			
			"fieldname": "id_number_riad",
			"fieldtype": "Data",
			"width": 100,
		},
		{
			
			"fieldname": "spaces13", # 13 spaces
			"fieldtype": "Data",
			"width": 200,
		},
		{
			
			"fieldname": "bank_acc_riad",
			"fieldtype": "Data",
			"width": 200,
		},
		{
			
			"fieldname": "sar_header", # 10 spaces
			"fieldtype": "Data",
			"width": 100,
		},
		{
			
			"fieldname": "salary",
			"fieldtype": "Data",
			# "apply_currency_formatter": 2,
			"width": 200,
		},
		{
			
			"fieldname": "sar",
			"fieldtype": "Data",
			"width": 100,
		},
		{
			
			"fieldname": "spaces239", # 239 spaces
			"fieldtype": "Data",
			"width": 10,
		},
		{
			
			"fieldname": "emp_name",
			"fieldtype": "Data",
			"width": 200,
		},
		{
			
			"fieldname": "spaces90", # 90 spaces
			"fieldtype": "Data",
			"width": 10,
		},
		{
			
			"fieldname": "emp_bank",
			"fieldtype": "Data",
			"width": 150,
		},
		{
			
			"fieldname": "spaces129", # 129 spaces
			"fieldtype": "Data",
			"width": 10,
		},	
		{
			
			"fieldname": "basic",
			"fieldtype": "Data",
			"width": 200
		},
		{
			
			"fieldname": "housing_allowance",
			"fieldtype": "Data",
			"width": 200
		},
		{
			
			"fieldname": "other_earnings",
			"fieldtype": "Data",
			"width": 200
		},
		{
			
			"fieldname": "dedactions",
			"fieldtype": "Data",
			"width": 200
		},
		{
			
			"fieldname": "spaces33", # 33 spaces
			"fieldtype": "Data",
			"width": 10,
		},
	]

def get_columns_ahly():
	return 	[
		{
			
			"fieldname": "emp_bank_ahly",
			"fieldtype": "Data",
			"width": 150,
		},
		{
			
			"fieldname": "bank_acc_ahly",
			"fieldtype": "Data",
			"width": 150,
		},
		{
			
			"fieldname": "salary_ahly",
			"fieldtype": "Data",
			"width": 150,
		},
		{
			
			"fieldname": "Month",
			"fieldtype": "Data",
			"width": 150,
		},
		{
			
			"fieldname": "emp_name",
			"fieldtype": "Data",
			"width": 250,
		},
		{
			
			"fieldname": "id_number",
			"fieldtype": "Data",
			"width": 150,
		},
		{
			
			"fieldname": "permanent_address",
			"fieldtype": "Data",
			"width": 200,
		},
	]

def get_columns_sumba():
	return 	[
		{
			
			"fieldname": "num",
			"fieldtype": "Data",
			"width": 100,
		},
		{
			
			"fieldname": "emp_num",
			"fieldtype": "Data",
			"width": 150,
		},
		{
			
			"fieldname": "emp_name",
			"fieldtype": "Data",
			"width": 200,
		},
		{
			
			"fieldname": "salary",
			"fieldtype": "Data",
			"width": 200,
		},
		{
			
			"fieldname": "checksum",
			"fieldtype": "Data",
			"width": 250,
		},
		{
			
			"fieldname": "emp_bank",
			"fieldtype": "Data",
			"width": 150,
		},
		{
			
			"fieldname": "bank_acc_no",
			"fieldtype": "Data",
			"width": 200,
		},
		{
			
			"fieldname": "zero",
			"fieldtype": "Data",
			"width": 100,
		},
		{
			
			"fieldname": "nationality",
			"fieldtype": "Data",
			"width": 100,
		},
		{
			
			"fieldname": "id_number",
			"fieldtype": "Data",
			"width": 100,
		},
		{
			
			"fieldname": "departement_location",
			"fieldtype": "Data",
			"width": 100,
		},
		{
			
			"fieldname": "spaces19", # 19 spaces
			"fieldtype": "Data",
			"width": 10,
		},
		{
			
			"fieldname": "basic",
			"fieldtype": "Data",
			"width": 170
		},
		{
			
			"fieldname": "housing_allowance",
			"fieldtype": "Data",
			"width": 170
		},
		{
			
			"fieldname": "other_earnings",
			"fieldtype": "Data",
			"width": 170
		},
		{
			
			"fieldname": "dedactions",
			"fieldtype": "Data",
			"width": 170
		},
	]

def get_columns_alrajhi_payroll():
	return 	[
		{
			
			"fieldname": "emp_num",
			"fieldtype": "Data",
			"width": 150,
		},
		{
			
			"fieldname": "bank_code",
			"fieldtype": "Data",
			"width": 200,
		},
		{
			
			"fieldname": "bank_acc_no",
			"fieldtype": "Data",
			"width": 200,
		},
		{
			
			"fieldname": "emp_name",
			"fieldtype": "Data",
			"width": 250,
		},
		{
			
			"fieldname": "salary",
			"fieldtype": "Data",
			"width": 150,
		},
		{
			
			"fieldname": "id_number",
			"fieldtype": "Data",
			"width": 100,
		},
		{
			
			"fieldname": "zero",
			"fieldtype": "Data",
			"width": 100,
		},
		{
			
			"fieldname": "onespace", # 14 spaces in emplooyees and one space in header
			"fieldtype": "Data",
			"width": 100,
		},
		{
			
			"fieldname": "file_seq",
			"fieldtype": "Data",
			"width": 100,
		},

		{
			
			"fieldname": "space65", #65 spaces in header
			"fieldtype": "Data",
			"width": 100,
		},
	]

def get_columns_alrajhi_interchange():
	return 	[
		{
			
			"fieldname": "emp_num",
			"fieldtype": "Data",
			"width": 150,
		},
		{
			
			"fieldname": "bank_code",
			"fieldtype": "Data",
			"width": 100,
		},
		{
			
			"fieldname": "bank_acc_no",
			"fieldtype": "Data",
			"width": 200,
		},
		{
			
			"fieldname": "emp_name",
			"fieldtype": "Data",
			"width": 350,
		},
		{
			
			"fieldname": "salary",
			"fieldtype": "data",
			"width": 200,
		},
		{
			
			"fieldname": "id_number",
			"fieldtype": "Data",
			"width": 200,
		},
		{
			
			"fieldname": "zero",
			"fieldtype": "Data",
			"width": 150,
		},
		{
			
			"fieldname": "zero3",
			"fieldtype": "Data",
			"width": 100,
		},
		{
			
			"fieldname": "i", # 11 spaces
			"fieldtype": "Data",
			"width": 100,
		},
	]

def get_columns_alrajhi_payroll_card():
	return 	[
		{
			
			"fieldname": "emp_num",
			"fieldtype": "Data",
			"width": 120,
		},
		{
			
			"fieldname": "zero5",
			"fieldtype": "Data",
			"width": 100,
		},
		{
			
			"fieldname": "payroll_card_number",
			"fieldtype": "Data",
			"width": 180,
		},
		{
			
			"fieldname": "emp_name",
			"fieldtype": "Data",
			"width": 180,
		},
		{
			
			"fieldname": "id_number_rajhi",
			"fieldtype": "Data",
			"width": 120,
		},
		{
			
			"fieldname": "salary",
			"fieldtype": "Data",
			"width": 120,
		},
		{
			
			"fieldname": "date",
			"fieldtype": "Data",
			"width": 100,
		},
		{
			
			"fieldname": "op_type",
			"fieldtype": "Data",
			"width": 50,
		},
		{
			
			"fieldname": "zero6",
			"fieldtype": "Data",
			"width": 80,
		},
		{
			
			"fieldname": "spaces10",
			"fieldtype": "Data", # 10 spaces
			"width": 50,
		},
		{
			
			"fieldname": "phone",
			"fieldtype": "Data",
			"width": 100,
		},
		{
			
			"fieldname": "basic",
			"fieldtype": "Data",
			"width": 120
		},
		{
			
			"fieldname": "housing_allowance",
			"fieldtype": "Data",
			"width": 120
		},
		{
			
			"fieldname": "other_earnings",
			"fieldtype": "Data",
			"width": 120
		},
		{
			
			"fieldname": "dedactions",
			"fieldtype": "Data",
			"width": 120
		},
	]

def get_columns_alaraby():
		return [
				{
					
					"fieldname": "d",
					"fieldtype": "Data",
					"width": 50,
				},

				{
					
					"fieldname": "month_to_date",
					"fieldtype": "Data",
					"width": 100
				},
				{
					
					"fieldname": "bank_ac_no",
					"fieldtype": "Data",
					"width": 150
				},
				{
					
					"fieldname": "first_name",
					"fieldtype": "Data",
					"width": 150
				},
				{
					
					"fieldname": "swift_number",
					"fieldtype": "Data",
					"width": 150
				},
				{
					
					"fieldname": "month",
					"fieldtype": "Data",
					"width": 100
				},
				{
					
					"fieldname": "basic",
					"fieldtype": "Data",
					"width": 100
				},
				{
					
					"fieldname": "housing_allowance",
					"fieldtype": "Data",
					"width": 100
				},
				{
					
					"fieldname": "other_earnings",
					"fieldtype": "Data",
					"width": 100
				},
				{
					
					"fieldname": "dedactions",
					"fieldtype": "Data",
					"width": 100
				},
				{
					
					"fieldname": "id_number",
					"fieldtype": "Data",
					"width": 150
				},
				{
					
					"fieldname": "co_number",
					"fieldtype": "Data",
					"width": 150
				}
			]
