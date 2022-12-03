from dataclasses import field
from warnings import filters
import frappe
from frappe import _
from frappe.utils import flt
from frappe.utils.nestedset import NestedSet, rebuild_tree
from frappe.desk.page.setup_wizard.setup_wizard import make_records

from erpnext.setup.doctype.company.company import Company, install_country_fixtures

from erpnext.hr.doctype.employee.employee import Employee
from erpnext.hr.doctype.department.department import Department
from erpnext.hr.doctype.travel_request.travel_request import TravelRequest
from erpnext.hr.doctype.expense_claim.expense_claim import ExpenseClaim
from erpnext.hr.doctype.employee_advance.employee_advance import EmployeeAdvance
from erpnext.hr.doctype.expense_claim_type.expense_claim_type import ExpenseClaimType

from erpnext.accounts.doctype.mode_of_payment.mode_of_payment import ModeofPayment

from erpnext.loan_management.doctype.loan_type.loan_type import LoanType
from erpnext.loan_management.doctype.loan.loan import Loan
from erpnext.loan_management.doctype.loan_disbursement.loan_disbursement import LoanDisbursement
from erpnext.loan_management.doctype.loan_repayment.loan_repayment import LoanRepayment
from erpnext.loan_management.doctype.loan_write_off.loan_write_off import LoanWriteOff

from erpnext.payroll.doctype.salary_component.salary_component import SalaryComponent
from erpnext.payroll.doctype.salary_structure.salary_structure import SalaryStructure
from erpnext.payroll.doctype.salary_structure_assignment.salary_structure_assignment import SalaryStructureAssignment
from erpnext.payroll.doctype.salary_slip.salary_slip import SalarySlip
from erpnext.payroll.doctype.payroll_entry.payroll_entry import PayrollEntry

from mosyr import create_account, create_cost_center, create_mode_payment, create_bank_account
from erpnext.hr.doctype.employee_checkin.employee_checkin import mark_attendance_and_link_log
from mosyr.api import custom_mark_attendance_and_link_log
from erpnext.hr.doctype.shift_type.shift_type import ShiftType
from frappe.utils import cint
import itertools
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
            rebuild_tree("Company", "parent_company")

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
        frappe.local.flags.ignore_update_nsm = True
        make_records(records)
        frappe.local.flags.ignore_update_nsm = False
        rebuild_tree("Department", "parent_department")

class CustomEmployee(Employee):
    def validate(self):
        self.set_missing_custome_values()
        super().validate()
    
    def set_missing_custome_values(self):
        if self.payroll_cost_center: return
        cost_center = create_cost_center("Main", self.company, True, ["cost_center", "round_off_cost_center", "depreciation_cost_center"])
        self.payroll_cost_center = cost_center

class CustomDepartment(Department):
    def validate(self):
        self.set_missing_custome_values()
        super().validate()
    
    def set_missing_custome_values(self):
        if self.payroll_cost_center: return
        cost_center = create_cost_center("Main", self.company, True, ["cost_center", "round_off_cost_center", "depreciation_cost_center"])
        self.payroll_cost_center = cost_center

class CustomTravelRequest(TravelRequest):
    def validate(self):
        self.set_missing_custome_values()
        super().validate()
    
    def set_missing_custome_values(self):
        if self.cost_center: return
        cost_center = create_cost_center("Main", self.company, True, ["cost_center", "round_off_cost_center", "depreciation_cost_center"])
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
            cost_center = create_cost_center("Main", self.company, True, ["cost_center", "round_off_cost_center", "depreciation_cost_center"])
            self.cost_center = cost_center
        for expense in self.expenses:
            if not expense.cost_center:
                expense.cost_center = cost_center

    def set_missing_custom_account(self):
        if self.payable_account: return
        account = create_account("Expense Payable", self.company, "Accounts Payable", "Liability", "Payable", True, "default_payable_account")
        self.payable_account = account

class CustomEmployeeAdvance(EmployeeAdvance):
    def validate(self):
        self.set_missing_custome_values()
        super().validate()
    
    def set_missing_custome_values(self):
        if not self.advance_account:
            account = create_account("Employees Advances", self.company, "Loans and Advances (Assets)", "Asset", "Payable", True, "default_employee_advance_account")
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
            account = create_account("Expense Claims", company.name, "Expenses", "Expense", "", False)
            self.append("accounts", {
                "company": company.name,
                "default_account": account
            })

class CustomModeofPayment(ModeofPayment):
    def validate(self):
        self.set_missing_custome_values()
        super().validate()
    
    def set_missing_custome_values(self):
        self.accounts = []
        companies = frappe.get_list("Company")
        for company in companies:
            account_name = f"{self.mode_of_payment}"
            account = create_account(account_name, company.name, "Current Assets", "Asset", "Receivable", False)
            self.append("accounts", {
                "company": company.name,
                "default_account": account
            })

