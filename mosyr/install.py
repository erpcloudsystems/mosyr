import frappe
from frappe.custom.doctype.property_setter.property_setter import make_property_setter
from mosyr import (
    create_account,
    create_cost_center,
    create_mode_payment,
    create_bank_account,
    update_fields_props,
)

risk_insurance_components = {
    "Risk On Company": {
        "amount": 0.0,
        "amount_based_on_formula": 1,
        "condition": "",
        "create_separate_payment_entry_against_benefit_claim": 0,
        "deduct_full_tax_on_selected_payroll_date": 0,
        "depends_on_payment_days": 0,
        "description": "",
        "disabled": 0,
        "do_not_include_in_total": 1,
        "exempted_from_income_tax": 0,
        "formula": "",
        "is_flexible_benefit": 0,
        "is_income_tax_component": 0,
        "is_tax_applicable": 1,
        "max_benefit_amount": 0.0,
        "only_tax_impact": 0,
        "pay_against_benefit_claim": 0,
        "round_to_the_nearest_integer": 0,
        "salary_component_abbr": "RCD",
        "statistical_component": 0,
        "type": "Deduction",
        "variable_based_on_taxable_salary": 0,
    },
    "Employee Pension Insurance": {
        "amount": 0.0,
        "amount_based_on_formula": 0,
        "condition": "",
        "create_separate_payment_entry_against_benefit_claim": 0,
        "deduct_full_tax_on_selected_payroll_date": 0,
        "depends_on_payment_days": 0,
        "description": "",
        "disabled": 0,
        "do_not_include_in_total": 0,
        "exempted_from_income_tax": 0,
        "formula": "",
        "is_flexible_benefit": 0,
        "is_income_tax_component": 0,
        "is_tax_applicable": 1,
        "max_benefit_amount": 0.0,
        "name": "Employee Pension Insurance",
        "only_tax_impact": 0,
        "pay_against_benefit_claim": 0,
        "round_to_the_nearest_integer": 0,
        "salary_component_abbr": "EPD",
        "statistical_component": 0,
        "type": "Deduction",
        "variable_based_on_taxable_salary": 0,
    },
    "Company Pension Insurance": {
        "amount": 0.0,
        "amount_based_on_formula": 0,
        "condition": "",
        "create_separate_payment_entry_against_benefit_claim": 0,
        "deduct_full_tax_on_selected_payroll_date": 0,
        "depends_on_payment_days": 0,
        "description": "",
        "disabled": 0,
        "do_not_include_in_total": 1,
        "exempted_from_income_tax": 0,
        "formula": "",
        "is_flexible_benefit": 0,
        "is_income_tax_component": 0,
        "is_tax_applicable": 1,
        "max_benefit_amount": 0.0,
        "only_tax_impact": 0,
        "pay_against_benefit_claim": 0,
        "round_to_the_nearest_integer": 0,
        "salary_component_abbr": "CPD",
        "statistical_component": 0,
        "type": "Deduction",
        "variable_based_on_taxable_salary": 0,
    },
    "Risk On Employee": {
        "amount": 0.0,
        "amount_based_on_formula": 1,
        "condition": "",
        "create_separate_payment_entry_against_benefit_claim": 0,
        "deduct_full_tax_on_selected_payroll_date": 0,
        "depends_on_payment_days": 0,
        "description": "",
        "disabled": 0,
        "do_not_include_in_total": 0,
        "exempted_from_income_tax": 0,
        "formula": "",
        "is_flexible_benefit": 0,
        "is_income_tax_component": 0,
        "is_tax_applicable": 1,
        "max_benefit_amount": 0.0,
        "only_tax_impact": 0,
        "pay_against_benefit_claim": 0,
        "round_to_the_nearest_integer": 0,
        "salary_component": "Risk On Employee",
        "salary_component_abbr": "RED",
        "statistical_component": 0,
        "type": "Deduction",
        "variable_based_on_taxable_salary": 0,
    },
}


def after_install():
    edit_gender_list()

    create_dafault_mode_of_payments()
    create_risk_insurance_components()
    companies = frappe.get_list("Company")
    create_dafault_bank_accounts(companies)
    create_dafault_accounts(companies)
    create_default_cost_centers(companies)
    hide_accounts_and_taxs_from_system()
    set_home_page_login()
    
    frappe.db.commit()
    add_permission_create_custom_field()

def add_permission_create_custom_field():
    frappe.get_doc(
        {
            "doctype": "Custom DocPerm",
            "role": "SaaS Manager",
            "read": 1,
            "write": 1,
            "create": 1,
            "delete": 1,
            "submit": 1,
            "cancel": 1,
            "amend": 0,
            "parent": "Custom Field",
            "if_owner": 0
        }
    ).insert(ignore_permissions=True)
    frappe.get_doc(
        {
            "doctype": "Custom DocPerm",
            "role": "SaaS Manager",
            "read": 1,
            "write": 1,
            "create": 1,
            "delete": 1,
            "submit": 1,
            "cancel": 1,
            "amend": 1,
            "parent": "Role",
            "if_owner": 0
        }
    ).insert(ignore_permissions=True)

