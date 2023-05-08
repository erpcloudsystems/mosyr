import frappe
import datetime

def execute():
    return
    # emp_benefites = frappe.get_all("Employee Benefit", filters={"docstatus": 1})
    # for row in emp_benefites:
    #     emp_benefit = frappe.get_doc("Employee Benefit", row.get("name"))

    #     if emp_benefit.payroll_month and len(str(emp_benefit.payroll_month).split("-")) == 2:
    #         date = datetime.datetime.strptime(f"{emp_benefit.payroll_month}-01", "%Y-%m-%d").date()
    #         emp_benefit.db_set("payroll_month", date)
    #         frappe.db.commit()
