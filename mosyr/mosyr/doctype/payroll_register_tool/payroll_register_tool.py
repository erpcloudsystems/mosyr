# Copyright (c) 2022, AnvilERP and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.model.naming import make_autoname
from frappe.utils import cint, flt

from erpnext.payroll.doctype.salary_structure_assignment.salary_structure_assignment import (
    get_assigned_salary_structure,
)


class PayrollRegisterTool(Document):
    def on_cancel(self):
        # frappe.msgprint("helllo badr")
        employees = []
        for employee in self.employees:
            employees.append(employee.employee)
        formatted_employee_ids = ', '.join([f"'{emp_id}'" for emp_id in employees])
        salary_stucture_assignments = frappe.db.sql( f"""
            select * from `tabSalary Structure Assignment` where employee IN({formatted_employee_ids}) and docstatus= 1;
        """,as_dict = 1)
        salary_structures = []
        for salary_stucture_assignment in salary_stucture_assignments:
            salary_structures.append(salary_stucture_assignment.salary_structure)
        # frappe.throw(f"{salary_structures}")
        for salary_stucture_assignment in salary_stucture_assignments:
            ssa = frappe.get_doc("Salary Structure Assignment", salary_stucture_assignment.name)
            ssa.cancel()
        # for salary_structure in salary_structures:
        #     ss = frappe.get_doc("Salary Structure", salary_structure)
        #     ss.cancel()
        pass
    def validate(self):
        if len(self.employees) == 1:
            self.employee_name = self.employees[0].employee_name
        if not self.from_date:
            frappe.throw(_("From Date is mandatory to prepare Salary Structures") + ".")
            return
        if not self.company:
            frappe.throw(_("Company is mandatory to prepare Salary Structures") + ".")
            return
        if flt(self.base) <= 0:
            frappe.throw(_("Base is mandatory to prepare Salary Structures") + ".")

    def on_submit(self):
        self.prepare_salary_structures()

    @frappe.whitelist()
    def fetch_employees(self, company, department=None, branch=None, designation=None):
        conds = [" status='Active' "]
        if company and len(f"{company}") > 0:
            conds.append(" company='{}' ".format(company))
        else:
            return []
        if department and len(f"{department}") > 0:
            conds.append(" department='{}' ".format(department))
        if branch and len(f"{branch}") > 0:
            conds.append(" branch='{}' ".format(branch))
        if designation and len(f"{designation}") > 0:
            conds.append(" designation='{}' ".format(designation))
        if len(conds) > 0:
            conds = " AND ".join(conds)
            conds = "WHERE {}".format(conds)
        else:
            return []

        return frappe.db.sql(
            "SELECT name, employee_name FROM `tabEmployee` {}".format(conds),
            as_dict=True,
        )

    def prepare_salary_structures(self):
        company_doc = frappe.db.exists("Company", self.company)
        if not company_doc:
            frappe.throw(_("Company {} dose not exists".format(self.company)))
            return
        currency = self.currency
        company_doc = frappe.get_doc("Company", company_doc)
        if not currency:
            currency = company_doc.default_currency
        else:
            currency_doc = frappe.db.exists("Currency", currency)
            if not currency_doc:
                currency = company_doc.default_currency
            else:
                currency = currency_doc

        valid_employees = []
        not_active_emps = []
        has_salary_structure = []
        different_comp = []

        # Check Employee Data
        for employee in self.employees:
            employee_doc = frappe.db.exists("Employee", employee.employee)
            if not employee_doc:
                not_active_emps.append(employee.get("employee_name", None))
                continue

            employee_doc = frappe.get_doc("Employee", employee_doc)
            if employee_doc.status != "Active":
                not_active_emps.append(employee_doc.name)
                continue

            if employee_doc.company != self.company:
                different_comp.append(employee_doc.name)
                continue

            salary_structure = get_assigned_salary_structure(
                employee_doc.name, self.from_date
            )
            if salary_structure and cint(self.override_existing_structures)==0:
                has_salary_structure.append(employee_doc.name)
                continue

            valid_employees.append(employee_doc.name)

        if len(valid_employees) > 0:
            ss_name = "PRT-{}-.#####".format(self.from_date)
            ss_name = make_autoname(ss_name)
            ss_doc = frappe.new_doc("Salary Structure")
            ss_doc.update(
                {
                    "__newname": ss_name,
                    "is_active": "Yes",
                    "payroll_frequency": self.payroll_frequency,
                    "company": company_doc.name,
                    "currency": currency,
                    "salary_slip_based_on_timesheet": 0,
                    "leave_encashment_amount_per_day": self.leave_encashment_amount_per_day
                }
            )
            ss_doc.__newname = ss_name
            for sc in self.earnings:
                ss_doc.append(
                    "earnings",
                    {
                        "salary_component": sc.salary_component,
                        "abbr": sc.abbr,
                        "amount": sc.amount,
                        "year_to_date": sc.year_to_date,
                        "additional_salary": sc.additional_salary,
                        "is_recurring_additional_salary": sc.is_recurring_additional_salary,
                        "statistical_component": sc.statistical_component,
                        "depends_on_payment_days": sc.depends_on_payment_days,
                        "exempted_from_income_tax": sc.exempted_from_income_tax,
                        "do_not_include_in_total": sc.do_not_include_in_total,
                        "condition": sc.condition,
                        "amount_based_on_formula": sc.amount_based_on_formula,
                        "formula": sc.formula,
                        "default_amount": sc.default_amount,
                        "additional_amount": sc.additional_amount,
                        "tax_on_flexible_benefit": sc.tax_on_flexible_benefit,
                        "tax_on_additional_salary": sc.tax_on_additional_salary,
                    },
                )
            for sc in self.deductions:
                ss_doc.append(
                    "deductions",
                    {
                        "salary_component": sc.salary_component,
                        "abbr": sc.abbr,
                        "amount": sc.amount,
                        "year_to_date": sc.year_to_date,
                        "additional_salary": sc.additional_salary,
                        "is_recurring_additional_salary": sc.is_recurring_additional_salary,
                        "statistical_component": sc.statistical_component,
                        "depends_on_payment_days": sc.depends_on_payment_days,
                        "exempted_from_income_tax": sc.exempted_from_income_tax,
                        "do_not_include_in_total": sc.do_not_include_in_total,
                        "condition": sc.condition,
                        "amount_based_on_formula": sc.amount_based_on_formula,
                        "formula": sc.formula,
                        "default_amount": sc.default_amount,
                        "additional_amount": sc.additional_amount,
                        "tax_on_flexible_benefit": sc.tax_on_flexible_benefit,
                        "tax_on_additional_salary": sc.tax_on_additional_salary,
                    },
                )
            ss_doc.save()
            ss_doc.submit()
            for emp in valid_employees:
                sa = frappe.new_doc("Salary Structure Assignment")
                sa.employee = emp
                sa.salary_structure = ss_doc.name
                sa.from_date = self.from_date
                sa.base = flt(self.base)
                sa.variable = flt(self.variable)
                sa.insert()
                sa.submit()
        msg = _(
            "<h5>Salary Structure Prepared for {} Employees</h5>".format(
                len(valid_employees)
            )
        )
        ss_status = True
        if cint(self.override_existing_structures)==0:
            msg_str = []
            if len(has_salary_structure) > 0:
                ss_status = False
                for hss in has_salary_structure:
                    msg_str.append("<li>{}</li>".format(hss))
            if len(msg_str) > 0:
                msg_str = "".join(msg_str)
                msg_str = "<p>{}</p><ul>{}</ul>".format(
                    _("Employees Assigned to salary structure"), msg_str
                )
            else:
                msg_str = ""
            msg += msg_str

        msg_str = []
        if len(different_comp) > 0:
            ss_status = False
            for hss in different_comp:
                msg_str.append("<li>{}</li>".format(hss))
        if len(msg_str) > 0:
            msg_str = "".join(msg_str)
            msg_str = "<p>{}</p><ul>{}</ul>".format(
                _("Employees belong to different companies"), msg_str
            )
        else:
            msg_str = ""
        msg += msg_str

        msg_str = []
        if len(not_active_emps) > 0:
            ss_status = False
            for hss in not_active_emps:
                msg_str.append("<li>{}</li>".format(hss))
        if len(msg_str) > 0:
            msg_str = "".join(msg_str)
            msg_str = "<p>{}</p><ul>{}</ul>".format(
                _("In active / not found employees"), msg_str
            )
        else:
            msg_str = ""
        msg += msg_str

        frappe.msgprint(msg, _("Salary Structure Status"))
        return {"status": ss_status}

    def get_employees_payroll_details(self, payroll):
        earnings = [
            sc.name
            for sc in frappe.db.sql(
                "select name from `tabSalary Component` where type='Earning'",
                as_dict=True,
            )
        ]
        deductions = [
            sc.name
            for sc in frappe.db.sql(
                "select name from `tabSalary Component` where type='Deduction'",
                as_dict=True,
            )
        ]
        zeros_earnings = [True for i in range(len(earnings))]
        zeros_deductions = [True for i in range(len(deductions))]
        ernings_total = 0
        deductions_total = 0
        total_e = 0
        total_d = 0
        total_loans = 0
        total_loans_sum = 0
        data = []
        emp_earnings_total = [0 for i in range(len(earnings))]
        emp_deductions_total = [0 for i in range(len(deductions))]
        payroll = frappe.get_doc("Payroll Entry", payroll)

        for sr, employee in enumerate(payroll.employees, 1):
            result_dict = frappe._dict()
            result_dict.update(
                {
                    "sr": sr,
                    "employee": employee.employee,
                    "employee_name": employee.employee_name,
                    "department": employee.department,
                    "designation": employee.designation,
                }
            )
            slip = frappe.get_doc(
                "Salary Slip",
                {"payroll_entry": payroll.name, "employee": employee.employee},
            )
            emp_earnings = [0 for i in range(len(earnings))]
            emp_deductions = [0 for i in range(len(deductions))]
            result_dict.update(
                {
                    "sr": sr,
                    "employee": employee.employee,
                    "employee_name": employee.employee_name,
                    "department": employee.department,
                    "designation": employee.designation,
                    "net_pay": 0,
                }
            )
            if slip:
                total_e = 0
                total_d = 0
                # frappe.msgprint(f"{slip.total_loan_repayment}")
                total_loans = slip.total_loan_repayment
                total_loans_sum += total_loans
                for e in slip.earnings:
                    try:
                        idx = earnings.index(e.salary_component)
                        amount = flt(e.amount)
                        if amount > 0:
                            zeros_earnings[idx] = False
                        emp_earnings[idx] = amount
                        emp_earnings_total[idx]+=amount
                        total_e += amount
                        ernings_total += amount
                    except:
                        pass
                for d in slip.deductions:
                    try:
                        idx = deductions.index(d.salary_component)
                        amount = flt(d.amount)
                        if amount > 0:
                            zeros_deductions[idx] = False
                        emp_deductions[idx] = amount
                        emp_deductions_total[idx] += amount
                        total_d += amount
                        deductions_total += amount
                    except:
                        pass
                total_d += total_loans
                deductions_total += total_loans
                net_pay = flt(slip.net_pay)
                result_dict.update({"net_pay": net_pay,"total_e": total_e ,"total_d": total_d, "total_loans": total_loans})
            
            result_dict.update(
                {
                    "earnings": emp_earnings,
                    "deductions": emp_deductions,
                    
                }
            )
            
            data.append(result_dict)
         
        return self.get_clean_data(
            zeros_earnings,
            zeros_deductions,
            earnings,
            ernings_total,
            deductions,
            deductions_total,
            data,
            total_loans,
            total_loans_sum,
            emp_earnings_total,
            emp_deductions_total
        )

    def get_clean_data(self, ezeros, dzeros, erns, total_e, dedcs, total_d, data, total_loans, total_loans_sum, emp_earnings_total, emp_deductions_total):
        earnings = []
        deductions = []
        for idx, e in enumerate(ezeros):
            if not e:
                earnings.append(erns[idx])
        for idx, d in enumerate(dzeros):
            if not d:
                deductions.append(dedcs[idx])

        final_data = []
        last_net_pay = 0
        arr_of_comp =  []
        for d in data:
            row = [
                d.get("sr", "-"),
                d.get("employee", ""),
                d.get("employee_name", ""),
                d.get("department", ""),
                d.get("designation", ""),
            ]
            erns = d.get("earnings", [])

            for idx, e in enumerate(ezeros):
                if not e:
                    row.append(erns[idx])
            row.append(d.get("total_e", ""))
            dedcs = d.get("deductions", [])
            for idx, de in enumerate(dzeros):
                if not de:
                    row.append(dedcs[idx])
            
            row.append(d.get("total_loans", ""))
            row.append(d.get("total_d", ""))
            last_net_pay += d.get("net_pay", 0)
            row.append(d.get("net_pay", 0))
            final_data.append(row)
        
        len_earnings = len(earnings)
        if len(earnings) > 0:
            len_earnings = len(earnings) + 1

        len_deductions = len(deductions)
        deductions.append("Loan")
        len_deductions += 1

        if len(deductions) > 0:
            len_deductions = len(deductions) + 1
        total_row = [
            "-",
            "الاجمالى",
            "",
            "",
            ""
        ]
        for i in emp_earnings_total:
            if i > 0:
                total_row.append( i)
        total_row.append(total_e)
        for i in emp_deductions_total:
            if i > 0:
                total_row.append(i)
        total_row.append(total_loans_sum)
        total_row.append(total_d)
        total_row.append(last_net_pay)
        final_data.append(
            total_row
        )
        
        return {
            "earnings": earnings,
            "len_earnings": len_earnings,
            "deductions": deductions,
            "len_deductions": len_deductions,
            "data": final_data,
            "total_e": total_e,
            "total_d": total_d,
        }
