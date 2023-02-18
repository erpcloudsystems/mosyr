import frappe

from erpnext.payroll.doctype.salary_component.salary_component import SalaryComponent
from erpnext.payroll.doctype.salary_structure.salary_structure import SalaryStructure
from erpnext.payroll.doctype.salary_structure_assignment.salary_structure_assignment import (
    SalaryStructureAssignment,
)
from erpnext.payroll.doctype.salary_slip.salary_slip import SalarySlip
from erpnext.payroll.doctype.payroll_entry.payroll_entry import PayrollEntry

from mosyr import (
    create_account,
    create_cost_center,
    create_mode_payment,
    create_bank_account,
)


class CustomSalaryComponent(SalaryComponent):
    def validate(self):
        self.set_missing_custome_values()
        super().validate()

    def set_missing_custome_values(self):
        self.accounts = []
        companies = frappe.get_list("Company")
        account_name = "Payroll Payable"
        if self.type == "Earning":
            account_name = "Payroll Payable - Earning"
        elif self.type == "Deduction":
            account_name = "Payroll Payable - Deduction"

        for company in companies:
            account = create_account(
                account_name,
                company.name,
                "Accounts Payable",
                "Liability",
                "",
                True,
                "default_payroll_payable_account",
            )
            self.append("accounts", {"company": company.name, "account": account})


class CustomSalaryStructure(SalaryStructure):
    def validate(self):
        self.set_missing_custome_values()
        super().validate()

    def set_missing_custome_values(self):
        if not self.mode_of_payment:
            mop = create_mode_payment("Payroll Payment", "Bank")
            self.mode_of_payment = mop
        if not self.payment_account:
            accounts = frappe.get_list(
                "Mode of Payment Account",
                filters={"parent": self.mode_of_payment or "", "company": self.company},
                fields=["*"],
            )
            if len(accounts) > 0:
                self.payment_account = accounts[0].default_account


class CustomSalaryStructureAssignment(SalaryStructureAssignment):
    def validate(self):
        self.set_missing_custome_values()
        super().validate()

    def set_missing_custome_values(self):
        if not self.payroll_payable_account:
            account = create_account(
                "Payroll Payable",
                self.company,
                "Accounts Payable",
                "Liability",
                "",
                True,
                "default_payroll_payable_account",
            )
            self.payroll_payable_account = account


class CustomSalarySlip(SalarySlip):
    def validate(self):
        self.set_missing_custome_values()
        super().validate()

    def set_missing_custome_values(self):
        # No need to set default ( Field Type is Select)
        # if not self.mode_of_payment:
        #     mop = create_mode_payment("Loans Payment", "Bank")
        #     self.mode_of_payment = mop
        if not self.payroll_cost_center:
            cost_center = create_cost_center(
                "Main",
                self.company,
                True,
                ["cost_center", "round_off_cost_center", "depreciation_cost_center"],
            )
            self.payroll_cost_center = cost_center


class CustomPayrollEntry(PayrollEntry):
    def validate(self):
        self.set_missing_custome_values()
        super().validate()

    def set_missing_custome_values(self):
        if not self.payroll_payable_account:
            account = create_account(
                "Payroll Payable",
                self.company,
                "Accounts Payable",
                "Liability",
                "",
                True,
                "default_payroll_payable_account",
            )
            self.payroll_payable_account = account

        if not self.cost_center:
            cost_center = create_cost_center(
                "Main",
                self.company,
                True,
                ["cost_center", "round_off_cost_center", "depreciation_cost_center"],
            )
            self.cost_center = cost_center

        if not self.bank_account:
            bank_account = create_bank_account(self.company)
            self.bank_account = bank_account

        if not self.payment_account:
            account = create_account(
                "Payroll Payment",
                self.company,
                "Loans and Advances (Assets)",
                "Asset",
                "Bank",
                False,
            )
            self.payment_account = account
