
import frappe 
from frappe.utils import nowdate, getdate, today
from frappe import _
from hijri_converter import Hijri, Gregorian
from mosyr.install import create_account

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
    if not doc.s_subscription_date: return
    if doc.s_subscription_date > doc.date_of_joining:
        frappe.throw(_("Date of Insurance Subscription must be before Joining of Birth"))
    comapny_data = frappe.get_list("Company Controller", filters={'company': doc.company}, fields=['*'])
    if len(comapny_data) > 0:
        comapny_data = comapny_data[0]
        if doc.social_insurance_type == "Saudi":
            doc.risk_on_employee = 0
            doc.risk_on_company = 0
            doc.pension_on_employee = comapny_data.pension_percentage_on_employee
            doc.pension_on_company = comapny_data.pension_percentage_on_company
        elif doc.social_insurance_type == "Non Saudi":
            doc.risk_on_employee = comapny_data.risk_percentage_on_employee
            doc.risk_on_company = comapny_data.risk_percentage_on_company
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