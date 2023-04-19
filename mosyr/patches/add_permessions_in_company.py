import frappe
from frappe.permissions import add_permission, update_permission_property

def execute():
    add_permission("Company", "SaaS Manager", permlevel=0)
    add_permission("Address", "SaaS Manager", permlevel=0)
    add_permission("Mode of Payment", "SaaS Manager", permlevel=0)
    frappe.db.commit()
    for perm in ["read", "write", "create", "submit", "cancel", "amend" , "select" , "email" ,"report" ,"print" , "import" , "report", "share"]:
        update_permission_property("Company" , 'SaaS Manager' , permlevel=0, ptype=perm ,value=1)
        update_permission_property("Mode of Payment" , 'SaaS Manager' , permlevel=0, ptype=perm ,value=1)
    frappe.db.commit()