import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_field

def execute():
    custom_field = frappe.db.exists("Custom Field", {"name" :"Company-column_break_0gjgh"})
    if custom_field :
        frappe.delete_doc("Custom Field", custom_field)
        frappe.db.commit()

    create_custom_field(
        "Company",
        dict(
            owner="Administrator",
            fieldname="column_break_0gjgh",
            fieldtype="Column Break",
            insert_after="pension_percentage_on_employee",
            
        ),
    )
    frappe.db.commit()

    custom_field = frappe.db.exists("Custom Field", {"name" :"Company-pension_percentage_on_company"})
    if custom_field :
        frappe.delete_doc("Custom Field", custom_field)
        frappe.db.commit()

    create_custom_field(
        "Company",
        dict(
            owner="Administrator",
            fieldname="pension_percentage_on_company",
            label="Pension Percentage On Company",
            fieldtype="Percent",
            insert_after="column_break_0gjgh"
        ),
    )
    frappe.db.commit()