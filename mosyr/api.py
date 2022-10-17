
import json

import frappe 
from frappe.utils import nowdate, getdate, today, flt, cint
from frappe import _
from hijri_converter import Hijri, Gregorian

def _get_employee_from_user(user):
    employee_docname = frappe.db.exists(
        {'doctype': 'Employee', 'user_id': user})

    if not employee_docname:
        frappe.throw(_('Employee NOT Found'))

    if employee_docname:
        return frappe.get_doc('Employee', employee_docname[0][0]).name
    return None

@frappe.whitelist()
def get_will_expire_docs():
    notify_settings = frappe.get_doc("HR Notification Settings")
    now = nowdate()

    # Get Employee Contracts that will be expired 
    expire_contracts = frappe.db.sql("""
        SELECT 
            name
        FROM
            `tabEmployee Contract`
        WHERE 
            docstatus = 1 AND contract_status = "Valid" AND DATEDIFF(contract_end_date, %(now)s) BETWEEN 0 AND %(diff_day)s
    """, {"now":now, "diff_day": notify_settings.for_contracts_notice_me_before}, as_dict=True)

    # Get Identities that will be expired 
    expire_identities = frappe.db.sql("""
        SELECT 
            name
        FROM
            `tabIdentity`
        WHERE 
            DATEDIFF(expire_date, %(now)s) BETWEEN 0 AND %(diff_day)s
    """, {"now":now, "diff_day": notify_settings.for_ids__notice_me_before}, as_dict=True)

    # Get Passports that will be expired 
    expire_passports = frappe.db.sql("""
        SELECT 
            name
        FROM
            `tabPassport`
        WHERE 
            DATEDIFF(passport_expire, %(now)s) BETWEEN 0 AND %(diff_day)s
    """, {"now":now, "diff_day": notify_settings.for_passports_notice_me_before}, as_dict=True)

    # Get Insurances that will be expired 
    expire_Insurances = frappe.db.sql("""
        SELECT 
            name, health_insurance_no
        FROM
            `tabEmployee`
        WHERE 
            DATEDIFF(insurance_card_expire, %(now)s) BETWEEN 0 AND %(diff_day)s
    """, {"now":now, "diff_day": notify_settings.for_insurance_notice_me_before}, as_dict=True)

    return {
            "expire_contracts":expire_contracts, 
            "expire_identities":expire_identities, 
            "expire_passports":expire_passports,
            "expire_Insurances": expire_Insurances
        }

@frappe.whitelist()
def show_expier_docs():
    notify_settings = frappe.get_doc("HR Notification Settings")
    if notify_settings.notify_after_login:
        result = get_will_expire_docs()
        expire_contracts = result.get("expire_contracts")
        expire_identities = result.get("expire_identities")
        expire_passports = result.get("expire_passports")
        expire_Insurances = result.get("expire_Insurances")
        
        msg = ""
        print_msg = False

        if len(expire_contracts): 
            msg += f"{len(expire_contracts)} Contracts Expire Within {notify_settings.for_contracts_notice_me_before} <br>"
            print_msg = True

        if len(expire_identities):
            msg += f" {len(expire_identities)} ID's Expire Within {notify_settings.for_ids__notice_me_before} <br> "
            print_msg = True

        if len(expire_passports):
            msg += f"{len(expire_passports)} Passport Expire Within {notify_settings.for_passports_notice_me_before} <br>"
            print_msg = True

        if len(expire_Insurances):
            msg += f"{len(expire_Insurances)} Insurances Expire Within {notify_settings.for_insurance_notice_me_before}"
            print_msg = True
        
        if print_msg:
            frappe.msgprint(_(msg), title= _('Employee Docs that will be expired'), indicator= 'orange')

@frappe.whitelist()
def set_employee_approvers(department):
    ''' Fetch Aprrovers From Department & Set it in Employee Page Depends on Department Field'''
    if department:
        leave_approver = expense_approver = shift_req_approver = ''
        department = frappe.get_doc('Department', department)
        
        if len(department.leave_approvers):
            leave_approver = department.leave_approvers[0].approver
            leave_approver = leave_approver
        if len(department.expense_approvers):
            expense_approver = department.expense_approvers[0].approver
            expense_approver = expense_approver

        if len(department.shift_request_approver):
            shift_req_approver = department.shift_request_approver[0].approver
            shift_req_approver = shift_req_approver

        return leave_approver, expense_approver, shift_req_approver

