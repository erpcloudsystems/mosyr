import frappe 
from frappe.utils import nowdate, getdate
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
def check_payment_mode(doc, method):
    if not doc.mode_of_payment or not doc.payment_account:
        payment_account = frappe.db.get_value("Account", {"company": doc.company, "account_type": "Cash"}, "name")
        payment_mode_list = frappe.get_list("Mode of Payment", filters={"type":"Cash"})
        if payment_mode_list:
            doc.mode_of_payment = payment_mode_list[0].name
            doc.payment_account = payment_account
        else:
            company_list = frappe.get_list("Company", fields=["name", "default_cash_account"])
            new_pay_mode = frappe.new_doc("Mode of Payment")
            new_pay_mode.mode_of_payment = "Cash"
            new_pay_mode.enabled = 1
            new_pay_mode.type = "Cash"
            if company_list:
                for company in company_list:
                    new_pay_mode.append("accounts", {
                        "company": company.get("name") or "",
                        "default_account": company.get("default_cash_account") or ""
                    })

            new_pay_mode.save()
            doc.mode_of_payment = new_pay_mode.name
            doc.payment_account = payment_account

@frappe.whitelist()
def set_accounts(doc, method):
    doc.accounts = []
    company_list = frappe.get_list("Company", fields=["name", "default_payroll_payable_account"])
    if company_list:
        for company in company_list:
            doc.append("accounts", {
                "company": company.get("name") or "",
                "account": company.get("default_payroll_payable_account") or ""
            })


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

accounts = [
        {
            "account": {
                "account_name": "Loan Account",
                "parent_account": "Loans and Advances (Assets)",
                "root_type": "Asset"
            },
            "for_fields": [
                {
                    "fieldname": "loan_account",
                    "doctype": "Loan Type"
                }
            ]
        },
        {
            "account": {
                "account_name": "Loan Disbursement",
                "parent_account": "Loans and Advances (Assets)",
                "root_type": "Asset"
            },
            "for_fields": [
                {
                    "fieldname": "disbursement_account",
                    "doctype": "Loan Type"
                }
            ]
        },
        {
            "account": {
                "account_name": "Loan Repayment",
                "parent_account": "Loans and Advances (Assets)",
                "root_type": "Asset"
            },
            "for_fields": [
                {
                    "fieldname": "payment_account",
                    "doctype": "Loan Type"
                }
            ]
        },
        {
            "account": {
                "account_name": "Loan Inreset",
                "parent_account": "Income",
                "root_type": "Income"
            },
            "for_fields": [
                {
                    "fieldname": "interest_income_account",
                    "doctype": "Loan Type",
                }
            ]
        },
        {
            "account": {
                "account_name": "Loan Penalty",
                "parent_account": "Income",
                "root_type": "Income"
            },
            "for_fields": [
                {
                    "fieldname": "penalty_income_account",
                    "doctype": "Loan Type"
                }
            ]
        },
        {
            "account": {
                "account_name": "Loan Write off Account",
                "parent_account": "Expenses",
                "root_type": "Expense"
            },
            "for_fields": [
                {
                    "fieldname": "write_off_account",
                    "doctype": "Loan Write Off"
                }
            ]
        },
        {
            "account": {
                "account_name": "Employee Advances",
                "parent_account": "Loans and Advances (Assets)",
                "root_type": "Asset",
                "check_company": 1,
                "check_company_field": "default_employee_advance_account"
            },
            "for_fields": [
                {
                    "fieldname": "advance_account",
                    "doctype": "Employee Advance"
                }
            ]
        },
        {
            "account": {
                "account_name": "Expense Claim",
                "parent_account": "Accounts Payable",
                "root_type": "Liability",
                "account_type": "Payable",
                "check_company": 0,
                "check_company_field": "default_employee_advance_account"
            },
            "for_fields": [
                {
                    "fieldname": "payable_account",
                    "doctype": "Expense Claim"
                }
            ]
        }
    ]
def set_missing_accounts(doc, method):
    company = frappe.get_list('Company', filters={'name': doc.company}, fields=['name', 'default_currency'])
    if len(company) == 0: return
    args = {
        "company": company.name,
        "account_currency": company.default_currency
    }
    if doc.doctype == "Loan Type":
        set_loan_type_accounts(doc, args)
    elif doc.doctype == "Loan Write Off":
        set_write_off_accounts(doc, args)
    elif doc.doctype == "Employee Advance":
        set_emp_advance_accounts(doc, args)
    elif doc.doctype == "Expense Claim":
        set_expense_claim_accounts(doc, args)

