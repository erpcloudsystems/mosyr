import frappe
from frappe.custom.doctype.property_setter.property_setter import make_property_setter

from mosyr import mosyr_accounts, mosyr_mode_payments

def after_install():
    edit_gender_list()
    prepare_mode_payments()
    prepare_system_accounts()
    hide_accounts_fields()
    
    # create_salary_components()
    # create_salary_structure()
    # frappe.db.commit()

def edit_gender_list():
    genders_to_del = frappe.get_list("Gender", filters={"name": ["not in", ["Female", "Male"]]})
    for gender in genders_to_del:
        try:
            gender = frappe.get_doc("Gender", gender.name)
            gender.delete()
        except:
            pass
        frappe.db.commit()

def prepare_system_accounts():
    companies = frappe.get_list("Company", fields=["default_currency", "name"])
    setup_loan_accounts(companies)
    setup_loan_type_accounts(companies)
    setup_loan_writeoff_accounts(companies)

    setup_employee_advance_accounts(companies)
    setup_expense_claim_accounts(companies)

    setup_salary_component_accounts()

def setup_loan_accounts(companies):
    accounts = mosyr_accounts.get('LoanType', [])
    mode_payments = mosyr_mode_payments.get('LoanType', {})
    for company in companies:
        args = {
            "company": company.name,
            "account_currency": company.default_currency
        }
        for account in accounts:
            args.update(account["account"])
            new_account = create_account(**args)
            if new_account:
                set_property_setter(new_account, account["for_fields"])
    
    new_mode = create_mode_payment(mode_payments["type"], mode_payments["title"])
    if new_mode:
        set_property_setter(new_mode, mode_payments["for_fields"])

def setup_loan_type_accounts(companies):
    accounts = mosyr_accounts.get('LoanType', [])
    mode_payments = mosyr_mode_payments.get('LoanType', {})
    for company in companies:
        args = {
            "company": company.name,
            "account_currency": company.default_currency
        }
        for account in accounts:
            args.update(account["account"])
            new_account = create_account(**args)
            if new_account:
                set_property_setter(new_account, account["for_fields"])
    new_mode = create_mode_payment(mode_payments["type"], mode_payments["title"])
    if new_mode:
        set_property_setter(new_mode, mode_payments["for_fields"])

def setup_loan_writeoff_accounts(companies):
    accounts = mosyr_accounts.get('LoanWriteOff', [])
    for company in companies:
        args = {
            "company": company.name,
            "account_currency": company.default_currency
        }
        for account in accounts:
            args.update(account["account"])
            new_account = create_account(**args)
            if new_account:
                set_property_setter(new_account, account["for_fields"])

def setup_employee_advance_accounts(companies):
    accounts = mosyr_accounts.get('EmployeeAdvance', [])
    for company in companies:
        args = {
            "company": company.name,
            "account_currency": company.default_currency
        }
        for account in accounts:
            args.update(account["account"])
            new_account = create_account(**args)
            if new_account:
                set_property_setter(new_account, account["for_fields"])

def setup_expense_claim_accounts(companies):
    accounts = mosyr_accounts.get('ExpenseClaim', [])
    for company in companies:
        args = {
            "company": company.name,
            "account_currency": company.default_currency
        }
        for account in accounts:
            args.update(account["account"])
            new_account = create_account(**args)
            if new_account:
                set_property_setter(new_account, account["for_fields"])

def setup_salary_component_accounts():
    sal_comps = frappe.get_list('Salary Component')
    for sal_comp in sal_comps:
        sal_comp = frappe.get_doc('Salary Component', sal_comp.name)
        sal_comp.save()

def setup_salary_structure_accounts():
    # Use account from payment entry
    mode_payments = mosyr_mode_payments.get('SalaryStructure', {})
    new_mode = create_mode_payment(mode_payments["type"], mode_payments["title"])
    # if new_mode:
    #     set_property_setter(new_mode, mode_payments["for_fields"])

def prepare_mode_payments():
    # to Set accounts in old data
    mods = frappe.get_list('Mode of Payment')
    for mod in mods:
        mod = frappe.get_doc('Mode of Payment', mod.name)
        mod.save()

    # for loans and hr
    create_mode_payment("Bank", "Loan Payment")
    create_mode_payment("Bank", "Advance Payment")
    create_mode_payment("Bank", "Salary Payment")

def create_mode_payment(mode_type, title):
    mode = frappe.db.exists("Mode of Payment", title)
    if not mode:
        mop = frappe.new_doc("Mode of Payment")
        mop.mode_of_payment = title
        mop.type = mode_type
        mop.save()
        mode = mop.name
    return mode

def hide_accounts_fields():
    make_property_setter("Mode of Payment" , "accounts", "hidden", 1, "Check", validate_fields_for_doctype=False,)
    make_property_setter("Salary Component", "accounts", "hidden", 1, "Check", validate_fields_for_doctype=False,)
    
    make_property_setter("Salary Structure", "account" , "hidden", 1, "Check", validate_fields_for_doctype=False,)
    make_property_setter("Salary Structure Assignment", "payroll_payable_account" , "hidden", 1, "Check", validate_fields_for_doctype=False,)
    

