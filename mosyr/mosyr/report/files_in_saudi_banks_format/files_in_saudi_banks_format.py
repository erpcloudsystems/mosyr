# Copyright (c) 2022, AnvilERP and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from random import randint
import datetime


def execute(filters=None):
	if not filters.get('company'): return [], []
	co_controller = frappe.get_list("Company Controller")
	if len(co_controller)>0:
		company_controller = frappe.get_doc("Company Controller" , filters.get('company'))
		disbursement_type = company_controller.disbursement_type
		bank_name = company_controller.bank_name
		if bank_name == "Al Inma Bank" and disbursement_type == 'Payroll':
			return get_columns_inma_payroll(),get_data_inma_payroll(filters)
		elif bank_name == "Al Inma Bank" and disbursement_type == 'WPS':
			return get_columns_inma_wps(),get_data_inma_wps(filters)
		elif bank_name == "Riyadh Bank" and disbursement_type == 'WPS':
			return get_columns_riad(),get_data_riad(filters)
		elif bank_name == "The National Commercial Bank" and disbursement_type == 'WPS':
			return get_columns_ahly(),get_data_ahly(filters)
		elif bank_name == "Samba Financial Group" and disbursement_type == 'WPS':
			return get_columns_sumba(),get_data_sumba(filters)
		elif bank_name == "Al Rajhi Bank" and disbursement_type == 'Payroll':
			return get_columns_alrajhi_payroll(),get_data_alrajhi_payroll(filters)
		elif bank_name == "Al Rajhi Bank" and disbursement_type == 'Interchange':
			return get_columns_alrajhi_interchange(),get_data_alrajhi_interchange(filters)
		elif bank_name == "Al Rajhi Bank" and disbursement_type == 'Payroll Cards':
			return get_columns_alrajhi_payroll_card(),get_data_alrajhi_payroll_card(filters)
		elif bank_name == "ARNB" and disbursement_type == 'WPS':
			return get_columns_alaraby(),get_data_alaraby(filters)
		else :
			return [] , []
	else :
		return [] , []

def get_data_inma_payroll(filters):
	condition='1=1 '
	if filters.get("month"):
		monthes = ['January',
				'February',
				'March',
				'April',
				'May',
				'June',
				'July',
				'August',
				'September',
				'October',
				'November',
				'December']
		date = filters.get("month")
		if date in monthes:
			idx = monthes.index(date) + 1
			condition += f""" AND Month (sl.start_date)={idx}"""
	if(filters.get('bank')):condition += f" AND emp.bank_name='{filters.get('bank')}'"
	if(filters.get('company')):condition += f" AND emp.company='{filters.get('company')}'"
	data = frappe.db.sql(f"""
		SELECT
			1 as one1,
			emp.employee_number as emp_num,
			emp.first_name,
			ROW_NUMBER() OVER (ORDER BY emp.first_name)  row_num ,
			emp.first_name as name,
			emp.bank_ac_no,
			'yes' as yes,
			b.swift_number,
			'SA' as sa,
			sl.month_to_date,
			'SAR' as sar,
			1 as one2,
			'/PAYROLL/' as payrol,
			IF(b.swift_number="INMA", 'BANK ACCOUNT', "SARIE") as inma,
			id.id_number as id_number
		FROM `tabEmployee` emp  
		LEFT JOIN `tabSalary Slip` sl ON sl.employee=emp.name and sl.status='Submitted' 
		LEFT JOIN `tabBank` b ON b.name=emp.bank_name
		LEFT JOIN `tabIdentity` id ON id.parent=emp.name
		WHERE {condition}
		GROUP BY emp.first_name
		ORDER BY row_num
		""",as_dict=1)
	company = filters.get('company') or frappe.get_doc("Global Defaults").default_company
	company_controller = frappe.get_doc("Company Controller" ,company)
	salary_slip = frappe.get_last_doc("Salary Slip",filters={'company':company,'docstatus':1}) 
	total_emp = len(frappe.get_list("Employee", filters={'status':'Active',"company": company}))
	salary_slip_list = frappe.get_list("Salary Slip",fields=['month_to_date'],filters={'company':company,'docstatus':1})
	salary=[]
	for ssl in salary_slip_list :
		salary.append(ssl.month_to_date)
	total_salary=sum(salary)
	
	data.insert(0,
		{'one1': 0,
		'row_num': company_controller.company_id,
		'emp_num': company_controller.bank_account_number,
		'name':company_controller.bank_name,
		'bank_ac_no':salary_slip.posting_date.strftime("%Y%m%d"),
		'yes':salary_slip.posting_date.strftime("%Y%m%d"),
		'swift_number':'',
		'sa':total_emp,
		'month_to_date':total_salary,
		'sar':'SAR',

		})

	return data

