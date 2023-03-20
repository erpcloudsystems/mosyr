import frappe


def execute():
    convert_webiste_user_to_self_service()

def convert_webiste_user_to_self_service():
    users = frappe.get_list("User", {"user_type":"Webiste User"})
    for user in users:
        u = frappe.get_doc("User", user)
        u.db_set("user_type", "Employee Self Service")
        frappe.db.commit()