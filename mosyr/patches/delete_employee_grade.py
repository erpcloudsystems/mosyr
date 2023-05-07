
import frappe

def execute():
    system_controller = frappe.get_doc("System Controller")
    items = system_controller.sidebar_item
    if len(items) == 0:
        return

    for row in items:
        if row.doc_name == "Employee Grade":
            index = row.idx if row.idx == 0 else row.idx - 1
            del items[index]
            system_controller.save()
            frappe.db.commit()