def get_data_inma_wps(filters):
	condition='1=1 '
	if filters.get("month"):
		monthes = ['January',
				'February',
				'March',
				'April',
				'May',
				'June',
				'July',
				'August',
				'September',
				'October',
				'November',
				'December']
		date = filters.get("month")
		if date in monthes:
			idx = monthes.index(date) + 1
			condition += f""" AND Month (sl.start_date)={idx}"""
	if(filters.get('bank')):condition += f" AND emp.bank_name='{filters.get('bank')}'"
	if(filters.get('company')):condition += f" AND emp.company='{filters.get('company')}'"

	data = frappe.db.sql(f"""
		SELECT
			1 as one1,
			emp.employee_number as emp_num,
			emp.name,
			ROW_NUMBER() OVER (ORDER BY emp.first_name)  row_num ,
			emp.first_name as name,
			emp.bank_ac_no,
			'Yes' as yes,
			b.swift_number,
			'SA' as sa,
			sl.month_to_date,
			'SAR' as sar,
			1 as one2,
			'/PAYROLL/' as payrol,
			IF(b.swift_number="INMA", 'BANK ACCOUNT', "SARIE") as inma,
			id.id_number as id_number,
			sd.amount as basic,
			sde.amount as housing_allowance,
			SUM(sade.amount) as other_earnings,
			sl.total_deduction as dedactions

		FROM `tabEmployee` emp  
		LEFT JOIN `tabSalary Slip` sl ON sl.employee=emp.name and sl.status='Submitted'
		LEFT JOIN `tabBank` b ON b.name=emp.bank_name
		LEFT JOIN `tabIdentity` id ON id.parent=emp.name
		LEFT JOIN `tabSalary Detail` sd ON sd.parent=sl.name and sd.salary_component="Basic"
		LEFT JOIN `tabSalary Detail` sde ON sde.parent=sl.name and sde.salary_component="Allowance Housing"
		LEFT JOIN `tabSalary Detail` sade ON sade.parent=sl.name and sade.salary_component<>"Allowance Housing" and sade.salary_component<>"Basic"  and sade.parentfield='earnings'
		WHERE {condition}
		GROUP BY emp.first_name
		""",as_dict=1)
		
	company = filters.get('company') or frappe.get_doc("Global Defaults").default_company
	bank = filters.get('bank') 
	company_controller = frappe.get_doc("Company Controller" ,company)
	salary_slip = frappe.get_last_doc("Salary Slip" ,filters={'docstatus':1,'company':company}) 
	total_emp = len(frappe.get_list("Employee", filters={'status':'Active',"company": company}))
	salary_slip_list = frappe.get_list("Salary Slip",fields=['month_to_date'],filters={'company':company,'docstatus':1})
	salary=[]
	for ssl in salary_slip_list :
		salary.append(ssl.month_to_date)
	total_salary=sum(salary)

	data.insert(0,
		{'one1': "WPS",
		'row_num': company_controller.company_id,
		'emp_num': company_controller.bank_account_number,
		'name':company_controller.bank_name,
		'bank_ac_no':salary_slip.posting_date.strftime("%Y%m%d"),
		'yes':salary_slip.posting_date.strftime("%Y%m%d"),
		'swift_number':'',
		'sa':total_emp,
		'month_to_date':total_salary,
		'sar':'SAR',
		'one2': company_controller.labors_office_file_no
		})
	return data

