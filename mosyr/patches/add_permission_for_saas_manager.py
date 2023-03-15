from mosyr.install import docs_for_manager
from frappe.permissions import update_permission_property
import frappe

def execute():
    add_permission_for_saas_manager()

def add_permission_for_saas_manager():
    for doc in docs_for_manager:
        # Add Select for Doctype and for all links fields
        doc = frappe.db.exists("DocType", doc)
        if not doc: continue
        doc = frappe.get_doc("DocType", doc)
        for field in doc.fields:
            if field.fieldtype != "Link": continue
            doc_field = frappe.db.exists("DocType", field.options)
            if not doc_field: continue
            update_permission_property(doc_field, "SaaS Manager", 0, "select", 1)
            update_permission_property(doc_field, "SaaS Manager", 0, "read", 1)
            update_permission_property(doc_field, "SaaS Manager", 0, "report", 1)
            update_permission_property(doc_field, "SaaS Manager", 0, "write", 1)
            update_permission_property(doc_field, "SaaS Manager", 0, "create", 1)
            update_permission_property(doc_field, "SaaS Manager", 0, "print", 1)
            update_permission_property(doc_field, "SaaS Manager", 0, "email", 1)
            update_permission_property(doc_field, "SaaS Manager", 0, "delete", 1)
            update_permission_property(doc_field, "SaaS Manager", 0, "import", 1)
            update_permission_property(doc_field, "SaaS Manager", 0, "export", 1)
            update_permission_property(doc_field, "SaaS Manager", 0, "email", 1)
            update_permission_property(doc_field, "SaaS Manager", 0, "set_user_permissions", 1)
            update_permission_property(doc_field, "SaaS Manager", 0, "share", 1)

        update_permission_property(doc_field, "SaaS Manager", 0, "select", 1)
        update_permission_property(doc_field, "SaaS Manager", 0, "read", 1)
        update_permission_property(doc_field, "SaaS Manager", 0, "report", 1)
        update_permission_property(doc_field, "SaaS Manager", 0, "write", 1)
        update_permission_property(doc_field, "SaaS Manager", 0, "create", 1)
        update_permission_property(doc_field, "SaaS Manager", 0, "print", 1)
        update_permission_property(doc_field, "SaaS Manager", 0, "email", 1)
        update_permission_property(doc_field, "SaaS Manager", 0, "delete", 1)
        update_permission_property(doc_field, "SaaS Manager", 0, "import", 1)
        update_permission_property(doc_field, "SaaS Manager", 0, "export", 1)
        update_permission_property(doc_field, "SaaS Manager", 0, "email", 1)
        update_permission_property(doc_field, "SaaS Manager", 0, "set_user_permissions", 1)
        update_permission_property(doc_field, "SaaS Manager", 0, "share", 1)
    frappe.db.commit()
