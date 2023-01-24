import frappe
from frappe.installer import update_site_config

def execute():
    types = frappe.get_list("User Type", filters={'is_standard': 0})
    user_type_limit = {}
    for utype in types:
        user_type_limit.setdefault(frappe.scrub(utype.name), 10000)
    update_site_config("user_type_doctype_limit", user_type_limit)