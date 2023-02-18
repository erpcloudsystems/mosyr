import frappe
from frappe import _
from frappe.utils import flt

import erpnext
from erpnext.payroll.doctype.salary_component.salary_component import SalaryComponent
from erpnext.payroll.doctype.salary_structure.salary_structure import SalaryStructure
from erpnext.payroll.doctype.salary_structure_assignment.salary_structure_assignment import (
    SalaryStructureAssignment,
)
from erpnext.payroll.doctype.salary_slip.salary_slip import SalarySlip
from erpnext.payroll.doctype.payroll_entry.payroll_entry import PayrollEntry
from erpnext.accounts.doctype.accounting_dimension.accounting_dimension import (
    get_accounting_dimensions,
)
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
                False,
                None,
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
    
    def create_journal_entry(self, je_payment_amount, user_remark):
        payroll_payable_account = self.payroll_payable_account
        precision = frappe.get_precision("Journal Entry Account", "debit_in_account_currency")

        accounts = []
        currencies = []
        multi_currency = 0
        company_currency = erpnext.get_company_currency(self.company)
        accounting_dimensions = get_accounting_dimensions() or []

        exchange_rate, amount = self.get_amount_and_exchange_rate_for_journal_entry(
            self.payment_account, je_payment_amount, company_currency, currencies
        )
        accounts.append(
            self.update_accounting_dimensions(
                {
                    "account": self.payment_account,
                    "bank_account": self.bank_account,
                    "credit_in_account_currency": flt(amount, precision),
                    "exchange_rate": flt(exchange_rate),
                },
                accounting_dimensions,
            )
        )

        exchange_rate, amount = self.get_amount_and_exchange_rate_for_journal_entry(
            payroll_payable_account, je_payment_amount, company_currency, currencies
        )
        accounts.append(
            self.update_accounting_dimensions(
                {
                    "account": payroll_payable_account,
                    "debit_in_account_currency": flt(amount, precision),
                    "exchange_rate": flt(exchange_rate),
                    "reference_type": self.doctype,
                    "reference_name": self.name,
                },
                accounting_dimensions,
            )
        )

        if len(currencies) > 1:
            multi_currency = 1

        journal_entry = frappe.new_doc("Journal Entry")
        journal_entry.voucher_type = "Bank Entry"
        journal_entry.user_remark = _("Payment of {0} from {1} to {2}").format(
            user_remark, self.start_date, self.end_date
        )
        journal_entry.company = self.company
        journal_entry.posting_date = self.posting_date
        journal_entry.multi_currency = multi_currency
        journal_entry.cheque_no = self.name
        journal_entry.cheque_date = frappe.utils.nowdate()
        journal_entry.set("accounts", accounts)
        journal_entry.save(ignore_permissions=True)
        journal_entry.submit()