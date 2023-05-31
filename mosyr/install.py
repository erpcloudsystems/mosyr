import frappe
from six import iteritems
from frappe.custom.doctype.property_setter.property_setter import make_property_setter
from frappe.custom.doctype.custom_field.custom_field import create_custom_field
from frappe.installer import update_site_config
from erpnext.setup.install import create_custom_role, create_user_type
from mosyr import (
    create_account,
    create_cost_center,
    create_mode_payment,
    create_bank_account,
    update_fields_props,
)
from frappe.permissions import update_permission_property, add_permission

docs_for_manager = [
    # "System Controller",
    "Expense Claim",
    "Employee Tax Exemption Declaration",
    "Employee Tax Exemption Proof Submission",
    "Work Experience",
    "Dependants Details",
    "Employee ID",
    "Passport Details",
    "Lateness Permission",
    "Exit Permission",
    "Company Id",
    "Translation",
    "User",
    "Users Permission Manager",
    "Department",
    "Branch",
    "Employee Group",
    "Designation",
    "Employee Grade",
    "Employment Type",
    "Shift Type",
    "Staffing Plan",
    "Holiday List",
    "Leave Type",
    "Leave Period",
    "Leave Policy",
    "Leave Policy Assignment",
    "Leave Allocation",
    "Leave Encashment",
    "Employee Health Insurance",
    "Leave Block List",
    "Employee",
    "End Of Service",
    "Leave Application",
    "Shift Request",
    "Shift Builder",
    "Contact Details",
    "Educational Qualification",
    "Emergency Contact",
    "Health Insurance",
    "Personal Details",
    "Salary Details",
    "Mosyr Form",
    "Attendance",
    "Employee Attendance Tool",
    "Attendance Request",
    "Upload Attendance",
    "Employee Checkin",
    "Payroll Settings",
    "Salary Component",
    "Salary Structure",
    "Salary Structure Assignment",
    "Employee Benefit",
    "Employee Deduction",
    "Payroll Entry",
    "Salary Slip",
    "Retention Bonus",
    "Employee Incentive",
    "Appraisal",
    "Appraisal Template",
    "Leave Application",
    "Compensatory Leave Request",
    "Travel Request",
    "Leave Encashment",
    "Loan Type",
    "Loan",
    "Loan Application",
    "Vehicle",
    "Vehicle Log",
    "Vehicle Service",
    "Document Manager",
    "Document Type",
    "Custody",
    "Cash Custody",
    "Cash Custody Expense",
    "Shift Assignment",
    "User Permission",
    "Nationality",
    "Religion",
    "Additional Salary",
    "Custom Field",
    "Company",
    "Address",
    "Letter Head",
    "Process Loan Interest Accrual",
    "Journal Entry",
    "Account",
    "Loan Interest Accrual",
    "Loan Repayment"
]
reports_for_manager = [
    "Insurances and Risk",
    "Employee Attendance Sheet",
    "Biomitric Devices",
    "Files in Saudi banks format",
    "Employee Leave Balance",
    "Employee Leave Balance Summary",
    "Leave Balance Encashment",
    "Exit Permissions Summary"
]


def after_install():
    edit_gender_list()
    create_banks()
    companies = frappe.get_list("Company")
    create_dafault_bank_accounts(companies)
    create_dafault_accounts(companies)
    create_default_cost_centers(companies)
    create_dafault_mode_of_payments()
    hide_accounts_and_taxs_from_system()
    create_non_standard_user_types()
    allow_read_for_reports()
    add_select_perm_for_all()
    create_role_and_set_to_admin()
    set_home_page_login()
    create_custom_field(
        "User",
        dict(
            owner="Administrator",
            fieldname="companies",
            label="Companies",
            fieldtype="Table MultiSelect",
            options="Company Table",
            insert_after="username",
            allow_in_quick_entry=1
        ),
    )
    
    frappe.db.commit()

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


def create_banks():
    banks = [
        {"bank_name": "Al Inma Bank", "swift_number": "INMA"},
        {"bank_name": "Riyadh Bank", "swift_number": "RIBL"},
        {"bank_name": "The National Commercial Bank", "swift_number": "NCBK"},
        {"bank_name": "Samba Financial Group", "swift_number": "SAMB"},
        {"bank_name": "Al Rajhi Bank", "swift_number": "RJHI"},
        {"bank_name": "Al Araby Bank", "swift_number": "ARNB"},
    ]
    for bank in banks:
        banks_list = frappe.get_list("Bank", filters={"name": bank["bank_name"]})
        if len(banks_list) == 0:
            bank_doc = frappe.new_doc("Bank")
            bank_doc.update(bank)
            bank_doc.save()
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

    # Setup For salayr components
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


