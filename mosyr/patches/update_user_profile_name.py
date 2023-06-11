import frappe


def execute():
    users = frappe.get_list("User", filters={"enabled": 1})
    if users:
        for row in users:
            user = frappe.get_doc("User", row.name)
            if user.user_type == "Employee Self Service":
                user.db_set("role_profile_name", "Self Service")

            if user.user_type == "SaaS Manager":
                user.db_set("role_profile_name", "SaaS Manager")

            if user.name == "support@mosyr.io":
                user.db_set("role_profile_name", "SaaS Manager")

            frappe.db.commit()