class CustomLoanType(LoanType):
    def validate(self):
        self.set_missing_custome_values()
        super().validate()

    def set_missing_custome_values(self):
        if not self.loan_account:
            account = create_account("Loans Account", self.company, "Loans and Advances (Assets)", "Asset", "", False)
            self.loan_account = account

        if not self.disbursement_account:
            account = create_account("Loans Disbursement", self.company, "Loans and Advances (Assets)", "Asset", "", False)
            self.disbursement_account = account

        if not self.payment_account:
            account = create_account("Loans Repayment", self.company, "Loans and Advances (Assets)", "Asset", "", False)
            self.payment_account = account

        if not self.interest_income_account:
            account = create_account("Loans Inreset", self.company, "Income", "Income", "", False)
            self.interest_income_account = account
        
        if not self.penalty_income_account:
            account = create_account("Loans Penalty", self.company, "Income", "Income", "", False)
            self.penalty_income_account = account
        
        if not self.mode_of_payment:
            mop = create_mode_payment("Loans Payment", "Bank")
            self.mode_of_payment = mop

class CustomLoan(Loan):
    def validate(self):
        self.set_missing_custome_values()
        super().validate()
    
    def set_missing_custome_values(self):
        if not self.loan_account:
            account = create_account("Loans Account", self.company, "Loans and Advances (Assets)", "Asset", "", False)
            self.loan_account = account

        if not self.disbursement_account:
            account = create_account("Loans Disbursement", self.company, "Loans and Advances (Assets)", "Asset", "", False)
            self.disbursement_account = account

        if not self.payment_account:
            account = create_account("Loans Repayment", self.company, "Loans and Advances (Assets)", "Asset", "", False)
            self.payment_account = account

        if not self.interest_income_account:
            account = create_account("Loans Inreset", self.company, "Income", "Income", "", False)
            self.interest_income_account = account
        
        if not self.penalty_income_account:
            account = create_account("Loans Penalty", self.company, "Income", "Income", "", False)
            self.penalty_income_account = account

        if not self.mode_of_payment:
            mop = create_mode_payment("Loans Payment", "Bank")
            self.mode_of_payment = mop
        
        if not self.cost_center:
            cost_center = create_cost_center("Main", self.company, True, ["cost_center", "round_off_cost_center", "depreciation_cost_center"])
            self.cost_center = cost_center

class CustomLoanDisbursement(LoanDisbursement):
    def validate(self):
        self.set_missing_custome_values()
        super().validate()
    
    def set_missing_custome_values(self):
        if not self.cost_center:
            cost_center = create_cost_center("Main", self.company, True, ["cost_center", "round_off_cost_center", "depreciation_cost_center"])
            self.cost_center = cost_center
        
        if not self.disbursement_account:
            account = create_account("Loans Disbursement", self.company, "Loans and Advances (Assets)", "Asset", "", False)
            self.disbursement_account = account
        
        if not self.loan_account:
            account = create_account("Loans Account", self.company, "Loans and Advances (Assets)", "Asset", "", False)
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
            cost_center = create_cost_center("Main", self.company, True, ["cost_center", "round_off_cost_center", "depreciation_cost_center"])
            self.cost_center = cost_center
        
        if not self.loan_account:
            account = create_account("Loans Account", self.company, "Loans and Advances (Assets)", "Asset", "", False)
            self.loan_account = account
        
        if not self.payment_account:
            account = create_account("Loans Repayment", self.company, "Loans and Advances (Assets)", "Asset", "", False)
            self.payment_account = account
        
        if not self.payroll_payable_account:
            account = create_account("Payroll Payable", self.company, "Accounts Payable", "Liability", "", True, "default_payroll_payable_account")
            self.payroll_payable_account = account
        
        if not self.penalty_income_account:
            account = create_account("Loans Penalty", self.company, "Income", "Income", "", False)
            self.penalty_income_account = account

    def update_paid_amount(self):
        super().update_paid_amount()
        loan = frappe.get_value(
            "Loan",
            self.against_loan,
            [
                "total_amount_paid",
                "loan_amount"
            ],
            as_dict=1,
        )
        frappe.db.sql(
            """ UPDATE `tabLoan`
            SET total_amount_remaining = %s
            WHERE name = %s """,
            (flt(loan.loan_amount - loan.total_amount_paid), self.against_loan),
        )
    def update_repayment_schedule(self, cancel=0):
        if self.is_term_loan and self.principal_amount_paid > self.payable_principal_amount:
            regenerate_repayment_schedule(self.name ,self.against_loan, cancel)

