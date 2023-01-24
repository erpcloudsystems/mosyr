import frappe
from frappe.permissions import update_permission_property
perms = [
    "read",
    "select",
    "write",
    "create",
    "delete",
    "submit",
    "cancel",
    "amend",
    "read",
    "report",
    "set_user_permissions"
]
def execute():
    docs_for_manager = ["Email Account", "Email Template", "Email Domain"]
    for doc in docs_for_manager:
        # Add Select for Doctype and for all links fields
        doc = frappe.db.exists("DocType", doc)
        if not doc: continue
        doc = frappe.get_doc("DocType", doc)

        for field in doc.fields:
            if field.fieldtype != "Link": continue
            doc_field = frappe.db.exists("DocType", field.options)
            if not doc_field: continue
            for p in perms:
                update_permission_property(doc_field, "SaaS Manager", 0, p, 1)
        for p in perms:
            update_permission_property(doc.name, "SaaS Manager", 0, p, 1)
    frappe.db.commit()