def get_data_riad(filters):
	condition='1=1 '
	if filters.get("month"):
		monthes = ['January',
				'February',
				'March',
				'April',
				'May',
				'June',
				'July',
				'August',
				'September',
				'October',
				'November',
				'December']
		date = filters.get("month")
		if date in monthes:
			idx = monthes.index(date) + 1
			condition += f""" AND Month (sl.start_date)={idx}"""
	if(filters.get('bank')):condition += f" AND emp.bank_name='{filters.get('bank')}'"
	if(filters.get('company')):condition += f" AND emp.company='{filters.get('company')}'"
	company = filters.get('company') or frappe.get_doc("Global Defaults").default_company
	agreement_symbol = frappe.get_value("Company Controller" , company , 'agreement_symbol') or '0'
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
			LPAD(ROW_NUMBER() OVER (ORDER BY emp.first_name) + 572700000 ,10,'0') row_num_riad,
			CASE WHEN id.id_number <> '' THEN LPAD(id.id_number,10,0)
			ELSE '0000000000'
			END AS id_number_riad ,
			LPAD(emp.bank_ac_no, 24, 0) as bank_acc_riad,
			LPAD(FORMAT(sl.month_to_date,2), 16, 0 ) as salary,
			'SAR' as sar,
			LPAD(emp.first_name,50,' ') as emp_name,
			RPAD(b.swift_number,11, 'X') as emp_bank,
			LPAD(FORMAT(sd.amount,2),13,0) as basic,
			LPAD(FORMAT(sde.amount,2),13,0) as housing_allowance,
			LPAD(FORMAT(SUM(sade.amount) ,2) ,13 ,0) as other_earnings,
			LPAD(FORMAT(sl.total_deduction,2),13 ,0) as dedactions
		FROM `tabEmployee` emp  
		LEFT JOIN `tabSalary Slip` sl ON sl.employee=emp.name and sl.status='Submitted' 
		LEFT JOIN `tabBank` b ON b.name=emp.bank_name
		LEFT JOIN `tabIdentity` id ON id.parent=emp.name
		LEFT JOIN `tabCompany Controller` cc ON cc.bank_name=b.name
		LEFT JOIN `tabSalary Detail` sd ON sd.parent=sl.name and sd.salary_component="Basic"
		LEFT JOIN `tabSalary Detail` sde ON sde.parent=sl.name and sde.salary_component="Allowance Housing"
		LEFT JOIN `tabSalary Detail` sade ON sade.parent=sl.name and sade.salary_component<>"Allowance Housing" and sade.salary_component<>"Basic"  and sade.parentfield='earnings'
		WHERE {condition}
		GROUP BY emp.first_name,emp_num
		ORDER BY row_num_riad
		""",as_dict=1)
	for d in data :
		
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

	company_controller = frappe.get_doc("Company Controller" ,company)
	salary_slip = frappe.get_last_doc("Salary Slip" ,filters={'docstatus':1,'company':company}) 
	total_emp = len(frappe.get_list("Employee", filters={'status':'Active',"company": company}))
	salary_slip_list = frappe.get_list("Salary Slip",fields=['month_to_date'],filters={'company':company,'docstatus':1})
	salary=[]
	for ssl in salary_slip_list :
		salary.append(ssl.month_to_date)
	total_salary=sum(salary)

	data.insert(0,
		{
		'riad_num':  111,
		'emp_num' : company_controller.agreement_symbol,
		'y':salary_slip.posting_date.strftime("%Y%m%d"),
		'agreament_s':'PAYROLLREF-PR-0001- '+ str(randint(100, 10000000000000000)),
		'row_num_riad' :(str(company_controller.establishment_number).zfill(9)),
		'id_number_riad':"RIBL",
		'bank_account_number' : (str(company_controller.bank_account_number).zfill(13)),
		'bank_acc_riad':' ' # 11 spaces
		,'sar_header' : 'SAR',
		'salary':company_controller.labors_office_file_no.zfill(9),
		'sar':' ' # 9 spaces
		})
	data.append(
		{
			'riad_num':999,
			'emp_num':(str("%.2f" % total_salary).zfill(18)),
			'y':(str(total_emp).zfill(6))
		}
	)
	return data

def get_data_ahly(filters):
	condition='1=1 '
	if filters.get("month"):
		monthes = ['January',
				'February',
				'March',
				'April',
				'May',
				'June',
				'July',
				'August',
				'September',
				'October',
				'November',
				'December']
		date = filters.get("month")
		if date in monthes:
			idx = monthes.index(date) + 1
			condition += f""" AND Month (sl.start_date)={idx}"""
	if(filters.get('bank')):condition += f" AND emp.bank_name='{filters.get('bank')}'"
	if(filters.get('company')):condition += f" AND emp.company='{filters.get('company')}'"
	data = frappe.db.sql(f"""
		SELECT
			b.swift_number as emp_bank_ahly,
			emp.bank_ac_no as bank_acc_ahly,
			sl.month_to_date as salary_ahly,
			LPAD(MONTHNAME(sl.start_date),3) AS Month,
			emp.first_name as emp_name,
			id.id_number as id_number,
			emp.permanent_address 
		FROM `tabEmployee` emp  
		LEFT JOIN `tabSalary Slip` sl ON sl.employee=emp.name and sl.status='Submitted' 
		LEFT JOIN `tabBank` b ON b.name=emp.bank_name
		LEFT JOIN `tabIdentity` id ON id.parent=emp.name
		WHERE {condition}
		GROUP BY emp.first_name ,bank_acc_ahly
		""",as_dict=1)
	return data

def get_data_sumba(filters):
	condition='1=1 '
	if filters.get("month"):
		monthes = ['January',
				'February',
				'March',
				'April',
				'May',
				'June',
				'July',
				'August',
				'September',
				'October',
				'November',
				'December']
		date = filters.get("month")
		if date in monthes:
			idx = monthes.index(date) + 1
			condition += f""" AND Month (sl.start_date)={idx}"""
	if(filters.get('bank')):condition += f" AND emp.bank_name='{filters.get('bank')}'"
	if(filters.get('company')):condition += f" AND emp.company='{filters.get('company')}'"
	company = filters.get('company') or frappe.get_doc("Global Defaults").default_company
	company_controller = frappe.get_doc("Company Controller" ,company)

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
			LPAD(emp.employee_number,12 ,0) as emp_num,
			RPAD(emp.first_name,45,' ') as emp_name,
			LPAD(FORMAT(sl.month_to_date,2),13,0) as salary,
			NULL as checksum,
			LPAD(b.swift_number,4,' ') as emp_bank,
			LPAD(emp.bank_ac_no,24,0) as bank_acc_no,
			'00000000000' as zero,
			IF(emp.nationality="Saudi", '1', "2") as nationality ,
			CASE WHEN id.id_number <> '' THEN LPAD(id.id_number,10,0)
			ELSE '0000000000'
			END AS id_number,
			LPAD(emp.departement_location, 20 ,' ') as departement_location,
			LPAD(FORMAT(sd.amount,2), 13 , 0) as basic,
			LPAD(FORMAT(sde.amount ,2) , 13 , 0) as housing_allowance,
			LPAD(FORMAT(SUM(sade.amount),2) , 13 , 0) as other_earnings,
			LPAD(FORMAT(sl.total_deduction,2), 13 , 0)  as dedactions
		FROM `tabEmployee` emp
		LEFT JOIN `tabSalary Slip` sl ON sl.employee=emp.name and sl.status='Submitted' 
		LEFT JOIN `tabBank` b ON b.name=emp.bank_name
		LEFT JOIN `tabIdentity` id ON id.parent=emp.name
		LEFT JOIN `tabSalary Detail` sd ON sd.parent=sl.name and sd.salary_component="Basic"
		LEFT JOIN `tabSalary Detail` sde ON sde.parent=sl.name and sde.salary_component="Allowance Housing"
		LEFT JOIN `tabSalary Detail` sade ON sade.parent=sl.name and sade.salary_component<>"Allowance Housing" and sade.salary_component<>"Basic"  and sade.parentfield='earnings'
		WHERE {condition}
		GROUP BY emp.name
		""",as_dict=1)
	for d in data :
		if d.get('salary', False):
			salary = d.get('salary').replace(',','').split('.')[0][1:]
		else :salary = d.get('salary').split('.')[0][1:]
		checksum =_samba_wps_checksum(company_controller.company_id,d.get('id_number'),d.get('emp_name'),salary)
		d.update({'checksum':checksum})
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
	
	
	company = filters.get('company') or frappe.get_doc("Global Defaults").default_company
	salary_slip = frappe.get_last_doc("Salary Slip" ,filters={'docstatus':1,'company':company}) 
	total_emp = len(frappe.get_list("Employee", filters={'status':'Active',"company": company}))
	salary_slip_list = frappe.get_list("Salary Slip",fields=['month_to_date'],filters={'company':company,'docstatus':1})
	salary=[]
	for ssl in salary_slip_list :
		salary.append(ssl.month_to_date)
	total_salary=sum(salary)
	data.insert(0,
		{
		'num': '0011',
		'emp_num' : str(salary_slip.posting_date.month).zfill(2),
		'emp_name' : str(salary_slip.posting_date.day).zfill(2),
		'salary':salary_slip.posting_date.strftime("%Y%m%d"),
		'checksum':company_controller.organization_english.ljust(40),
		'emp_bank' : company_controller.company_id.ljust(152)
		})
	if (str("%.2f" % total_salary).zfill(19), False): 
		salary=(str("%.2f" % total_salary).zfill(19)).replace(',','').replace('.','')
	else:
		salary=(str("%.2f" % total_salary).zfill(19))
	data.append(
		{
			'num':'003',
			'emp_num':str(total_emp).zfill(6),
			'emp_name':salary,
			'salary':' ' # 181 spaces
		}
	)
	return data

