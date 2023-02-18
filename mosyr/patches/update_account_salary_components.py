
def execute():
    import frappe
    for sc in frappe.get_list("Salary Component"):
        sc = frappe.get_doc("Salary Component", sc.name)
        sc.save()
    frappe.db.commit()