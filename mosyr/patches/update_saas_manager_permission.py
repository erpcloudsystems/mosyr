import frappe
from frappe.permissions import add_permission, update_permission_property

def execute():
    add_permission("Translation", "SaaS Manager", permlevel=0)
    frappe.db.commit()
    for perm in ["read", "write", "create", "delete", "submit", "cancel", "amend" , "select" , "email" ,"report" ,"print" , "import" , "share"]:
        update_permission_property("Translation" , 'SaaS Manager' , permlevel=0, ptype=perm ,value=1)
    frappe.db.commit()
