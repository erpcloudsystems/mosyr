import frappe


def execute():
    if frappe.db.exists("Custom Field", "Employee-citizen"):
        field_doc = frappe.get_doc("Custom Field", "Employee-citizen")
        field_doc.delete()
        frappe.db.commit()