def get_data_alrajhi_payroll(filters):
	condition='1=1 '
	if filters.get("month"):
		monthes = ['January', 'February', 'March', 'April','May', 'June', 'July', 'August', 'September', 'October', 'November','December']
		date = filters.get("month")
		if date in monthes:
			idx = monthes.index(date) + 1
			condition += f""" AND Month (sl.start_date)={idx}"""
	if(filters.get('bank')):condition += f" AND emp.bank_name='{filters.get('bank')}'"
	if(filters.get('company')):condition += f" AND emp.company='{filters.get('company')}'"
	data = frappe.db.sql(f"""
		SELECT
			LPAD(emp.employee_number,12,0) as emp_num,
			LPAD(b.swift_number , 4,' ') as bank_code,
			LPAD(emp.bank_ac_no,24,0) as bank_acc_no,
			RPAD(emp.first_name ,50 ,' ') as emp_name,
			LPAD(FORMAT(sl.month_to_date,2) , 17, 0) as salary,
			LPAD(id.id_number , 15 , 0) as id_number,
			'0' as zero
		FROM `tabEmployee` emp  
		LEFT JOIN `tabSalary Slip` sl ON sl.employee=emp.name and sl.status='Submitted' 
		LEFT JOIN `tabBank` b ON b.name=emp.bank_name
		LEFT JOIN `tabIdentity` id ON id.parent=emp.name
		WHERE {condition}
		GROUP BY emp_num ,bank_acc_no
		ORDER BY emp_num
		""",as_dict=1)
	for d in data :
		if d.get('salary', False):
			sl_total = d.get('salary').replace(',','').replace('.','')
			d.update({'salary':sl_total})
	company = filters.get('company') or frappe.get_doc("Global Defaults").default_company
	company_controller = frappe.get_doc("Company Controller" ,company)
	salary_slip = frappe.get_last_doc("Salary Slip" ,filters={'docstatus':1,'company':company}) 
	total_emp = len(frappe.get_list("Employee", filters={'status':'Active',"company": company}))
	# get total salary
	salary_slip_list = frappe.get_list("Salary Slip",fields=['month_to_date'],filters={'company':company,'docstatus':1})
	salary=[]
	for ssl in salary_slip_list :
		salary.append(ssl.month_to_date)
	total_salary=sum(salary)

	if company_controller.calendar_accreditation == 'Gregorian': cal = 'G'
	if company_controller.calendar_accreditation == 'Hijri': cal = 'H'

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
	data.insert(0,
		{
		'emp_num': '000000000000',
		'bank_code' : cal,
		'bank_acc_no' : today.strftime("%Y%m%d"),
		'emp_name': (today + datetime.timedelta(days=1)).strftime("%Y%m%d"),
		'salary':salary,
		'id_number' : str(total_emp).zfill(8),
		"zero":str(company_controller.bank_account_number).zfill(15),
		"file_seq":"",
		})
	return data

def get_data_alrajhi_interchange(filters):
	condition='1=1 '
	if filters.get("month"):
		monthes = ['January',
				'February',
				'March',
				'April',
				'May',
				'June',
				'July',
				'August',
				'September',
				'October',
				'November',
				'December']
		date = filters.get("month")
		if date in monthes:
			idx = monthes.index(date) + 1
			condition += f""" AND Month (sl.start_date)={idx}"""
	if(filters.get('bank')):condition += f" AND emp.bank_name='{filters.get('bank')}'"
	if(filters.get('company')):condition += f" AND emp.company='{filters.get('company')}'"
	data = frappe.db.sql(f"""
		SELECT
			LPAD(emp.employee_number,12,0) as emp_num,
			LPAD(b.swift_number,4,' ') as bank_code,
			RPAD(emp.bank_ac_no,24,'X') as bank_acc_no,
			LPAD(emp.first_name,50,'x') as emp_name,
			LPAD(FORMAT(sl.month_to_date,2),17,0) as salary,
			LPAD(id.id_number,15,0) as id_number,
			'0' as zero,
			'000' as zero3
		FROM `tabEmployee` emp  
		LEFT JOIN `tabSalary Slip` sl ON sl.employee=emp.name and sl.status='Submitted' 
		LEFT JOIN `tabBank` b ON b.name=emp.bank_name
		LEFT JOIN `tabIdentity` id ON id.parent=emp.name
		WHERE {condition}
		GROUP BY emp.name ,emp_num
		ORDER BY emp_num
		""",as_dict=1)

	for d in data :
		if  d.get('salary', False):
			sl_total = d.get('salary').replace(',','').replace('.','')
			d.update({'salary':sl_total})
	company = filters.get('company') or frappe.get_doc("Global Defaults").default_company
	company_controller = frappe.get_doc("Company Controller" ,company)
	salary_slip = frappe.get_last_doc("Salary Slip" ,filters={'docstatus':1,'company':company}) 
	total_emp = len(frappe.get_list("Employee", filters={'status':'Active',"company": company}))
	if company_controller.calendar_accreditation == 'Gregorian': cal = 'G' 
	if company_controller.calendar_accreditation == 'Hijri': cal = 'H' 
	# get total salary
	salary_slip_list = frappe.get_list("Salary Slip",fields=['month_to_date'],filters={'company':company,'docstatus':1})
	salary=[]
	for ssl in salary_slip_list :
		salary.append(ssl.month_to_date)
	total_salary=sum(salary)
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
	data.insert(0,
		{
		'emp_num': '000000000000',
		'bank_code' : cal,
		'bank_acc_no' : today.strftime("%Y%m%d"),
		'emp_name': (today + datetime.timedelta(days=1)).strftime("%Y%m%d"),
		'salary':salary,
		'id_number' : str(total_emp).zfill(8),
		"zero":company_controller.bank_account_number.zfill(15),
		"zero3":" "*67,
		"i":"I",
		})
	return data

