import frappe
from frappe.utils import flt

from erpnext.loan_management.doctype.loan_type.loan_type import LoanType
from erpnext.loan_management.doctype.loan.loan import Loan
from erpnext.loan_management.doctype.loan_disbursement.loan_disbursement import (
	LoanDisbursement,
)
from erpnext.loan_management.doctype.loan_repayment.loan_repayment import LoanRepayment
from erpnext.loan_management.doctype.loan_write_off.loan_write_off import LoanWriteOff

from mosyr import (
	create_account,
	create_cost_center,
	create_mode_payment,
	create_bank_account,
)

from mosyr.overrides import regenerate_repayment_schedule


class CustomLoanType(LoanType):
	def validate(self):
		self.set_missing_custome_values()
		super().validate()

	def set_missing_custome_values(self):
		if not self.loan_account:
			account = create_account(
				"Loans Account",
				self.company,
				"Loans and Advances (Assets)",
				"Asset",
				"",
				False,
			)
			self.loan_account = account

		if not self.disbursement_account:
			account = create_account(
				"Loans Disbursement",
				self.company,
				"Loans and Advances (Assets)",
				"Asset",
				"",
				False,
			)
			self.disbursement_account = account

		if not self.payment_account:
			account = create_account(
				"Loans Repayment",
				self.company,
				"Loans and Advances (Assets)",
				"Asset",
				"",
				False,
			)
			self.payment_account = account

		if not self.interest_income_account:
			account = create_account(
				"Loans Inreset", self.company, "Income", "Income", "", False
			)
			self.interest_income_account = account

		if not self.penalty_income_account:
			account = create_account(
				"Loans Penalty", self.company, "Income", "Income", "", False
			)
			self.penalty_income_account = account

		if not self.mode_of_payment:
			mop = create_mode_payment("Loans Payment", "Bank")
			self.mode_of_payment = mop


class CustomLoan(Loan):
	def validate(self):
		self.set_missing_custome_values()
		super().validate()

	def set_missing_custome_values(self):
		if self.is_new():
			self.total_amount_remaining = flt(self.total_payment)
		if not self.loan_account:
			account = create_account(
				"Loans Account",
				self.company,
				"Loans and Advances (Assets)",
				"Asset",
				"",
				False,
			)
			self.loan_account = account

		if not self.disbursement_account:
			account = create_account(
				"Loans Disbursement",
				self.company,
				"Loans and Advances (Assets)",
				"Asset",
				"",
				False,
			)
			self.disbursement_account = account

		if not self.payment_account:
			account = create_account(
				"Loans Repayment",
				self.company,
				"Loans and Advances (Assets)",
				"Asset",
				"",
				False,
			)
			self.payment_account = account

		if not self.interest_income_account:
			account = create_account(
				"Loans Inreset", self.company, "Income", "Income", "", False
			)
			self.interest_income_account = account

		if not self.penalty_income_account:
			account = create_account(
				"Loans Penalty", self.company, "Income", "Income", "", False
			)
			self.penalty_income_account = account

		if not self.mode_of_payment:
			mop = create_mode_payment("Loans Payment", "Bank")
			self.mode_of_payment = mop

		if not self.cost_center:
			cost_center = create_cost_center(
				"Main",
				self.company,
				True,
				["cost_center", "round_off_cost_center", "depreciation_cost_center"],
			)
			self.cost_center = cost_center


class CustomLoanDisbursement(LoanDisbursement):
	def validate(self):
		self.set_missing_custome_values()
		super().validate()

	def set_missing_custome_values(self):
		if not self.cost_center:
			cost_center = create_cost_center(
				"Main",
				self.company,
				True,
				["cost_center", "round_off_cost_center", "depreciation_cost_center"],
			)
			self.cost_center = cost_center

		if not self.disbursement_account:
			account = create_account(
				"Loans Disbursement",
				self.company,
				"Loans and Advances (Assets)",
				"Asset",
				"",
				False,
			)
			self.disbursement_account = account

		if not self.loan_account:
			account = create_account(
				"Loans Account",
				self.company,
				"Loans and Advances (Assets)",
				"Asset",
				"",
				False,
			)
			self.loan_account = account

		if not self.bank_account:
			bank_account = create_bank_account(self.company)
			self.bank_account = bank_account


class CustomLoanRepayment(LoanRepayment):
	def validate(self):
		self.set_missing_custome_values()
		super().validate()

		
	def set_missing_custome_values(self):
		if not self.cost_center:
			cost_center = create_cost_center(
				"Main",
				self.company,
				True,
				["cost_center", "round_off_cost_center", "depreciation_cost_center"],
			)
			self.cost_center = cost_center

		if not self.loan_account:
			account = create_account(
				"Loans Account",
				self.company,
				"Loans and Advances (Assets)",
				"Asset",
				"",
				False,
			)
			self.loan_account = account

		if not self.payment_account:
			account = create_account(
				"Loans Repayment",
				self.company,
				"Loans and Advances (Assets)",
				"Asset",
				"",
				False,
			)
			self.payment_account = account

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

		if not self.penalty_income_account:
			account = create_account(
				"Loans Penalty", self.company, "Income", "Income", "", False
			)
			self.penalty_income_account = account

	def update_paid_amount(self):
		super().update_paid_amount()
		loan = frappe.get_value(
			"Loan",
			self.against_loan,
			["total_amount_paid", "loan_amount"],
			as_dict=1,
		)
		frappe.db.sql(
			""" UPDATE `tabLoan`
			SET total_amount_remaining = %s
			WHERE name = %s """,
			(flt(loan.loan_amount - loan.total_amount_paid), self.against_loan),
		)

	def update_repayment_schedule(self, cancel=0):
		if (
			self.is_term_loan
		):
			regenerate_repayment_schedule(self.name, self.against_loan, cancel)


class CustomLoanWriteOff(LoanWriteOff):
	def validate(self):
		self.set_missing_custome_values()
		super().validate()

	def set_missing_custome_values(self):
		if not self.cost_center:
			cost_center = create_cost_center(
				"Main",
				self.company,
				True,
				["cost_center", "round_off_cost_center", "depreciation_cost_center"],
			)
			self.cost_center = cost_center

		if not self.write_off_account:
			account = create_account(
				"Loans Write Off", self.company, "Expenses", "Expense", "", False
			)
			self.write_off_account = account
