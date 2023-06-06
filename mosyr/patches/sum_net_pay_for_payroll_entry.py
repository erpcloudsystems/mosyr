import frappe

def execute():
    old_payrolls = frappe.get_list("Payroll Entry", {"docstatus":1},pluck="name")
    for p in old_payrolls:
        doc = frappe.get_doc("Payroll Entry", p)
        salary_slips = frappe.get_list("Salary Slip",{"payroll_entry": p}, pluck="net_pay")
        if len(salary_slips) > 0:
            total_net_pay = sum(salary_slips)
            doc.db_set("total_netpay", total_net_pay)
    frappe.db.commit()
