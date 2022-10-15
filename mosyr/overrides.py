import frappe
from frappe import _
from frappe.model.document import Document

from mosyr.install import create_account, create_mode_payment
from mosyr import mosyr_accounts, mosyr_mode_payments

from erpnext.loan_management.doctype.loan.loan import Loan
from erpnext.loan_management.doctype.loan_type.loan_type import LoanType
from erpnext.loan_management.doctype.loan_write_off.loan_write_off import LoanWriteOff

from erpnext.hr.doctype.employee_advance.employee_advance import EmployeeAdvance
from erpnext.hr.doctype.expense_claim.expense_claim import ExpenseClaim

from erpnext.payroll.doctype.salary_structure.salary_structure import SalaryStructure

from frappe.utils.nestedset import NestedSet
from erpnext.setup.doctype.company.company import Company, install_country_fixtures

class CustomLoan(Loan):
    def validate(self):
        self.set_missing_custome_values()
        super().validate()

    def set_missing_custome_values(self):
        loan_type = frappe.get_doc("Loan Type", self.loan_type)
        for fieldname in [
            "payment_account",
            "disbursement_account",
            "loan_account",
            "interest_income_account",
            "penalty_income_account",
            "mode_of_payment"]:
            if not self.get(fieldname):
                self.update({fieldname:  loan_type[fieldname]})

class CustomLoanType(LoanType):
    def validate(self):
        self.set_missing_custome_values()
        super().validate()

    def set_missing_custome_values(self):
        company = frappe.get_doc("Company", self.company)
        accounts = mosyr_accounts.get('LoanType', [])
        for fieldname in [
            "payment_account",
            "disbursement_account",
            "loan_account",
            "interest_income_account",
            "penalty_income_account",]:
            if not self.get(fieldname):
                for account in accounts:
                    if account.get('fieldname') == fieldname:
                        args = {
                            "company": company.name,
                            "account_currency": company.default_currency
                        }
                        args.update(account["account"])
                        new_account = create_account(**args)
                        if new_account:
                            self.update({fieldname:  new_account})
                        else:
                            frappe.throw(_("Something Went Wrong!"))
        
        mode_payment = mosyr_mode_payments.get("LoanType")
        if not self.mode_of_payment:
            new_mode = create_mode_payment(mode_payment["type"], mode_payment["title"])
            if new_mode:
                self.mode_of_payment = new_mode
            else:
                frappe.throw(_("Something Went Wrong!"))

class CustomLoanWriteOff(LoanWriteOff):
    def validate(self):
        self.set_missing_custome_values()
        super().validate()

    def set_missing_custome_values(self):
        company = frappe.get_doc("Company", self.company)
        accounts = mosyr_accounts.get('LoanWriteOff', [])
        fieldname = "write_off_account"
        if not self.get(fieldname):
            for account in accounts:
                if account.get('fieldname') == fieldname:
                    args = {
                        "company": company.name,
                        "account_currency": company.default_currency
                    }
                    args.update(account["account"])
                    new_account = create_account(**args)
                    if new_account:
                        self.update({fieldname:  new_account})
                    else:
                        frappe.throw(_("Something Went Wrong!"))
        
class CustomEmployeeAdvance(EmployeeAdvance):
    def validate(self):
        self.set_missing_custome_values()
        super().validate()
    
    def set_missing_custome_values(self):
        company = frappe.get_doc("Company", self.company)
        mode_payment = mosyr_mode_payments.get("EmployeeAdvance")
        if not self.mode_of_payment:
            new_mode = create_mode_payment(mode_payment["type"], mode_payment["title"])
            if new_mode:
                self.mode_of_payment = new_mode
            else:
                frappe.throw(_("Something Went Wrong!"))
        
        accounts = mosyr_accounts.get('EmployeeAdvance', [])
        fieldname = "advance_account"
        if not self.get(fieldname):
            if company.default_employee_advance_account:
                self.advance_account = company.default_employee_advance_account
                return
            for account in accounts:
                if account.get('fieldname') == fieldname:
                    args = {
                        "company": company.name,
                        "account_currency": company.default_currency
                    }
                    args.update(account["account"])
                    new_account = create_account(**args)
                    if new_account:
                        self.update({fieldname:  new_account})
                    else:
                        frappe.throw(_("Something Went Wrong!"))

class CustomExpenseClaim(ExpenseClaim):
    def validate(self):
        self.set_missing_custome_values()
        super().validate()
    
    def set_missing_custome_values(self):
        company = frappe.get_doc("Company", self.company)
        accounts = mosyr_accounts.get('ExpenseClaim', [])
        fieldname = "payable_account"
        if not self.get(fieldname):
            for account in accounts:
                if account.get('fieldname') == fieldname:
                    args = {
                        "company": company.name,
                        "account_currency": company.default_currency
                    }
                    args.update(account["account"])
                    new_account = create_account(**args)
                    if new_account:
                        self.update({fieldname:  new_account})
                    else:
                        frappe.throw(_("Something Went Wrong!"))