def add_permission_read():
    add_permission("Domain", "Saas Manager", permlevel=0, ptype=None)

def edit_gender_list():
    genders_to_del = frappe.get_list(
        "Gender", filters={"name": ["not in", ["Female", "Male"]]}
    )
    for gender in genders_to_del:
        try:
            gender = frappe.get_doc("Gender", gender.name)
            gender.delete()
        except:
            pass
        frappe.db.commit()


def create_dafault_bank_accounts(companies):
    for company in companies:
        create_bank_account(company.name)


def create_dafault_accounts(companies):
    for company in companies:
        create_account(
            "Employees Advances",
            company.name,
            "Loans and Advances (Assets)",
            "Asset",
            "Payable",
            True,
            "default_employee_advance_account",
        )
        create_account("Expense Claims", company.name, "Expenses", "Expense", "", False)
        create_account(
            "Expense Payable",
            company.name,
            "Accounts Payable",
            "Liability",
            "Payable",
            True,
            "default_payable_account",
        )
        create_account(
            "Loans Account",
            company.name,
            "Loans and Advances (Assets)",
            "Asset",
            "",
            False,
        )
        create_account(
            "Loans Disbursement",
            company.name,
            "Loans and Advances (Assets)",
            "Asset",
            "",
            False,
        )
        create_account(
            "Loans Repayment",
            company.name,
            "Loans and Advances (Assets)",
            "Asset",
            "",
            False,
        )
        create_account("Loans Inreset", company.name, "Income", "Income", "", False)
        create_account("Loans Penalty", company.name, "Income", "Income", "", False)
        create_account(
            "Loans Write Off", company.name, "Expenses", "Expense", "", False
        )
        create_account(
            "Payroll Payable",
            company.name,
            "Accounts Payable",
            "Liability",
            "",
            True,
            "default_payroll_payable_account",
        )
        create_account(
            "Payroll Payment",
            company.name,
            "Loans and Advances (Assets)",
            "Asset",
            "Bank",
            False,
        )

    # Setup For mode of payments
    for mop in frappe.get_list("Mode of Payment"):
        mop = frappe.get_doc("Mode of Payment", mop.name)
        mop.save()

    # Setup For salayr components
    for sc in frappe.get_list("Salary Component"):
        sc = frappe.get_doc("Salary Component", sc.name)
        sc.save()

    # Setup For expense claim
    for ect in frappe.get_list("Expense Claim Type"):
        ect = frappe.get_doc("Expense Claim Type", ect.name)
        ect.save()


def create_default_cost_centers(companies):
    for company in companies:
        create_cost_center(
            "Main",
            company.name,
            True,
            ["cost_center", "round_off_cost_center", "depreciation_cost_center"],
        )


def create_dafault_mode_of_payments():
    create_mode_payment("Advance Payment", "Bank")
    create_mode_payment("Loans Payment", "Bank")
    create_mode_payment("Parroll Payment", "Bank")


def create_risk_insurance_components():
    components = [
        comp.name
        for comp in frappe.db.sql(
            "SELECT LOWER(name) as name FROM `tabSalary Component`", as_dict=True
        )
    ]
    for component in [
        "Risk On Company",
        "Risk On Employee",
        "Employee Pension Insurance",
        "Company Pension Insurance",
    ]:
        if f"{component}".lower() in components:
            continue
        sc_doc = frappe.new_doc("Salary Component")
        data = risk_insurance_components.get(component)
        sc_doc.salary_component = component
        sc_doc.update(data)
        sc_doc.save()
    frappe.db.commit()


def hide_accounts_and_taxs_from_system():
    for key in update_fields_props.keys():
        fields_props = update_fields_props.get(f"{key}", [])
        add_property_setter(fields_props)


def update_custom_roles(role_args, args):
    name = frappe.db.get_value("Custom Role", role_args, "name")
    if name:
        custom_role = frappe.get_doc("Custom Role", name)
        for new_role in args.get("roles", []):
            rol = new_role.get("role", False)
            if not rol:
                continue
            custom_role.append("roles", {"role": rol})
        custom_role.save()
    else:
        frappe.get_doc(args).insert()
    frappe.db.commit()


def add_property_setter(fields_props):
    for props in fields_props:
        doctype = props.get("doctype", False)
        fieldname = props.get("field", False)
        property = props.get("prop", False)
        value = props.get("value", False)
        property_type = props.get("prop_type", False)
        if (
            not doctype
            or not fieldname
            or not property
            or not value
            or not property_type
        ):
            continue

        try:
            make_property_setter(
                doctype,
                fieldname,
                property,
                value,
                property_type,
                validate_fields_for_doctype=False,
            )
        except:
            pass
    frappe.db.commit()


def set_missing_custom_account(self):
    if self.payable_account:
        return
    account = create_account(
        "Expense Claims",
        self.company,
        "Accounts Payable",
        "Liability",
        "Payable",
        True,
        "default_payable_account",
    )
    self.payable_account = account


def set_home_page_login():
    frappe.db.set_value("Website Settings", "Website Settings", "home_page", "login")
    frappe.db.commit()