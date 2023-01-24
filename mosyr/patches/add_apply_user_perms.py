import frappe
from mosyr.install import docs_for_manager
from frappe.permissions import update_permission_property

def execute():
    docs_for_manager.append("Account")
    for doc in docs_for_manager:
        # Add Select for Doctype and for all links fields
        doc = frappe.db.exists("DocType", doc)
        if not doc: continue
        doc = frappe.get_doc("DocType", doc)

        for field in doc.fields:
            if field.fieldtype != "Link": continue
            doc_field = frappe.db.exists("DocType", field.options)
            if not doc_field: continue
            update_permission_property(doc_field, "SaaS Manager", 0, "set_user_permissions", 1)
        update_permission_property(doc_field, "SaaS Manager", 0, "set_user_permissions", 1)
    frappe.db.commit()