def get_data_alrajhi_payroll_card(filters):
	condition='1=1 '
	if filters.get("month"):
		monthes = ['January',
				'February',
				'March',
				'April',
				'May',
				'June',
				'July',
				'August',
				'September',
				'October',
				'November',
				'December']
		date = filters.get("month")
		if date in monthes:
			idx = monthes.index(date) + 1
			condition += f""" AND Month (sl.start_date)={idx}"""
	if(filters.get('bank')):condition += f" AND emp.bank_name='{filters.get('bank')}'"
	if(filters.get('company')):condition += f" AND emp.company='{filters.get('company')}'"
	today=datetime.datetime.today().strftime('%Y%m%d')
	data = frappe.db.sql(f"""
		SELECT
			LPAD(emp.employee_number,12,0) as emp_num,
			'00000' as zero5,
			LPAD(emp.payroll_card_number,19,0) as payroll_card_number,
			LPAD(emp.first_name,50,' ') as emp_name,
			CASE WHEN id.id_number <> '' THEN LPAD(id.id_number,10,0)
			ELSE '0000000000'
			END AS id_number,
			LPAD(FORMAT(sl.month_to_date,2), 17, 0 )as salary,
			{today} as date,
			'2' as op_type,
			'000000' as zero6,
			CASE WHEN emp.cell_number <> '' THEN LPAD(emp.cell_number,10,0)
			ELSE '0000000000'
			END AS phone,
			LPAD(FORMAT(sd.amount, 2),13,0) as basic ,
			LPAD(FORMAT(sde.amount, 2),13,0) as housing_allowance,
			LPAD(FORMAT(SUM(sade.amount), 2),13,0) as other_earnings,
			LPAD(FORMAT(sl.total_deduction, 2),13,0) as dedactions
		FROM `tabEmployee` emp  
		LEFT JOIN `tabSalary Slip` sl ON sl.employee=emp.name and sl.status='Submitted' 
		LEFT JOIN `tabIdentity` id ON id.parent=emp.name
		LEFT JOIN `tabSalary Detail` sd ON sd.parent=sl.name and sd.salary_component="Basic"
		LEFT JOIN `tabSalary Detail` sde ON sde.parent=sl.name and sde.salary_component="Allowance Housing"
		LEFT JOIN `tabSalary Detail` sade ON sade.parent=sl.name and sade.salary_component<>"Allowance Housing" and sade.salary_component<>"Basic"  and sade.parentfield='earnings'
		WHERE {condition}
		GROUP BY emp.name
		ORDER BY emp_num
		""",as_dict=1)

	for d in data :
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
	condition='1=1 '
	if filters.get("month"):
		monthes = ['January',
				'February',
				'March',
				'April',
				'May',
				'June',
				'July',
				'August',
				'September',
				'October',
				'November',
				'December']
		date = filters.get("month")
		if date in monthes:
			idx = monthes.index(date) + 1
			condition += f""" AND Month (sl.start_date)={idx}"""
	if(filters.get('bank')):condition += f" AND emp.bank_name='{filters.get('bank')}'"
	if(filters.get('company')):condition += f" AND emp.company='{filters.get('company')}'"
	month = monthes[frappe.utils.get_datetime().month]
	year = frappe.utils.get_datetime().year
	data = frappe.db.sql(f"""
		SELECT
			'D' as d,
			sl.month_to_date,
			sl.gross_pay,
			emp.bank_ac_no,
			emp.first_name,
			'NCBK' as swift_number,
			"salaries for {month} {year}" as month,
			sd.amount as basic,
			sde.amount  as housing_allowance,
			0 as other_earnings,
			sl.total_deduction as dedactions,
			id.id_number as id_number,
			null as co_number
		FROM `tabEmployee` emp  
		LEFT JOIN `tabSalary Slip` sl ON sl.employee=emp.name and sl.status='Submitted' 
		LEFT JOIN `tabBank` b ON b.name=emp.bank_name
		LEFT JOIN `tabIdentity` id ON id.parent=emp.name
		LEFT JOIN `tabSalary Detail` sd ON sd.parent=sl.name and sd.salary_component="Basic"
		LEFT JOIN `tabSalary Detail` sde ON sde.parent=sl.name and sde.salary_component="Allowance Housing"
		WHERE emp.status ='Active' and {condition}
		
		""",as_dict=1)
	for d in data:
		if d.get("gross_pay") and d.get("basic") and d.get("housing_allowance"):
			other_earnings = d.get("gross_pay" or 0) - d.get("basic" or 0) - d.get("housing_allowance" or 0)
			d.update({"other_earnings":other_earnings})
	company = filters.get('company') or frappe.get_doc("Global Defaults").default_company
	company_controller = frappe.get_doc("Company Controller" ,company)
	salary_slip_list = frappe.get_list("Salary Slip",fields=['month_to_date'],filters={'company':company,'docstatus':1})
	salary=[]
	for d in data:
		salary.append(d.get("month_to_date"))
	total_salary=sum(salary)
	data.insert(0,
		{'d': 'H',
		'month_to_date': "ARNB",
		'bank_ac_no': company_controller.agreement_number_for_customer,
		'first_name':"N",
		'swift_number':frappe.utils.get_datetime().date().strftime("%d%m%Y") + ".EX1",
		'month':company_controller.bank_account_number,
		'basic':"SAR",
		'housing_allowance': frappe.utils.get_datetime().date().strftime("%d%m%Y"),
		'other_earnings' :total_salary,
		'dedactions':frappe.utils.get_datetime().date().strftime("%d%m%Y"),
		'id_number':company_controller.company_id,
		'co_number':f"salaries for {month} {year}"
		})
	return data

