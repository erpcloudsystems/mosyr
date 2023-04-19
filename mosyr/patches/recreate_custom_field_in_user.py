import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_field

def execute():
    create_custom_field(
        "User",
        dict(
            owner="Administrator",
            fieldname="companies",
            label="Companies",
            fieldtype="Table MultiSelect",
            options="Company Table",
            insert_after="username",
            allow_in_quick_entry=1
        ),
    )
    frappe.db.commit()