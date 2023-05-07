import frappe

def execute():
    custom_fields = ["Employee-nationality", "Employee-religion"]
    for field in custom_fields:
        frappe.delete_doc_if_exists("Custom Field", field)
        frappe.db.commit()