def set_loan_type_accounts(doc, args):
    if not doc.loan_account:
        fltrs = {
            "account_name": "Loan Account",
            "company": doc.company,
        }
        account = frappe.db.get_value("Account", filters=fltrs)
        details = {
            "account_name": "Loan Account",
            "parent_account": "Loans and Advances (Assets)",
            "root_type": "Asset"
        }
        details.update(args)
        if not account:
            account = create_account(**details)
        doc.loan_account = account

    if not doc.disbursement_account:
        fltrs = {
            "account_name": "Loan Disbursement",
            "company": doc.company,
        }
        account = frappe.db.get_value("Account", filters=fltrs)
        details = {
            "account_name": "Loan Disbursement",
            "parent_account": "Loans and Advances (Assets)",
            "root_type": "Asset"
        }
        details.update(args)
        if not account:
            account = create_account(**details)
        doc.disbursement_account = account
    
    if not doc.payment_account:
        fltrs = {
            "account_name": "Loan Repayment",
            "company": doc.company,
        }
        account = frappe.db.get_value("Account", filters=fltrs)
        details = {
            "account_name": "Loan Repayment",
            "parent_account": "Loans and Advances (Assets)",
            "root_type": "Asset"
        }
        details.update(args)
        if not account:
            account = create_account(**details)
        doc.payment_account = account
    
    if not doc.interest_income_account:
        fltrs = {
            "account_name": "Loan Inreset",
            "company": doc.company,
        }
        account = frappe.db.get_value("Account", filters=fltrs)
        details = {
            "account_name": "Loan Inreset",
            "parent_account": "Income",
            "root_type": "Income"
        }
        details.update(args)
        if not account:
            account = create_account(**details)
        doc.interest_income_account = account
    
    if not doc.penalty_income_account:
        fltrs = {
            "account_name": "Loan Penalty",
            "company": doc.company,
        }
        account = frappe.db.get_value("Account", filters=fltrs)
        details = {
            "account_name": "Loan Penalty",
            "parent_account": "Income",
            "root_type": "Income"
        }
        details.update(args)
        if not account:
            account = create_account(**details)
        doc.penalty_income_account = account
    
    # manual validate accounts
    if  not doc.loan_account or not doc.disbursement_account or doc.payment_account or not doc.interest_income_account or not doc.penalty_income_account:
        frappe.throw(_("Something wen wrong!, call support to fix"))

def set_write_off_accounts(doc, args):
    if not doc.write_off_account:
        fltrs = {
            "account_name": "Loan Write off Account",
            "company": doc.company,
        }
        account = frappe.db.get_value("Account", filters=fltrs)

        details = {
            "account_name": "Loan Write off Account",
            "parent_account": "Expenses",
            "root_type": "Expense"
        }
        details.update(args)
        if not account:
            account = create_account(**details)
        doc.write_off_account = account
    
    if not doc.write_off_account:
        frappe.throw(_("Something wen wrong!, call support to fix"))

def set_emp_advance_accounts(doc, args):
    if not doc.advance_account:
        fltrs = {
            "account_name": "Employee Advances",
            "company": doc.company,
        }
        account = frappe.db.get_value("Account", filters=fltrs)

        details = {
            "account_name": "Employee Advances",
            "parent_account": "Loans and Advances (Assets)",
            "root_type": "Asset",
            "check_company": 1,
            "check_company_field": "default_employee_advance_account"
        }
        details.update(args)
        if not account:
            account = create_account(**details)
        doc.advance_account = account
    
    if not doc.advance_account:
        frappe.throw(_("Something wen wrong!, call support to fix"))

def set_expense_claim_accounts(doc, args):
    if not doc.payable_account:
        fltrs = {
            "account_name": "Expense Claim",
            "company": doc.company,
        }
        account = frappe.db.get_value("Account", filters=fltrs)

        details = {
            "account_name": "Expense Claim",
            "parent_account": "Accounts Payable",
            "root_type": "Liability",
            "account_type": "Payable",
            "check_company": 0
        }
        details.update(args)
        if not account:
            account = create_account(**details)
        doc.payable_account = account
    
    if not doc.payable_account:
        frappe.throw(_("Something wen wrong!, call support to fix"))
