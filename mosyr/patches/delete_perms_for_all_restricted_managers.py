import frappe

def execute():
    perms_to_delete = frappe.db.sql("""
        SELECT usp.name as name
        FROM `tabUser Permission` usp
        LEFT JOIN `tabUser` user ON usp.user = user.name
        WHERE user.user_type = 'SaaS Manager' and usp.allow<>'Company'
    """, as_dict=True)
    for up in perms_to_delete:
        up = frappe.get_doc('User Permission', up.name)
        up.delete()
    frappe.db.commit()