import frappe

def execute():
    if frappe.db.exists('Report', 'Exit Permissions Total'):
        field_doc = frappe.get_doc('Report', 'Exit Permissions Total')
        field_doc.delete()
        frappe.db.commit()