class CustomSalaryStructure(SalaryStructure):
    def validate(self):
        self.set_missing_custome_values()
        super().validate()
    
    def set_missing_custome_values(self):
        mode_payment = mosyr_mode_payments.get("SalaryStructure")
        if not self.mode_of_payment:
            new_mode = create_mode_payment(mode_payment["type"], mode_payment["title"])
            if new_mode:
                self.mode_of_payment = new_mode
            else:
                frappe.throw(_("Something Went Wrong!"))

from frappe.desk.page.setup_wizard.setup_wizard import make_records
class CustomCompany(Company, NestedSet):
    def on_update(self):
        NestedSet.on_update(self)
        
        if not frappe.db.sql(
            """select name from tabAccount
                where company=%s and docstatus<2 limit 1""",
            self.name,
        ):
            if not frappe.local.flags.ignore_chart_of_accounts:
                frappe.flags.country_change = True
                self.create_default_accounts()
                self.create_default_warehouses()

        if not frappe.db.get_value("Cost Center", {"is_group": 0, "company": self.name}):
            self.create_default_cost_center()

        if frappe.flags.country_change:
            install_country_fixtures(self.name, self.country)
            self.create_default_tax_template()

        if not frappe.db.get_value("Department", {"company": self.name}):
            self.create_default_departments()

        if not frappe.local.flags.ignore_chart_of_accounts:
            self.set_default_accounts()
            if self.default_cash_account:
                self.set_mode_of_payment_account()

        if self.default_currency:
            frappe.db.set_value("Currency", self.default_currency, "enabled", 1)

        if (
            hasattr(frappe.local, "enable_perpetual_inventory")
            and self.name in frappe.local.enable_perpetual_inventory
        ):
            frappe.local.enable_perpetual_inventory[self.name] = self.enable_perpetual_inventory

        if frappe.flags.parent_company_changed:
            from frappe.utils.nestedset import rebuild_tree

            rebuild_tree("Company", "parent_company")

        frappe.clear_cache()
    
    def create_default_departments(self):
        records = [
            # Department
            {
                "doctype": "Department",
                "department_name": _("All Departments"),
                "is_group": 1,
                "parent_department": "",
                "__condition": lambda: not frappe.db.exists("Department", _("All Departments")),
            },
            {
                "doctype": "Department",
                "department_name": _("Accounts"),
                "parent_department": _("All Departments"),
                "company": self.name,
            },
            {
                "doctype": "Department",
                "department_name": _("Marketing"),
                "parent_department": _("All Departments"),
                "company": self.name,
            },
            {
                "doctype": "Department",
                "department_name": _("Sales"),
                "parent_department": _("All Departments"),
                "company": self.name,
            },
            {
                "doctype": "Department",
                "department_name": _("Purchase"),
                "parent_department": _("All Departments"),
                "company": self.name,
            },
            {
                "doctype": "Department",
                "department_name": _("Operations"),
                "parent_department": _("All Departments"),
                "company": self.name,
            },
            {
                "doctype": "Department",
                "department_name": _("Production"),
                "parent_department": _("All Departments"),
                "company": self.name,
            },
            {
                "doctype": "Department",
                "department_name": _("Dispatch"),
                "parent_department": _("All Departments"),
                "company": self.name,
            },
            {
                "doctype": "Department",
                "department_name": _("Customer Service"),
                "parent_department": _("All Departments"),
                "company": self.name,
            },
            {
                "doctype": "Department",
                "department_name": _("Human Resources"),
                "parent_department": _("All Departments"),
                "company": self.name,
            },
            {
                "doctype": "Department",
                "department_name": _("Management"),
                "parent_department": _("All Departments"),
                "company": self.name,
            },
            {
                "doctype": "Department",
                "department_name": _("Quality Management"),
                "parent_department": _("All Departments"),
                "company": self.name,
            },
            {
                "doctype": "Department",
                "department_name": _("Research & Development"),
                "parent_department": _("All Departments"),
                "company": self.name,
            },
            {
                "doctype": "Department",
                "department_name": _("Legal"),
                "parent_department": _("All Departments"),
                "company": self.name,
            },
        ]

        # Make root department with NSM updation
        make_records(records[:1])
        from frappe.utils.nestedset import rebuild_tree
        frappe.local.flags.ignore_update_nsm = True
        make_records(records)
        frappe.local.flags.ignore_update_nsm = False
        rebuild_tree("Department", "parent_department")