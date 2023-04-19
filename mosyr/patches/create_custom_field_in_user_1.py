import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_field

def execute():
    custom_field = frappe.db.exists("Custom Field", {"name" :"User-companies"})
    if custom_field :
        frappe.delete_doc("Custom Field", custom_field)
        frappe.db.commit()
        
    create_custom_field(
        "User",
        dict(
            owner="Administrator",
            fieldname="companies",
            label="Companies",
            fieldtype="Table MultiSelect",
            options="Company Table",
            insert_after="username",
        ),
    )
    frappe.db.commit()