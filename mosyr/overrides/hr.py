import frappe
from frappe import _
from frappe.desk.page.setup_wizard.setup_wizard import make_records
from frappe.utils.nestedset import NestedSet, rebuild_tree

from erpnext.setup.doctype.company.company import Company, install_country_fixtures
from erpnext.hr.doctype.employee.employee import Employee
from erpnext.hr.doctype.department.department import Department
from erpnext.hr.doctype.travel_request.travel_request import TravelRequest
from erpnext.hr.doctype.expense_claim.expense_claim import ExpenseClaim
from erpnext.hr.doctype.employee_advance.employee_advance import EmployeeAdvance
from erpnext.hr.doctype.expense_claim_type.expense_claim_type import ExpenseClaimType

from mosyr import (
    create_account,
    create_cost_center,
    create_mode_payment,
)


class CustomCompany(Company, NestedSet):
    def validate(self):
        self.update_default_account = False
        if self.is_new():
            self.update_default_account = True
        super().validate()

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

        if not frappe.db.get_value(
            "Cost Center", {"is_group": 0, "company": self.name}
        ):
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
            frappe.local.enable_perpetual_inventory[
                self.name
            ] = self.enable_perpetual_inventory
        if frappe.flags.parent_company_changed:
            rebuild_tree("Company", "parent_company")

        super().on_update()
        frappe.clear_cache()


    def after_insert(self):
        super().after_insert()
        self.update_custom_linked_accounts()

    def update_custom_linked_accounts(self):
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

    def create_default_departments(self):
        records = [
            # Department
            {
                "doctype": "Department",
                "department_name": _("All Departments"),
                "is_group": 1,
                "parent_department": "",
                "__condition": lambda: not frappe.db.exists(
                    "Department", _("All Departments")
                ),
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
        frappe.local.flags.ignore_update_nsm = True
        make_records(records)
        frappe.local.flags.ignore_update_nsm = False
        rebuild_tree("Department", "parent_department")


class CustomEmployee(Employee):
    def validate(self):
        self.set_missing_custome_values()
        super().validate()

    def set_missing_custome_values(self):
        if self.payroll_cost_center:
            return
        cost_center = create_cost_center(
            "Main",
            self.company,
            True,
            ["cost_center", "round_off_cost_center", "depreciation_cost_center"],
        )
        self.payroll_cost_center = cost_center
    
    def update_user(self):
        super().update_user()
        user = frappe.get_doc("User", self.user_id)
        if user.user_type == "SaaS Manager": return
        user.flags.ignore_permissions = True
        user.user_type = "Employee Self Service"
        user.save()

class CustomDepartment(Department):
    def validate(self):
        self.set_missing_custome_values()
        super().validate()

    def set_missing_custome_values(self):
        if self.payroll_cost_center:
            return
        cost_center = create_cost_center(
            "Main",
            self.company,
            True,
            ["cost_center", "round_off_cost_center", "depreciation_cost_center"],
        )
        self.payroll_cost_center = cost_center


class CustomTravelRequest(TravelRequest):
    def validate(self):
        self.set_missing_custome_values()
        super().validate()

    def set_missing_custome_values(self):
        if self.cost_center:
            return
        cost_center = create_cost_center(
            "Main",
            self.company,
            True,
            ["cost_center", "round_off_cost_center", "depreciation_cost_center"],
        )
        self.cost_center = cost_center


class CustomExpenseClaim(ExpenseClaim):
    def validate(self):
        self.set_missing_custome_values()
        super().validate()

    def set_missing_custome_values(self):
        self.set_missing_custom_account()
        self.set_missing_custom_cost_center()

    def set_missing_custom_cost_center(self):
        if not self.cost_center:
            cost_center = create_cost_center(
                "Main",
                self.company,
                True,
                ["cost_center", "round_off_cost_center", "depreciation_cost_center"],
            )
            self.cost_center = cost_center
        for expense in self.expenses:
            if not expense.cost_center:
                expense.cost_center = cost_center

    def set_missing_custom_account(self):
        if self.payable_account:
            return
        account = create_account(
            "Expense Payable",
            self.company,
            "Accounts Payable",
            "Liability",
            "Payable",
            True,
            "default_payable_account",
        )
        self.payable_account = account


class CustomEmployeeAdvance(EmployeeAdvance):
    def validate(self):
        self.set_missing_custome_values()
        super().validate()

    def set_missing_custome_values(self):
        if not self.advance_account:
            account = create_account(
                "Employees Advances",
                self.company,
                "Loans and Advances (Assets)",
                "Asset",
                "Payable",
                True,
                "default_employee_advance_account",
            )
            self.advance_account = account
        if not self.mode_of_payment:
            mop = create_mode_payment("Advance Payment", "Bank")
            self.mode_of_payment = mop


class CustomExpenseClaimType(ExpenseClaimType):
    def validate(self):
        self.set_missing_custome_values()
        super().validate()

    def set_missing_custome_values(self):
        self.accounts = []
        companies = frappe.get_list("Company")
        for company in companies:
            account = create_account(
                "Expense Claims", company.name, "Expenses", "Expense", "", False
            )
            self.append(
                "accounts", {"company": company.name, "default_account": account}
            )