def regenerate_repayment_schedule(repayment , loan, cancel=0):
    loan_doc = frappe.get_doc("Loan", loan)
    self = frappe.get_doc("Loan Repayment", repayment)
    repayment_schedule_length = len(loan_doc.get("repayment_schedule"))

    repayment_amount = self.amount_paid
    if repayment_schedule_length:
        for row in loan_doc.repayment_schedule:
            if row.paid_amount >= row.principal_amount: continue
            if repayment_amount > row.principal_amount-row.paid_amount:
                diff = row.principal_amount - row.paid_amount
                row.paid_amount = row.paid_amount + diff
                repayment_amount = repayment_amount - diff
            else:
                row.paid_amount = row.paid_amount + repayment_amount 
                repayment_amount = 0
            if repayment_amount <= 0: break
        loan_doc.save(ignore_permissions=True)

class CustomLoanWriteOff(LoanWriteOff):
    def validate(self):
        self.set_missing_custome_values()
        super().validate()

    def set_missing_custome_values(self):
        if not self.cost_center:
            cost_center = create_cost_center("Main", self.company, True, ["cost_center", "round_off_cost_center", "depreciation_cost_center"])
            self.cost_center = cost_center
        
        if not self.write_off_account:
            account = create_account("Loans Write Off", self.company, "Expenses", "Expense", "", False)
            self.write_off_account = account

class CustomSalaryComponent(SalaryComponent):
    def validate(self):
        self.set_missing_custome_values()
        super().validate()
    
    def set_missing_custome_values(self):
        self.accounts = []
        companies = frappe.get_list("Company")
        for company in companies:
            account = create_account("Payroll Payable", company.name, "Accounts Payable", "Liability", "", True, "default_payroll_payable_account")
            self.append("accounts", {
                "company": company.name,
                "account": account
            })

class CustomSalaryStructure(SalaryStructure):
    def validate(self):
        self.set_missing_custome_values()
        super().validate()
    
    def set_missing_custome_values(self):
        if not self.mode_of_payment:
            mop = create_mode_payment("Payroll Payment", "Bank")
            self.mode_of_payment = mop
        if not self.payment_account:
            accounts = frappe.get_list("Mode of Payment Account", 
                                            filters={'parent': self.mode_of_payment or "", 'company': self.company},
                                            fields=['*'])
            if len(accounts) > 0:
                self.payment_account = accounts[0].default_account

class CustomSalaryStructureAssignment(SalaryStructureAssignment):
    def validate(self):
        self.set_missing_custome_values()
        super().validate()
    
    def set_missing_custome_values(self):
        if not self.payroll_payable_account:
            account = create_account("Payroll Payable", self.company, "Accounts Payable", "Liability", "", True, "default_payroll_payable_account")
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
            cost_center = create_cost_center("Main", self.company, True, ["cost_center", "round_off_cost_center", "depreciation_cost_center"])
            self.payroll_cost_center = cost_center

class CustomPayrollEntry(PayrollEntry):
    def validate(self):
        self.set_missing_custome_values()
        super().validate()
    
    def set_missing_custome_values(self):
        if not self.payroll_payable_account:
            account = create_account("Payroll Payable", self.company, "Accounts Payable", "Liability", "", True, "default_payroll_payable_account")
            self.payroll_payable_account = account

        if not self.cost_center:
            cost_center = create_cost_center("Main", self.company, True, ["cost_center", "round_off_cost_center", "depreciation_cost_center"])
            self.cost_center = cost_center
        
        if not self.bank_account:
            bank_account = create_bank_account(self.company)
            self.bank_account = bank_account

        if not self.payment_account:
            account = create_account("Payroll Payment", self.company, "Loans and Advances (Assets)", "Asset", "Bank", False)
            self.payment_account = account

class CustomShiftType(ShiftType):
    @frappe.whitelist()
    def process_auto_attendance(self):
        super().process_auto_attendance()
        self.custom_process_auto_attendance()

    def custom_process_auto_attendance(self):
        if (not cint(self.enable_auto_attendance) or not self.process_attendance_after or not self.last_sync_of_checkin):
            return

        filters = {
            "time": (">=", self.process_attendance_after),
            "shift_actual_end": ("<", self.last_sync_of_checkin),
            "shift": self.name,
        }
        logs = frappe.db.get_list("Employee Checkin", fields="*", filters=filters, order_by="employee,time")
        for key, group in itertools.groupby(logs, key=lambda x: (x["employee"], x["shift_actual_start"])):
            single_shift_logs = list(group)
            (attendance_status, working_hours, late_entry, early_exit, in_time, out_time) = self.get_attendance(single_shift_logs)
            custom_mark_attendance_and_link_log(
                single_shift_logs,
                attendance_status,
                key[1].date(),
                working_hours,
                late_entry,
                early_exit,
                in_time,
                out_time,
                self.name,
            )