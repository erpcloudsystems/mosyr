import frappe

def execute():
    if frappe.db.exists('Custom Field', 'Employee-payment_type'):
        field_doc = frappe.get_doc('Custom Field', 'Employee-payment_type')
        field_doc.delete()
        frappe.db.commit()