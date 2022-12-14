import frappe


def execute():
    if frappe.db.exists("Report", "Attendance"):
        field_doc = frappe.get_doc("Report", "Attendance")
        field_doc.delete()
        frappe.db.commit()