@frappe.whitelist()
def convert_date(gregorian_date=None, hijri_date=None):
    if gregorian_date:
        gd, gm, gy = getdate(gregorian_date).day, getdate(gregorian_date).month, getdate(gregorian_date).year
        hijri = Gregorian(gy, gm, gd).to_hijri()
        return str(hijri)

    if hijri_date:
        hd, hm, hy = getdate(hijri_date).day, getdate(hijri_date).month, getdate(hijri_date).year
        gregorian = Hijri(hy, hm, hd ).to_gregorian()
        return str(gregorian)

def setup_mode_accounts(doc, method):
    from mosyr.install import create_account
    companies = frappe.get_list('Company', fields=['name', 'default_currency', 'default_bank_account', 'default_cash_account'])
    doc.accounts = []
    
    account_name = "Bank Account"
    account_type = "Bank"
    parent_account = "Bank Accounts"
    
    if f"{doc.name}".lower == "Salary Payment".lower():
        account_name = "Salary"
        account_type = "Indirect Expenses"
        parent_account = "Accounts Payable"

    for company in companies:
        if doc.type == "Bank":
            if company.default_bank_account:
                doc.append('accounts', {
                    'company': company.name,
                    'default_account': company.default_bank_account,
                })
            else:
                new_account = create_account(**{
                    "account_name": account_name,
                    "account_type": account_type,
                    "parent_account": parent_account,
                    "root_type": "Asset",
                    "company": company.name,
                    "account_currency": company.default_currency
                })
                if new_account:
                    doc.append('accounts', {
                        'company': company.name,
                        'default_account': new_account
                    })
        else:
            if company.default_cash_account:
                doc.append('accounts', {
                    'company': company.name,
                    'default_account': company.default_cash_account,
                })
            else:
                new_account = create_account(**{
                    "account_name": "Cash",
                    "account_type": "Cash",
                    "parent_account": "Cash In Hand",
                    "root_type": "Asset",
                    "company": company.name,
                    "account_currency": company.default_currency
                })
                if new_account:
                    doc.append('accounts', {
                        'company': company.name,
                        'default_account': new_account,
                    })

def setup_components_accounts(doc, method):
    from mosyr.install import create_account
    companies = frappe.get_list('Company', fields=['name', 'default_currency', 'default_payroll_payable_account'])
    doc.accounts = []
    for company in companies:
        new_account = create_account(**{
                "account_name": "Salary",
                "parent_account": "Indirect Expenses",
                "root_type": "Expense",
                "company": company.name,
                "account_currency": company.default_currency
            })
        if new_account:
            doc.append('accounts', {
                'company': company.name,
                'account': new_account,
            })

def validate_social_insurance(doc, method):
    comapny_data = frappe.get_list("Company Controller", filters={'company': doc.company}, fields=['*'])
    social_type = "Saudi" if f"{doc.nationality}".lower() in ["saudi", "سعودي", "سعودى"] else "Non Saudi"
    if len(comapny_data) > 0:
        comapny_data = comapny_data[0]
        doc.social_insurance_type = social_type
        
        if social_type == "Saudi":
            doc.risk_on_employee = 0
            doc.risk_on_company = 0
            doc.pension_on_employee = flt(comapny_data.pension_percentage_on_employee)
            doc.pension_on_company = flt(comapny_data.pension_percentage_on_company)
        else:
            doc.risk_on_employee = flt(comapny_data.risk_percentage_on_employee)
            doc.risk_on_company = flt(comapny_data.risk_percentage_on_company)
            doc.pension_on_employee = 0
            doc.pension_on_company = 0
    else:
        doc.social_insurance_type = "Other"
        doc.risk_on_employee = 0
        doc.risk_on_company = 0
        doc.pension_on_employee = 0
        doc.pension_on_company = 0

