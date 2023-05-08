import frappe
import datetime

def execute():
    emp_deductions = frappe.get_all("Employee Deduction", filters={"docstatus": 1})
    for row in emp_deductions:
        emp_deduction = frappe.get_doc("Employee Deduction", row.get("name"))

        if emp_deduction.payroll_month and len(str(emp_deduction.payroll_month).split("-")) == 2:
            date = datetime.datetime.strptime(f"{emp_deduction.payroll_month}-01", "%Y-%m-%d").date()
            emp_deduction.db_set("payroll_month", date)
            frappe.db.commit()
