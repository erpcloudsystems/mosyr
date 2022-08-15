import frappe
from frappe.custom.doctype.property_setter.property_setter import make_property_setter

def after_install():
    edit_gender_list()
    prepare_system_accounts()
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

def prepare_system_accounts():
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
                "check_company": 0
            },
            "for_fields": [
                {
                    "fieldname": "payable_account",
                    "doctype": "Expense Claim"
                }
            ]
        }
    ]
    companies = frappe.get_list("Company", fields=["default_currency", "name"])
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

def set_property_setter(new_account, fields):
    # Hide, non-reqd and default
    for fld in fields:
        if not fld["doctype"] or not fld["fieldname"]: continue
        make_property_setter(fld["doctype"], fld["fieldname"], "reqd", 0, "Check", validate_fields_for_doctype=False,)
        # make_property_setter(fld["doctype"], fld["fieldname"], "hidden", 1, "Check", validate_fields_for_doctype=False,)
        make_property_setter(fld["doctype"], fld["fieldname"], "default", new_account, "Text", validate_fields_for_doctype=False,)

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