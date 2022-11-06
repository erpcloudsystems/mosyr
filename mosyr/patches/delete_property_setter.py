import frappe

def execute():
    if frappe.db.exists('Property Setter', 'Employee-employee_number-hidden'):
        field_doc_one = frappe.get_doc('Property Setter', 'Employee-employee_number-hidden')
        field_doc_one.delete()
        
    if frappe.db.exists('Property Setter', 'Employee-employee_number-reqd'):
        field_doc_two = frappe.get_doc('Property Setter', 'Employee-employee_number-reqd')
        field_doc_two.delete()
    frappe.db.commit()