def hide_accounts_and_taxs_from_system():
    for key in update_fields_props.keys():
        fields_props = update_fields_props.get(f"{key}", [])
        add_property_setter(fields_props)


def create_non_standard_user_types():
    non_stadard_users = {}
    manager_user_type = get_manager_user_data()
    self_service_user_type = get_self_service_data()

    non_stadard_users.update(manager_user_type)
    non_stadard_users.update(self_service_user_type)

    user_type_limit = {}
    for user_type, data in iteritems(non_stadard_users):
        user_type_limit.setdefault(frappe.scrub(user_type), 10000)
    update_site_config("user_type_doctype_limit", user_type_limit)

    for user_type, data in iteritems(non_stadard_users):
        create_custom_role(data)
        if user_type == "SaaS Manager":
            sm = frappe.db.exists("Role", "SaaS Manager")
            if sm:
                smr = frappe.get_doc("Role", sm)
                smr.is_custom = 1
                smr.desk_access = 1
                smr.save(ignore_permissions=True)
            else:
                smr = frappe.new_doc()
                smr.update({
                    "role_name": "SaaS Manager",
                    "desk_access": 1,
                    "is_custom": 1
                })
                smr.save(ignore_permissions=True)
            frappe.db.commit()
        create_user_type(user_type, data)

    add_permission_read()
    frappe.db.commit()
    

def get_manager_user_data():
    doctypes = {}
    for document in docs_for_manager:
        doctypes.update(
            {
                document: [
                    "read",
                    "write",
                    "create",
                    "delete",
                    "submit",
                    "cancel",
                    "amend",
                    "set_user_permissions"
                ]
            }
        )

    types = {
        "SaaS Manager": {
            "role": "SaaS Manager",
            "apply_user_permission_on": "Employee",
            "user_id_field": "user_id",
            "doctypes": doctypes,
        }
    }
    return types


def get_self_service_data():
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
                "Employee Tax Exemption Declaration": [
                    "read",
                    "write",
                    "create",
                    "delete",
                ],
                "Employee Tax Exemption Proof Submission": [
                    "read",
                    "write",
                    "create",
                    "delete",
                ],
                "Timesheet": [
                    "read",
                    "write",
                    "create",
                    "delete",
                    "submit",
                    "cancel",
                    "amend",
                ],
                "Work Experience": [
                    "read",
                    "write",
                    "create",
                    "delete",
                    "submit",
                    "cancel",
                    "amend",
                ],
                "Dependants Details": [
                    "read",
                    "write",
                    "create",
                    "delete",
                    "submit",
                    "cancel",
                    "amend",
                ],
                "Passport Details": [
                    "read",
                    "write",
                    "create",
                    "delete",
                    "submit",
                    "cancel",
                    "amend",
                ],
                "Salary Details": [
                    "read",
                    "write",
                    "create",
                    "delete",
                    "submit",
                    "cancel",
                    "amend",
                ],
                "Health Insurance": [
                    "read",
                    "write",
                    "create",
                    "delete",
                    "submit",
                    "cancel",
                    "amend",
                ],
                "Contact Details": [
                    "read",
                    "write",
                    "create",
                    "delete",
                    "submit",
                    "cancel",
                    "amend",
                ],
                "Emergency Contact": [
                    "read",
                    "write",
                    "create",
                    "delete",
                    "submit",
                    "cancel",
                    "amend",
                ],
                "Educational Qualification": [
                    "read",
                    "write",
                    "create",
                    "delete",
                    "submit",
                    "cancel",
                    "amend",
                ],
                "Personal Details": [
                    "read",
                    "write",
                    "create",
                    "delete",
                    "submit",
                    "cancel",
                    "amend",
                ],
                "Employee ID": [
                    "read",
                    "write",
                    "create",
                    "delete",
                    "submit",
                    "cancel",
                    "amend",
                ],
                "Lateness Permission": [
                    "read",
                    "write",
                    "create",
                    "delete",
                    "submit",
                    "cancel",
                    "amend",
                ],
                "Exit Permission": [
                    "read",
                    "write",
                    "create",
                    "delete",
                    "submit",
                    "cancel",
                    "amend",
                ],
            },
        },
    }