def get_columns_inma_payroll():
		return [
				{
					"label": _(""),
					"fieldname": "one1",
					"fieldtype": "Data",
					"width": 10,
				},
				{
					"label": _("Idx"),
					"fieldname": "row_num",
					"fieldtype": "Data",
					"width": 100,
				},
				{
					"label": _("Employee Number"),
					"fieldname": "emp_num",
					"fieldtype": "Data",
					"width": 150
				},
				{
					"label": _("Name"),
					"fieldname": "name",
					"fieldtype": "Data",
					"width": 100
				},
				{
					"label": _("Bank Acount Number"),
					"fieldname": "bank_ac_no",
					"fieldtype": "Data",
					"width": 100
				},
				{
					"label": _(""),
					"fieldname": "yes",
					"fieldtype": "Data",
					"width": 100,
				},
				{
					"label": _("Bank Code"),
					"fieldname": "swift_number",
					"fieldtype": "Data",
					"width": 100
				},
				{
					"label": _(""),
					"fieldname": "sa",
					"fieldtype": "Data",
					"width": 50,
				},
				{
					"label": _("Total Salary"),
					"fieldname": "month_to_date",
					"fieldtype": "Data",
					"width": 100
				},
				{
					"label": _(""),
					"fieldname": "sar",
					"fieldtype": "Data",
					"width": 50,
				},
				{
					"label": _(""),
					"fieldname": "one2",
					"fieldtype": "Data",
					"width": 100,
				},
				{
					"label": _(""),
					"fieldname": "payrol",
					"fieldtype": "Data",
					"width": 100,
				},
				{
					"label": _(""),
					"fieldname": "inma",
					"fieldtype": "Data",
					"width": 200,
				},
				{
					"label": _(""),
					"fieldname": "",
					"fieldtype": "Data",
					"width": 10,
				},
				{
					"label": _(""),
					"fieldname": "",
					"fieldtype": "Data",
					"width": 10,
				},
				{
					"label": _(""),
					"fieldname": "",
					"fieldtype": "Data",
					"width": 10,
				},
				{
					"label": _(""),
					"fieldname": "",
					"fieldtype": "Data",
					"width": 10,
				},
				{
					"label": _(""),
					"fieldname": "",
					"fieldtype": "Data",
					"width": 10,
				},
				{
					"label": _(""),
					"fieldname": "",
					"fieldtype": "Data",
					"width": 10,
				},
				{
					"label": _(""),
					"fieldname": "",
					"fieldtype": "Data",
					"width": 10,
				},
				{
					"label": _(""),
					"fieldname": "",
					"fieldtype": "Data",
					"width": 10,
				},
				{
					"label": _(""),
					"fieldname": "",
					"fieldtype": "Data",
					"width": 10,
				},
				{
					"label": _(""),
					"fieldname": "",
					"fieldtype": "Data",
					"width": 10,
				},
				{
					"label": _(""),
					"fieldname": "",
					"fieldtype": "Data",
					"width": 10,
				},
				{
					"label": _(""),
					"fieldname": "",
					"fieldtype": "Data",
					"width": 10,
				},
				{
					"label": _(""),
					"fieldname": "",
					"fieldtype": "Data",
					"width": 10,
				},
				{
					"label": _("Id Number"),
					"fieldname": "id_number",
					"fieldtype": "Data",
					"width": 100
				},
			]

def get_columns_inma_wps():

	return [
			{
				"label": _(""),
				"fieldname": "one1",
				"fieldtype": "Data",
				"width": 100,
			},
			{
				"label": _("Idx"),
				"fieldname": "row_num",
				"fieldtype": "Data",
				"width": 100,
			},
			{
				"label": _("Employee Number"),
				"fieldname": "emp_num",
				"fieldtype": "Data",
				"width": 150
			},
			{
				"label": _("Name"),
				"fieldname": "name",
				"fieldtype": "Data",
				"width": 200
			},
			{
				"label": _("Bank Acount Number"),
				"fieldname": "bank_ac_no",
				"fieldtype": "Data",
				"width": 100
			},
			{
				"label": _(""),
				"fieldname": "yes",
				"fieldtype": "Data",
				"width": 100,
			},
			{
				"label": _("Bank Code"),
				"fieldname": "swift_number",
				"fieldtype": "Data",
				"width": 100
			},
			{
				"label": _(""),
				"fieldname": "sa",
				"fieldtype": "Data",
				"width": 50,
			},
			{
				"label": _("Total Salary"),
				"fieldname": "month_to_date",
				"fieldtype": "",
				"width": 100
			},
			{
				"label": _(""),
				"fieldname": "sar",
				"fieldtype": "Data",
				"width": 50,
			},
			{
				"label": _(""),
				"fieldname": "one2",
				"fieldtype": "Data",
				"width": 100,
			},
			{
				"label": _(""),
				"fieldname": "payrol",
				"fieldtype": "Data",
				"width": 100,
			},
			{
				"label": _(""),
				"fieldname": "inma",
				"fieldtype": "Data",
				"width": 150,
			},
			{
				"label": _(""),
				"fieldname": "",
				"fieldtype": "Data",
				"width": 10,
			},
			{
				"label": _(""),
				"fieldname": "",
				"fieldtype": "Data",
				"width": 10,
			},
			{
				"label": _(""),
				"fieldname": "",
				"fieldtype": "Data",
				"width": 10,
			},
			{
				"label": _(""),
				"fieldname": "",
				"fieldtype": "Data",
				"width": 10,
			},
			{
				"label": _(""),
				"fieldname": "",
				"fieldtype": "Data",
				"width": 10,
			},
			{
				"label": _(""),
				"fieldname": "",
				"fieldtype": "Data",
				"width": 10,
			},
			{
				"label": _(""),
				"fieldname": "",
				"fieldtype": "Data",
				"width": 10,
			},
			{
				"label": _(""),
				"fieldname": "",
				"fieldtype": "Data",
				"width": 10,
			},
			{
				"label": _(""),
				"fieldname": "",
				"fieldtype": "Data",
				"width": 10,
			},
			{
				"label": _(""),
				"fieldname": "",
				"fieldtype": "Data",
				"width": 10,
			},
			{
				"label": _(""),
				"fieldname": "",
				"fieldtype": "Data",
				"width": 10,
			},
			{
				"label": _(""),
				"fieldname": "",
				"fieldtype": "Data",
				"width": 10,
			},
			{
				"label": _(""),
				"fieldname": "",
				"fieldtype": "Data",
				"width": 10,
			},
			{
				"label": _("Id Number"),
				"fieldname": "id_number",
				"fieldtype": "Data",
				"width": 100
			},
			{
				"label": _(""),
				"fieldname": "",
				"fieldtype": "Data",
				"width": 10,
			},
			{
				"label": _(""),
				"fieldname": "",
				"fieldtype": "Data",
				"width": 10,
			},
			{
				"label": _("Basic"),
				"fieldname": "basic",
				"fieldtype": "Data",
				"width": 100
			},
			{
				"label": _("Allowance Housing"),
				"fieldname": "housing_allowance",
				"fieldtype": "Data",
				"width": 100
			},
			{
				"label": _("Other Earnings"),
				"fieldname": "other_earnings",
				"fieldtype": "Data",
				"width": 100
			},
			{
				"label": _("Dedactions"),
				"fieldname": "dedactions",
				"fieldtype": "Data",
				"width": 100
			},
		]

