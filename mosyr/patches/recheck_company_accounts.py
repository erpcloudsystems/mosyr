
def execute():
    import frappe
    for company in frappe.get_all('Company'):
        company = frappe.get_doc('Company', company.name)
        try: company.on_update()
        except: pass
    frappe.db.commit()