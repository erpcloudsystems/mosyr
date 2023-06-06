import frappe

def execute():
    if frappe.db.exists("User Type", "Employee Self Service"):
        selfservice_user = frappe.get_doc("User Type", "Employee Self Service")
        prev_docs = frappe.get_all("User Document Type", {"parent": "Employee Self Service"}, pluck="document_type")

        if "Letter" not in prev_docs:
            selfservice_user.append("user_doctypes", {
                "document_type": "Letter",
                "read": 1
            })
            selfservice_user.save(ignore_permissions=True)
            frappe.db.commit()
