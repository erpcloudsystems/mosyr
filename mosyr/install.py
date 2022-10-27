from six import iteritems

import frappe
from frappe.custom.doctype.property_setter.property_setter import make_property_setter
from frappe.installer import update_site_config

from erpnext.setup.install import create_user_type

from mosyr import create_account, create_cost_center, create_mode_payment, create_bank_account, update_fields_props

def after_install():
    edit_gender_list()
    prepare_mode_payments()
    prepare_system_accounts()
    hide_accounts_fields()
    
    create_salary_components()
    create_salary_structures_for_companies()
    # frappe.db.commit()
    edit_doctypes_user_type()
    create_banks()
    companies = frappe.get_list("Company")
    create_dafault_bank_accounts(companies)
    create_dafault_accounts(companies)
    create_default_cost_centers(companies)
    create_dafault_mode_of_payments()
    hide_accounts_and_taxs_from_system()
    setup_doctypes_user_type()


def edit_gender_list():
    genders_to_del = frappe.get_list("Gender", filters={"name": ["not in", ["Female", "Male"]]})
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
        create_account("Employees Advances", company.name, "Loans and Advances (Assets)", "Asset", "Payable", True, "default_employee_advance_account")
        create_account("Expense Claims", company.name, "Expenses", "Expense", "", False)
        create_account("Expense Payable", company.name, "Accounts Payable", "Liability", "Payable", True, "default_payable_account")
        create_account("Loans Account", company.name, "Loans and Advances (Assets)", "Asset", "", False)
        create_account("Loans Disbursement", company.name, "Loans and Advances (Assets)", "Asset", "", False)
        create_account("Loans Repayment", company.name, "Loans and Advances (Assets)", "Asset", "", False)
        create_account("Loans Inreset", company.name, "Income", "Income", "", False)
        create_account("Loans Penalty", company.name, "Income", "Income", "", False)
        create_account("Loans Write Off", company.name, "Expenses", "Expense", "", False)
        create_account("Payroll Payable", company.name, "Accounts Payable", "Liability", "", True, "default_payroll_payable_account")
        create_account("Payroll Payment", company.name, "Loans and Advances (Assets)", "Asset", "Bank", False)
        
    # Setup For mode of payments
    for mop in frappe.get_list("Mode of Payment"):
        mop = frappe.get_doc("Mode of Payment", mop.name)
        mop.save()

    # Setup For salayr components
    for sc in frappe.get_list("Salary Component"):
        sc = frappe.get_doc("Salary Component", sc.name)
        sc.save()
    
    # Setup For salayr components
    for ect in frappe.get_list("Expense Claim Type"):
        ect = frappe.get_doc("Expense Claim Type", ect.name)
        ect.save()

def create_default_cost_centers(companies):
    for company in companies:
        create_cost_center("Main", company.name, True, ["cost_center", "round_off_cost_center", "depreciation_cost_center"])

def create_dafault_mode_of_payments():
    create_mode_payment("Advance Payment", "Bank")
    create_mode_payment("Loans Payment", "Bank")
    create_mode_payment("Parroll Payment", "Bank")

def hide_accounts_and_taxs_from_system():
    for key in update_fields_props.keys():
        fields_props = update_fields_props.get(f"{key}", [])
        add_property_setter(fields_props)

def setup_doctypes_user_type():
	user_types = get_user_types_data()
	user_type_limit = {}
	for user_type, data in iteritems(user_types):
		user_type_limit.setdefault(frappe.scrub(user_type), 20)
	update_site_config("user_type_doctype_limit", user_type_limit)
	for user_type, data in iteritems(user_types):
		create_user_type(user_type, data)
	frappe.db.commit()

def get_user_types_data():
	return {
		"Employee Self Service": {
			"role": "Employee Self Service",
			"apply_user_permission_on": "Employee",
			"user_id_field": "user_id",
			"doctypes": {

				"Salary Slip": ["read"],
				"Employee": ["read", "write"],
				"Expense Claim": ["read", "write", "create", "delete"],
				"Leave Application": ["read", "write", "create", "delete"],
				"Attendance Request": ["read", "write", "create", "delete"],
				"Compensatory Leave Request": ["read", "write", "create", "delete"],
				"Employee Tax Exemption Declaration": ["read", "write", "create", "delete"],
				"Employee Tax Exemption Proof Submission": ["read", "write", "create", "delete"],
				"Timesheet": ["read", "write", "create", "delete", "submit", "cancel", "amend"],
				
				"Work Experience": ["read", "write", "create", "delete", "submit", "cancel", "amend"],
				"Dependants Details": ["read", "write", "create", "delete", "submit", "cancel", "amend"],
				"Passport Details": ["read", "write", "create", "delete", "submit", "cancel", "amend"],
				"Salary Details": ["read", "write", "create", "delete", "submit", "cancel", "amend"],
				"Health Insurance": ["read", "write", "create", "delete", "submit", "cancel", "amend"],
				"Contact Details": ["read", "write", "create", "delete", "submit", "cancel", "amend"],
				"Emergency Contact": ["read", "write", "create", "delete", "submit", "cancel", "amend"],
				"Educational Qualification": ["read", "write", "create", "delete", "submit", "cancel", "amend"],
				"Personal Details": ["read", "write", "create", "delete", "submit", "cancel", "amend"],
				"Employee ID": ["read", "write", "create", "delete", "submit", "cancel", "amend"],
				"Lateness Permission": ["read", "write", "create", "delete", "submit", "cancel", "amend"],
			},
		}
	}

def create_banks():
    banks = [
        {"bank_name":"Al Inma Bank","swift_number" :"INMA" },
        {"bank_name":"Riyadh Bank","swift_number" :"RIBL" },
        {"bank_name":"The National Commercial Bank","swift_number" :"NCBK" },
        {"bank_name":"Samba Financial Group","swift_number" :"SAMB" },
        {"bank_name":"Al Rajhi Bank","swift_number" :"RJHI" },
        {"bank_name":"Al Araby Bank","swift_number" :"ARNB" },
    ]
    for bank in banks:
        banks_list = frappe.get_list("Bank", filters={"name": bank['bank_name']})
        if len(banks_list) == 0:
            bank_doc = frappe.new_doc("Bank")
            bank_doc.update(bank)
            bank_doc.save()
    frappe.db.commit()
def add_property_setter(fields_props):
    for props in fields_props:
        doctype = props.get("doctype", False)
        fieldname = props.get("field", False)
        property = props.get("prop", False)
        value = props.get("value", False)
        property_type = props.get("prop_type", False)
        if not doctype or not fieldname or not property or not value or not property_type:
            continue
        
        try: make_property_setter(doctype,fieldname,property, value,property_type,validate_fields_for_doctype=False,)
        except: pass
    frappe.db.commit()

    def set_missing_custom_account(self):
        if self.payable_account: return
        account = create_account("Expense Claims", self.company, "Accounts Payable", "Liability", "Payable", True, "default_payable_account")
        self.payable_account = account
