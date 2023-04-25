from frappe.permissions import add_permission
import frappe

def execute():
    add_permission("Domain", "Saas Manager", permlevel=0, ptype=None)
    frappe.db.commit()
