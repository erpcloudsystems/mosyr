import frappe

def execute():
    if frappe.db.exists("Property Setter", "Payroll Entry-main-title_field"):
        frappe.delete_doc("Property Setter", "Payroll Entry-main-title_field", True)
        frappe.db.commit()