def get_columns_riad():
	return [
		{
			"label": _(""),
			"fieldname": "riad_num",
			"fieldtype": "Data",
			"width": 100,
		},
		{
			"label": _("Employee Number"),
			"fieldname": "emp_num",
			"fieldtype": "Data",
			"width": 200,
		},
		{
			"label": _(""),
			"fieldname": "y",
			"fieldtype": "Data",
			"width": 100,
		},
		{
			"label": _("Agreament Number"),
			"fieldname": "agreament_s",
			"fieldtype": "Data",
			"width": 300,
		},
		{
			"label": _(""),
			"fieldname": "row_num_riad",
			"fieldtype": "Data",
			"width": 100,
		},
		{
			"label": _("Identity"),
			"fieldname": "id_number_riad",
			"fieldtype": "Data",
			"width": 100,
		},
		{
			"label": _(""),
			"fieldname": "bank_account_number", # 13 spaces
			"fieldtype": "Data",
			"width": 200,
		},
		{
			"label": _("Account Number"),
			"fieldname": "bank_acc_riad",
			"fieldtype": "Data",
			"width": 200,
		},
		{
			"label": _(''),
			"fieldname": "sar_header", # 10 spaces
			"fieldtype": "Data",
			"width": 100,
		},
		{
			"label": _("Salary"),
			"fieldname": "salary",
			"fieldtype": "Data",
			# "apply_currency_formatter": 2,
			"width": 200,
		},
		{
			"label": _(""),
			"fieldname": "sar",
			"fieldtype": "Data",
			"width": 100,
		},
		{
			"label": _(""),
			"fieldname": "", # 239 spaces
			"fieldtype": "Data",
			"width": 10,
		},
		{
			"label": _("Employee Name"),
			"fieldname": "emp_name",
			"fieldtype": "Data",
			"width": 200,
		},
		{
			"label": _(""),
			"fieldname": "", # 90 spaces
			"fieldtype": "Data",
			"width": 10,
		},
		{
			"label": _("Back Code"),
			"fieldname": "emp_bank",
			"fieldtype": "Data",
			"width": 150,
		},
		{
			"label": _(""),
			"fieldname": "", # 129 spaces
			"fieldtype": "Data",
			"width": 10,
		},	
		{
			"label": _("Basic"),
			"fieldname": "basic",
			"fieldtype": "Data",
			"width": 200
		},
		{
			"label": _("Allowance Housing"),
			"fieldname": "housing_allowance",
			"fieldtype": "Data",
			"width": 200
		},
		{
			"label": _("Other Earnings"),
			"fieldname": "other_earnings",
			"fieldtype": "Data",
			"width": 200
		},
		{
			"label": _("Dedactions"),
			"fieldname": "dedactions",
			"fieldtype": "Data",
			"width": 200
		},
		{
			"label": _(""),
			"fieldname": "", # 33 spaces
			"fieldtype": "Data",
			"width": 10,
		},
	]

def get_columns_ahly():
	return 	[
		{
			"label": _("Bank Code"),
			"fieldname": "emp_bank_ahly",
			"fieldtype": "Data",
			"width": 150,
		},
		{
			"label": _("Employee Account Number"),
			"fieldname": "bank_acc_ahly",
			"fieldtype": "Data",
			"width": 150,
		},
		{
			"label": _("Salary"),
			"fieldname": "salary_ahly",
			"fieldtype": "Data",
			"width": 150,
		},
		{
			"label": _("Notes"),
			"fieldname": "Month",
			"fieldtype": "Data",
			"width": 150,
		},
		{
			"label": _("Employee Name"),
			"fieldname": "emp_name",
			"fieldtype": "Data",
			"width": 250,
		},
		{
			"label": _("Identity"),
			"fieldname": "id_number",
			"fieldtype": "Data",
			"width": 150,
		},
		{
			"label": _("Permanent Address"),
			"fieldname": "permanent_address",
			"fieldtype": "Data",
			"width": 200,
		},
	]

def get_columns_sumba():
	return 	[
		{
			"label": _(""),
			"fieldname": "num",
			"fieldtype": "Data",
			"width": 100,
		},
		{
			"label": _("Employee Number"),
			"fieldname": "emp_num",
			"fieldtype": "Data",
			"width": 150,
		},
		{
			"label": _("Employee Name"),
			"fieldname": "emp_name",
			"fieldtype": "Data",
			"width": 200,
		},
		{
			"label": _("Salary"),
			"fieldname": "salary",
			"fieldtype": "Data",
			"width": 200,
		},
		{
			"label": _("CheckSum"),
			"fieldname": "checksum",
			"fieldtype": "Data",
			"width": 250,
		},
		{
			"label": _("Bank Code"),
			"fieldname": "emp_bank",
			"fieldtype": "Data",
			"width": 150,
		},
		{
			"label": _("Bank Account Number"),
			"fieldname": "bank_acc_no",
			"fieldtype": "Data",
			"width": 200,
		},
		{
			"label": _(""),
			"fieldname": "zero",
			"fieldtype": "Data",
			"width": 100,
		},
		{
			"label": _("Is Saudi"),
			"fieldname": "nationality",
			"fieldtype": "Data",
			"width": 100,
		},
		{
			"label": _("Identity"),
			"fieldname": "id_number",
			"fieldtype": "Data",
			"width": 100,
		},
		{
			"label": _("Departement Location"),
			"fieldname": "departement_location",
			"fieldtype": "Data",
			"width": 100,
		},
		{
			"label": _(""),
			"fieldname": "", # 19 spaces
			"fieldtype": "Data",
			"width": 10,
		},
		{
			"label": _("Basic"),
			"fieldname": "basic",
			"fieldtype": "Data",
			"width": 170
		},
		{
			"label": _("Allowance Housing"),
			"fieldname": "housing_allowance",
			"fieldtype": "Data",
			"width": 170
		},
		{
			"label": _("Other Earnings"),
			"fieldname": "other_earnings",
			"fieldtype": "Data",
			"width": 170
		},
		{
			"label": _("Dedactions"),
			"fieldname": "dedactions",
			"fieldtype": "Data",
			"width": 170
		},
	]