def notify_expired_dates(doc, method):
    emp = doc
    # Check Employee Insurance
    if getdate(emp.insurance_card_expire) < getdate(today()):
        emp.db_set("notify_insurance_e", 1, update_modified=False)

    # Check ID's
    need_update = False
    for eid in emp.identity:
        if getdate(eid.expire_date) < getdate(today()):
            need_update = True
    if need_update: emp.db_set("notify_id", 1, update_modified=False)

    # Check Passports
    need_update = False
    for epass in emp.passport:
        if getdate(epass.passport_expire) < getdate(today()):
            need_update = True
    if need_update: emp.db_set("notify_passport", 1, update_modified=False)

    # Check Dependent Insurance
    need_update = False
    for edep in emp.dependent:
        if getdate(edep.insurance_card_expire) < getdate(today()):
            need_update = True
    if need_update: emp.db_set("notify_insurance_d", 1, update_modified=False)

def check_other_annual_leaves(doc, method):
    if cint(doc.is_annual_leave) == 1 and cint(doc.allow_encashment) == 1:
        leaves = frappe.get_list("Leave Type", filters={"is_annual_leave": 1, "allow_encashment": 1})
        print(leaves)
        #frappe.db.sql("""SELECT name FROM `tabLeave Type` WHERE is_annual_leave=1 AND allow_encashment=1""")
        if len(leaves) >= 1:
            msg_str = ""
            for l in leaves:
                msg_str += "<li>{}</li>".format(_(l['name']))
            msg_str = "<ul>" + msg_str + "</ul>"
            frappe.throw(_("Only One Annual Leave allowed to be encashment check.")+msg_str)

def set_employee_gender(doc, method):
    gender_doc = frappe.db.exists("Gender", doc.e_gender)
    if gender_doc:
        doc.gender = gender_doc
    else:
        gender_doc = frappe.new_doc("Gender")
        gender_doc.gender = doc.e_gender
        gender_doc.save()
        frappe.db.commit()
        doc.gender = gender_doc.name

@frappe.whitelist(allow_guest=True)
def add_employee_log(*args, **kwargs):
    logs_data =frappe.request.data.decode()
    if isinstance(logs_data, str):
        logs_data = json.loads(logs_data)
    logs_data = logs_data.get("logs", [])
    errors = []
    success = []
    if isinstance(logs_data, list):
        for log in logs_data:
            log_id = log.get("log_id", False)
            device_id = log.get("device_id", "")
            if log_id:
                employee_field_value = log.get("employee_field_value", False)
                timestamp = log.get("timestamp", False)
                if not employee_field_value or not timestamp:
                    errors.append({
                        "log_id": log_id,
                        "result": "Employee Id or Chickin datetime"
                    })
                    continue
                employee = frappe.db.get_values(
                    "Employee",{"attendance_device_id": employee_field_value},
                    ["name", "employee_name", "attendance_device_id"], as_dict=True,)
                if employee:
                    employee = employee[0]
                else:
                    errors.append({
                        "log_id": log_id,
                        "result": "no employee found for {}".format(employee_field_value or "")
                    })
                    continue

                frappe.logger("mosyr.biometric").debug({"resuest_data":" [!] logs_data"})
                doc = frappe.new_doc("Employee Checkin")
                doc.employee = employee.name
                doc.employee_name = employee.employee_name
                doc.time = timestamp
                doc.device_id = device_id
                doc.log_type = None
                doc.insert(ignore_permissions=True)
                success.append({
                    "log_id": log_id,
                    "result": "success"
                })
    return {
        "errors": errors,
        "success": success,
    }

def translate_employee(doc,method):
    tr = False
    if doc.is_new():
        tr = frappe.new_doc("Translation")
    else:
        old_doc = doc.get_doc_before_save()
        if doc.full_name_en and doc.full_name_en != old_doc.full_name_en:
            tr = frappe.new_doc("Translation")
    if not tr: return

    tr.language = "en"
    tr.source_text = doc.first_name
    tr.translated_text = doc.full_name_en
    tr.save()
