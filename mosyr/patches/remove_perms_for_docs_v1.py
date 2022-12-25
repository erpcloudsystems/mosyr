
def execute():
    import frappe
    from frappe.core.page.permission_manager.permission_manager import remove as remove_perm
    remove_perm_from = ['Translation', 'System Controller']
    for t in frappe.get_list("User Type"):
        t = frappe.get_doc("User Type", t.name)
        for doc in t.user_doctypes:
            if doc.document_type in remove_perm_from:
                t.remove(doc)
        t.save()
    for doc in remove_perm_from:
        remove_perm(doc, "SaaS Maanger", 0)
    frappe.db.commit()
