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
from erpnext.payroll.doctype.payroll_entry.payroll_entry import PayrollEntry, get_joining_relieving_condition, get_sal_struct, remove_payrolled_employees, get_emp_list
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
        # self.set_missing_custome_values()
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
        #     account = create_account(
        #         account_name,
        #         company.name,
        #         "Accounts Payable",
        #         "Liability",
        #         "",
        #         False,
        #         None,
        #     )
            self.append("accounts", {"company": company.name, "account": f"{account_name}"})


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
        # Check if payroll entry
        if self.payroll_entry:
            payroll_entry = frappe.get_doc("Payroll Entry", self.payroll_entry)
            for employee in payroll_entry.employees:
                if (
                    employee.employee == self.employee 
                    and flt(employee.deduct_from_salary) == 1
                    and flt(employee.deduction_per_day) > 0
                    and flt(employee.deduction_days) > 0):
                    found = False
                    for deduction in self.deductions:
                        if deduction.is_leave_deduction == 1:
                            deduction.amount = flt(employee.deduction_per_day) * flt(employee.deduction_days)
                            found = True
                            super().validate()
                            break
                    if not found:
                        self.append("deductions", {
                            "salary_component": "Leave Deduction",
                            "amount": flt(employee.deduction_per_day) * flt(employee.deduction_days),
                            "is_leave_deduction": 1
                        })
                        super().validate()

        

    def set_missing_custome_values(self):
        # Check Leave Deduction Salary Component
        ld = frappe.db.exists("Salary Component", "Leave Deduction")
        if ld:
            ld = frappe.get_doc("Salary Component", ld)
            if ld.type != "Deduction":
                ld.type = "Deduction"
                ld.save()
                frappe.db.commit()
        else:
            ld = frappe.new_doc("Salary Component")
            ld.salary_component = "Leave Deduction"
            ld.abbr = f"LD-{frappe.utils.now_datetime().timestamp()}"
            ld.depends_on_payment_days = 0
            ld.save()
            frappe.db.commit()
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
    
    @frappe.whitelist()
    def fill_employee_details(self):
        self.set("employees", [])
        employees = self.custom_get_emp_list()
        if not employees:
            error_msg = _(
                "No employees found for the mentioned criteria:<br>Company: {0}<br> Currency: {1}<br>"
            ).format(
                frappe.bold(self.company),
                frappe.bold(self.currency),
            )
            if len(self.branches) > 0:
                branches = []
                for branch in self.branches:
                    branches.append("<li>{0}</li>".format(frappe.bold(branch.branch)))
                branches = "".join(branches)
                error_msg += "<br>" + _("Branches: <ul>{0}</ul>").format(branches)
            if len(self.departments) > 0:
                departments = []
                for department in self.departments:
                    departments.append("<li>{0}</li>".format(frappe.bold(department.department)))
                departments = "".join(departments)
                error_msg += "<br>" + _("Departments: <ul>{0}</ul>").format(departments)
            if len(self.designations) > 0:
                designations = []
                for designation in self.designations:
                    designations.append("<li>{0}</li>".format(frappe.bold(designation.designation)))
                designations = "".join(designations)
                error_msg += "<br>" + _("Designations: <ul>{0}</ul>").format(designations)
            if self.start_date:
                error_msg += "<br>" + _("Start date: {0}").format(frappe.bold(self.start_date))
            if self.end_date:
                error_msg += "<br>" + _("End date: {0}").format(frappe.bold(self.end_date))
            frappe.throw(error_msg, title=_("No employees found"))

        for d in employees:
            total_leaves = get_total_leaves_taken(d.employee, self.start_date, self.end_date)
            dd = {
                "total_leaves_taken": total_leaves,
            }
            dd.update(d)
            self.append("employees", dd)

        self.number_of_employees = len(self.employees)
        if self.validate_attendance:
            return self.validate_employee_attendance()

    @frappe.whitelist()
    def get_employee_details_for_payroll(self, employee):
        total_leaves = get_total_leaves_taken(employee, self.start_date, self.end_date) or 0
        return {
            "total_leaves_taken": total_leaves
        }

    def custom_make_filters(self):
        filters = frappe._dict()
        filters["company"] = self.company
        branches = []
        departments = []
        designations = []

        for branch in self.branches:
            branches.append(branch.branch)

        for department in self.departments:
            departments.append(department.department)
        
        for designation in self.designations:
            designations.append(designation.designation)

        filters["branches"] = branches
        filters["departments"] = departments
        filters["designations"] = designations

        return filters

    def custom_get_emp_list(self):
        """
        Returns list of active employees based on selected criteria
        and for which salary structure exists
        """
        self.check_mandatory()
        filters = self.custom_make_filters()
        cond = custom_get_filter_condition(filters)
        cond += get_joining_relieving_condition(self.start_date, self.end_date)

        condition = ""
        if self.payroll_frequency:
            condition = """and payroll_frequency = '%(payroll_frequency)s'""" % {
                "payroll_frequency": self.payroll_frequency
            }

        sal_struct = get_sal_struct(
            self.company, self.currency, self.salary_slip_based_on_timesheet, condition
        )
        if sal_struct:
            cond += "and t2.salary_structure IN %(sal_struct)s "
            cond += "and t2.payroll_payable_account = %(payroll_payable_account)s "
            cond += "and %(from_date)s >= t2.from_date"
            emp_list = get_emp_list(sal_struct, cond, self.end_date, self.payroll_payable_account)
            emp_list = remove_payrolled_employees(emp_list, self.start_date, self.end_date)
            return emp_list

def custom_get_filter_condition(filters):
    cond = ""
    for f in ["company"]:
        if filters.get(f):
            cond += " and t1." + f + " = " + frappe.db.escape(filters.get(f))
    for f in ["branches"]:
        d = filters.get(f)
        if isinstance(d, list) and len(d) > 0:
            ind = ",".join([f" {frappe.db.escape(id_)} " for id_ in d])
            cond += " and t1.branch in ( " + ind + " ) "
    for f in ["departments"]:
        d = filters.get(f)
        if isinstance(d, list) and len(d) > 0:
            ind = ",".join([f" {frappe.db.escape(id_)} " for id_ in d])
            cond += " and t1.department in ( " + ind + " ) "

    for f in ["designations"]:
        d = filters.get(f)
        if isinstance(d, list) and len(d) > 0:
            ind = ",".join([f" {frappe.db.escape(id_)} " for id_ in d])
            cond += " and t1.designation in ( " + ind + " ) "
    
    return cond


def get_total_leaves_taken(employee, from_date, to_date):
    from erpnext.hr.doctype.leave_application.leave_application import get_leaves_for_period
    allocation_records = [lt.name for lt in frappe.db.sql("select name from `tabLeave Type`", as_dict=True)]
    total_leaves_taken = 0

    for d in allocation_records:
        leaves_taken = get_leaves_for_period(employee, d, from_date, to_date) * -1
        total_leaves_taken += leaves_taken

    return total_leaves_taken
