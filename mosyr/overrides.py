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

