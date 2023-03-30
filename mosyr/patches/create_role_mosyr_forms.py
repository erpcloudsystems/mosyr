import frappe
from erpnext.setup.install import create_custom_role

def execute():   
    # create role Mosyr Forms and added this role for saas manager and employee self service 
    create_custom_role({"role": "Mosyr Forms"})
    frappe.db.commit()

    users = frappe.get_list("User")
    if len(users) > 0:
        for user in users:
            user = frappe.get_doc("User", user)
            if user.user_type not in ["System User", "SaaS Manager", "Website User"]:
                utype = user.user_type
                user.db_set("user_type", "System User")
                user.save(ignore_permissions=True)
                frappe.db.commit()

                user.add_roles("Mosyr Forms")
                frappe.db.commit()

                user.db_set("user_type", utype)
                frappe.db.commit()