def allow_read_for_reports():
    args = {
        "doctype": "Custom Role",
        "roles": [{"role": "SaaS Manager", "parenttype": "Custom Role"}],
    }
    for report in reports_for_manager:
        ref_doctype = frappe.db.get_value("Report", report, "ref_doctype")
        args.update(
            {
                "report": report,
                "ref_doctype": ref_doctype,
            }
        )
        update_custom_roles({"report": report}, args)
        update_permission_property(ref_doctype, "SaaS Manager", 0, "select", 1)
        update_permission_property(ref_doctype, "SaaS Manager", 0, "read", 1)
        update_permission_property(ref_doctype, "SaaS Manager", 0, "report", 1)
    frappe.db.commit()

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

def add_select_perm_for_all():
    docs_for_manager.append("Account")
    docs_for_manager.append("Email Domain")
    docs_for_manager.append("Email Template")
    docs_for_manager.append("Email Account")
    for doc in docs_for_manager:
        # Add Select for Doctype and for all links fields
        doc = frappe.db.exists("DocType", doc)
        if not doc: continue
        doc = frappe.get_doc("DocType", doc)

        for field in doc.fields:
            if field.fieldtype != "Link": continue
            doc_field = frappe.db.exists("DocType", field.options)
            if not doc_field: continue
            update_permission_property(doc_field, "SaaS Manager", 0, "select", 1)
            update_permission_property(doc_field, "SaaS Manager", 0, "read", 1)
            update_permission_property(doc_field, "SaaS Manager", 0, "report", 1)
            update_permission_property(doc_field, "SaaS Manager", 0, "write", 1)
            update_permission_property(doc_field, "SaaS Manager", 0, "create", 1)
            update_permission_property(doc_field, "SaaS Manager", 0, "print", 1)
            update_permission_property(doc_field, "SaaS Manager", 0, "email", 1)
            update_permission_property(doc_field, "SaaS Manager", 0, "delete", 1)
            update_permission_property(doc_field, "SaaS Manager", 0, "import", 1)
            update_permission_property(doc_field, "SaaS Manager", 0, "export", 1)
            update_permission_property(doc_field, "SaaS Manager", 0, "email", 1)
            update_permission_property(doc_field, "SaaS Manager", 0, "set_user_permissions", 1)
            update_permission_property(doc_field, "SaaS Manager", 0, "share", 1)
            update_permission_property(doc_field, "Employee Self Service", 0, "select", 1)
        update_permission_property(doc_field, "SaaS Manager", 0, "select", 1)
        update_permission_property(doc_field, "SaaS Manager", 0, "read", 1)
        update_permission_property(doc_field, "SaaS Manager", 0, "report", 1)
        update_permission_property(doc_field, "SaaS Manager", 0, "write", 1)
        update_permission_property(doc_field, "SaaS Manager", 0, "create", 1)
        update_permission_property(doc_field, "SaaS Manager", 0, "print", 1)
        update_permission_property(doc_field, "SaaS Manager", 0, "email", 1)
        update_permission_property(doc_field, "SaaS Manager", 0, "delete", 1)
        update_permission_property(doc_field, "SaaS Manager", 0, "import", 1)
        update_permission_property(doc_field, "SaaS Manager", 0, "export", 1)
        update_permission_property(doc_field, "SaaS Manager", 0, "email", 1)
        update_permission_property(doc_field, "SaaS Manager", 0, "set_user_permissions", 1)
        update_permission_property(doc_field, "SaaS Manager", 0, "share", 1)
        update_permission_property(doc.name, "Employee Self Service", 0, "select", 1)
    frappe.db.commit()

def create_role_and_set_to_admin():
    create_custom_role({"role": "Read User Type"})
    frappe.get_doc("User", "Administrator").add_roles("Read User Type")
    frappe.db.commit()
    update_permission_property("User", "Read User Type", 3, "read", 1)
    update_permission_property("User", "Read User Type", 3, "write", 1)
    frappe.db.commit()
    
    # create role Mosyr Forms and added this role for saas manager and employee self service 
    create_custom_role({"role": "Mosyr Forms"})
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