def get_columns_alrajhi_payroll():
	return 	[
		{
			"label": _("Employee Number"),
			"fieldname": "emp_num",
			"fieldtype": "Data",
			"width": 150,
		},
		{
			"label": _("Bank Code"),
			"fieldname": "bank_code",
			"fieldtype": "Data",
			"width": 200,
		},
		{
			"label": _("Account Number"),
			"fieldname": "bank_acc_no",
			"fieldtype": "Data",
			"width": 200,
		},
		{
			"label": _("Employee Name"),
			"fieldname": "emp_name",
			"fieldtype": "Data",
			"width": 250,
		},
		{
			"label": _("Salary"),
			"fieldname": "salary",
			"fieldtype": "Data",
			"width": 150,
		},
		{
			"label": _("Identity"),
			"fieldname": "id_number",
			"fieldtype": "Data",
			"width": 100,
		},
		{
			"label": _("Employee ID Type"),
			"fieldname": "zero",
			"fieldtype": "Data",
			"width": 100,
		},
		{
			"label": _(""),
			"fieldname": "one", # 14 spaces
			"fieldtype": "Data",
			"width": 100,
		},
		{
			"label": _(""),
			"fieldname": "file_seq",
			"fieldtype": "Data",
			"width": 100,
		},

		{
			"label": _(""),
			"fieldname": "", #65 spaces in header
			"fieldtype": "Data",
			"width": 100,
		},
	]

def get_columns_alrajhi_interchange():
	return 	[
		{
			"label": _("Employee Number"),
			"fieldname": "emp_num",
			"fieldtype": "Data",
			"width": 150,
		},
		{
			"label": _("Bank Code"),
			"fieldname": "bank_code",
			"fieldtype": "Data",
			"width": 100,
		},
		{
			"label": _("Employee Account Number"),
			"fieldname": "bank_acc_no",
			"fieldtype": "Data",
			"width": 200,
		},
		{
			"label": _("Employee Name"),
			"fieldname": "emp_name",
			"fieldtype": "Data",
			"width": 350,
		},
		{
			"label": _("Salary"),
			"fieldname": "salary",
			"fieldtype": "data",
			"width": 200,
		},
		{
			"label": _("Identity"),
			"fieldname": "id_number",
			"fieldtype": "Data",
			"width": 200,
		},
		{
			"label": _(""),
			"fieldname": "zero",
			"fieldtype": "Data",
			"width": 150,
		},
		{
			"label": _(""),
			"fieldname": "zero3",
			"fieldtype": "Data",
			"width": 100,
		},
		{
			"label": _(""),
			"fieldname": "i", # 11 spaces
			"fieldtype": "Data",
			"width": 100,
		},
	]

def get_columns_alrajhi_payroll_card():
	return 	[
		{
			"label": _("Employee Number"),
			"fieldname": "emp_num",
			"fieldtype": "Data",
			"width": 120,
		},
		{
			"label": _(""),
			"fieldname": "zero5",
			"fieldtype": "Data",
			"width": 100,
		},
		{
			"label": _("Payroll Card Number"),
			"fieldname": "payroll_card_number",
			"fieldtype": "Data",
			"width": 180,
		},
		{
			"label": _("Employee Name"),
			"fieldname": "emp_name",
			"fieldtype": "Data",
			"width": 180,
		},
		{
			"label": _("Identity"),
			"fieldname": "id_number",
			"fieldtype": "Data",
			"width": 120,
		},
		{
			"label": _("Salary"),
			"fieldname": "salary",
			"fieldtype": "Data",
			"width": 120,
		},
		{
			"label": _("Date"),
			"fieldname": "date",
			"fieldtype": "Data",
			"width": 100,
		},
		{
			"label": _("Operation Type"),
			"fieldname": "op_type",
			"fieldtype": "Data",
			"width": 50,
		},
		{
			"label": _(""),
			"fieldname": "zero6",
			"fieldtype": "Data",
			"width": 80,
		},
		{
			"label": _(""),
			"fieldname": "",
			"fieldtype": "Data", # 10 spaces
			"width": 50,
		},
		{
			"label": _("Phone"),
			"fieldname": "phone",
			"fieldtype": "Data",
			"width": 100,
		},
		{
			"label": _("Basic"),
			"fieldname": "basic",
			"fieldtype": "Data",
			"width": 120
		},
		{
			"label": _("Allowance Housing"),
			"fieldname": "housing_allowance",
			"fieldtype": "Data",
			"width": 120
		},
		{
			"label": _("Other Earnings"),
			"fieldname": "other_earnings",
			"fieldtype": "Data",
			"width": 120
		},
		{
			"label": _("Dedactions"),
			"fieldname": "dedactions",
			"fieldtype": "Data",
			"width": 120
		},
	]

def get_columns_alaraby():
		return [
				{
					"label": _(""),
					"fieldname": "d",
					"fieldtype": "Data",
					"width": 50,
				},

				{
					"label": _("Total Salary"),
					"fieldname": "month_to_date",
					"fieldtype": "Data",
					"width": 100
				},
				{
					"label": _("Bank Account Number"),
					"fieldname": "bank_ac_no",
					"fieldtype": "Data",
					"width": 150
				},
				{
					"label": _("Employee Name"),
					"fieldname": "first_name",
					"fieldtype": "Data",
					"width": 150
				},
				{
					"label": _("Swift Number"),
					"fieldname": "swift_number",
					"fieldtype": "Data",
					"width": 150
				},
				{
					"label": _("Salary Month"),
					"fieldname": "month",
					"fieldtype": "Data",
					"width": 100
				},
				{
					"label": _("Basic"),
					"fieldname": "basic",
					"fieldtype": "Data",
					"width": 100
				},
				{
					"label": _("Allowance Housing"),
					"fieldname": "housing_allowance",
					"fieldtype": "Data",
					"width": 100
				},
				{
					"label": _("Other Earnings"),
					"fieldname": "other_earnings",
					"fieldtype": "Data",
					"width": 100
				},
				{
					"label": _("Dedactions"),
					"fieldname": "dedactions",
					"fieldtype": "Data",
					"width": 100
				},
				{
					"label": _("Identity"),
					"fieldname": "id_number",
					"fieldtype": "Data",
					"width": 150
				},
				{
					"label": _("Salaries Month"),
					"fieldname": "co_number",
					"fieldtype": "Data",
					"width": 150
				}
			]