def set_property_setter(value, fields):
    # Hide, non-reqd and default
    for fld in fields:
        if not fld["doctype"] or not fld["fieldname"]: continue
        make_property_setter(fld["doctype"], fld["fieldname"], "reqd", 0, "Check", validate_fields_for_doctype=False,)
        make_property_setter(fld["doctype"], fld["fieldname"], "hidden", 1, "Check", validate_fields_for_doctype=False,)
        make_property_setter(fld["doctype"], fld["fieldname"], "default", value, "Text", validate_fields_for_doctype=False,)

def create_account(**kwargs):
    if kwargs.get("check_company") and kwargs.get("check_company_field"):
        try:
            val = frappe.get_value("Company",  kwargs.get("company"), kwargs.get("check_company_field")) or None
            if val: return val
        except: pass
    
    fltrs = {
        "account_name": kwargs.get("account_name"),
        "company": kwargs.get("company")
    }
    
    if kwargs.get("account_type", False):
        fltrs.update({
            "account_type": kwargs.get("account_type", "")
        })
    account = frappe.db.get_value(
        "Account", filters=fltrs
    )
    
    if account:
        return account
    else:
        parent_name = frappe.db.get_value(
            "Account", filters={
                "account_name": kwargs.get("parent_account"),
                "company": kwargs.get("company"),
                "is_group": 1
            }
        )
        if not parent_name:
            parent_name = frappe.db.get_value(
                "Account", filters={
                    "company": kwargs.get("company"),
                    "root_type": kwargs.get("root_type"),
                    "is_group": 1
                    }, order_by="creation"
                )
        if not parent_name:
            return None
        account = frappe.get_doc(
            dict(
                doctype="Account",
                account_name=kwargs.get("account_name"),
                account_type=kwargs.get("account_type", False),
                parent_account=parent_name,
                company=kwargs.get("company"),
                account_currency=kwargs.get("account_currency"),
            )
        )

        account.save()
        return account.name

def create_salary_components():
    print("[*] Add Salary Components")
    base_components = [
        {"component": "Basic",                 "abbr": "B"},
        {"component": "Housing",               "abbr": "H"},
        {"component": "Allowance Housing",     "abbr":"AH"},
        {"component": "Allowance Worknatural", "abbr":"AW"},
        {"component": "Allowance Other",       "abbr":"AO"},
        {"component": "Allowance Phone",       "abbr":"AP"},
        {"component": "Allowance Trans",       "abbr":"AT"},
        {"component": "Allowance Living",      "abbr":"AL"}]
        # Benefit Components
    benefit_components = [
        {"component": "Back Pay",              "abbr":"BP"},
        {"component": "Bonus",                 "abbr":"BO"},
        {"component": "Overtime",              "abbr":"OT"},
        {"component": "Business Trip",         "abbr":"BT"},
        {"component": "Commission",            "abbr":"COM"}]
    
    deduction_components = [
        {"component": "Deduction",              "abbr":"DD"}]
                 
    for component in base_components:
        salary_component = component["component"]
        if not frappe.db.exists("Salary Component", salary_component):
            salary_component_abbr = component["abbr"]
            component_type = "Earning"
            salary_component_doc = frappe.new_doc("Salary Component")
            salary_component_doc.update({
                "salary_component": salary_component,
                "salary_component_abbr": salary_component_abbr,
                "type": component_type})
            salary_component_doc.save()
    
    for component in benefit_components:
        salary_component = component["component"]
        if not frappe.db.exists("Salary Component", salary_component):
            salary_component_abbr = component["abbr"]
            component_type = "Earning"
            salary_component_doc = frappe.new_doc("Salary Component")
            salary_component_doc.update({
                "salary_component": salary_component,
                "salary_component_abbr": salary_component_abbr,
                "type": component_type,
                "is_flexible_benefit": 1
            })
            salary_component_doc.save()
    
    for component in deduction_components:
        salary_component = component["component"]
        if not frappe.db.exists("Salary Component", salary_component):
            salary_component_abbr = component["abbr"]
            component_type = "Deduction"
            salary_component_doc = frappe.new_doc("Salary Component")
            salary_component_doc.update({
                "salary_component": salary_component,
                "salary_component_abbr": salary_component_abbr,
                "type": component_type
            })
            salary_component_doc.save()
    frappe.db.commit()

def create_salary_structure():
    components = [
        {"component": "Housing",               "abbr": "H"},
        {"component": "Allowance Housing",     "abbr":"AH"},
        {"component": "Allowance Worknatural", "abbr":"AW"},
        {"component": "Allowance Other",       "abbr":"AO"},
        {"component": "Allowance Phone",       "abbr":"AP"},
        {"component": "Allowance Trans",       "abbr":"AT"},
        {"component": "Allowance Living",      "abbr":"AL"}]
    salary_structure_doc = frappe.new_doc("Salary Structure")
    company = frappe.defaults.get_global_default("company")
    company = frappe.get_doc("Company", company)
    salary_structure_doc.update({
        "__newname": "Base Salary Structure",
        "is_active": "Yes",
        "payroll_frequency": "Monthly",
        "company": company.name,
        "currency": company.default_currency
    })

    for component in components:
        salary_component_abbr = component["abbr"]
        salary_component = component["component"]
        salary_structure_doc.append("earnings", {
            "salary_component": salary_component,
            "abbr": salary_component_abbr
        })
    salary_structure_doc.save()
    salary_structure_doc.submit()
