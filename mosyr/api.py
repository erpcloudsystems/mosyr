
import json

import frappe 
from frappe.utils import nowdate, getdate, today, flt, cint, date_diff
from frappe import _
from hijri_converter import Hijri, Gregorian
from json import loads

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
            
            if log_id:
                # Extract data from log
                employee_field_value = log.get("employee_field_value", False)
                device_id = log.get("device_id", "")
                timestamp = log.get("timestamp", False)
                log_type = log.get("log_type", '-')
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
                if not isinstance(log_type, str):
                    log_type = None
                else:
                    log_type = f'{log_type}'.upper()
                
                if log_type in ['0', 0, 'IN']:
                    log_type = "IN"
                elif log_type in ['1', 1, 'OUT']:
                    log_type = "OUT"
                else:
                    log_type = None

                frappe.logger("mosyr.biometric").debug({"resuest_data":" [!] logs_data"})
                doc = frappe.new_doc("Employee Checkin")
                doc.employee = f'{employee.name}'
                doc.employee_name = f'{employee.employee_name}'
                doc.time = timestamp
                doc.device_id = f'{device_id}'
                doc.log_type = log_type
                try:
                    doc.insert(ignore_permissions=True)
                    success.append({
                        "log_id": log_id,
                        "result": "success"
                    })
                except Exception as e:
                    success.append({
                        "log_id": log_id,
                        "result": e
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

@frappe.whitelist()
def get_doctypes(doctype, txt, searchfield, start, page_len, filters):
    result = frappe.db.sql("""
        select doc_name,parent_name from `tabSideBar Item Table`
        where doc_name LIKE %(txt)s or parent_name LIKE %(txt)s""" ,{"txt": "%" + txt + "%"})
    return result

def set_user_type(doc,method):
    if doc.email != "Administrator":
        doc.user_type = "Employee Self Service"
        doc.save()

def set_employee_number(doc,method):
    doc.employee_number = doc.number

def set_date_of_joining(doc,method):
    doc.date_of_joining = doc.custom_date_of_joining

@frappe.whitelist()
def get_roles(doctype, txt, searchfield, start, page_len, filters):
    result = frappe.db.sql("""
        select name from `tabRole`
        where is_custom = 1 and name LIKE %(txt)s  LIKE %(txt)s""" ,{"txt": "%" + txt + "%"})
    return result

def validate_remaining_loan(doc,method):
    loan_doc = frappe.get_doc("Loan", doc.against_loan)
    if loan_doc.total_payment - loan_doc.total_amount_paid == 0:
        frappe.throw(f"The Remaining in this loan equal zero")
    if loan_doc.total_amount_paid + doc.amount_paid >  loan_doc.total_payment:
        frappe.throw(f"Remaining in your loan is {loan_doc.total_amount_remaining}, Not {doc.amount_paid}, Please change the amount paid to {loan_doc.total_amount_remaining}")

@frappe.whitelist()
def get_repayment_schedule(doc_name):
    repayment_schedule = frappe.db.sql(f"""
        SELECT rs.idx, rs.name, rs.paid_amount, rs.total_payment, rs.payment_date, rs.payment_date as new_payment_date
        FROM `tabLoan` l 
        LEFT JOIN `tabRepayment Schedule` rs ON rs.parent=l.name 
        WHERE rs.parent='{doc_name}' AND rs.total_payment>rs.paid_amount AND l.docstatus=1
        ORDER BY rs.payment_date""", as_dict=1)

    return repayment_schedule

@frappe.whitelist()
def set_new_date_in_repayment(rows, doc_name):
    loan_doc = frappe.db.exists("Loan", doc_name)
    if not loan_doc:
        frappe.throw(_("Loan {} not found".format((doc_name))))
        return
    try:
        loan_doc = frappe.get_doc("Loan", doc_name)
        rows = loads(rows)
        errors = []
        for tidx, row in enumerate(rows, 1):
            new_payment_date = row.get("new_date", "")
            repayment = frappe.get_doc("Repayment Schedule", row.get("row_name", ""))
            if date_diff(repayment.payment_date, new_payment_date) > 0:
                errors.append({
                    "date": repayment.payment_date,
                    "idx": tidx
                })
        
        if len(errors) > 0:
            errors_str = ''
            for err in errors:
                errors_str += "Choose Date after {} in row {}".format(err.get("date", ""), err.get("idx", ""))+"<br>"
            frappe.msgprint(_(errors_str))
            return "err"
        
        for tidx, row in enumerate(rows, 1):
            new_payment_date = row.get("new_date", "")
            repayment = frappe.get_doc("Repayment Schedule", row.get("row_name", ""))
            repayment.db_set("payment_date", new_payment_date, update_modified=False)
        reorder_payments_by_dates(loan_doc.name)
        
    except Exception as e:
        frappe.throw(_("Incorrect format"))

def reorder_payments_by_dates(row_parent):
    repayment_schedule = frappe.db.sql(f"""
           SELECT name 
           FROM `tabRepayment Schedule` 
           WHERE parent='{row_parent}' ORDER BY payment_date""", as_dict=1)
    for new_idx, row in enumerate(repayment_schedule, 1):
        doc = frappe.get_doc("Repayment Schedule" ,row.name)
        doc.db_set("idx", new_idx, update_modified=False)


@frappe.whitelist()
def get_users(doctype, txt, searchfield, start, page_len, filters):
    result = frappe.db.sql("""
        select name, full_name from `tabUser`
        where name LIKE %(txt)s and user_type <> 'SaaS Manager' and name not in ('Guest', 'Administrator', 'support@mosyr.io') """ ,{"txt": "%" + txt + "%"})
    return result

def update_user_type_limits(doc,method):
    from frappe.installer import update_site_config
    types = frappe.get_list("User Type", filters={'is_standard': 0})
    user_type_limit = {}
    for utype in types:
        user_type_limit.setdefault(frappe.scrub(utype.name), 10000)
    update_site_config("user_type_doctype_limit", user_type_limit)