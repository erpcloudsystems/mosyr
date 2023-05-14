import frappe

def execute():
    if frappe.db.exists("User Type", "SaaS Manager"):
        saas_manager = frappe.get_doc("User Type", "SaaS Manager")
        prev_docs = frappe.get_all("User Document Type", {"parent": "Saas Manager"}, pluck="document_type")
        new_docs = ["Process Loan Interest Accrual", "Journal Entry", "Account"]
        for doc in new_docs:
            if doc not in prev_docs:
                saas_manager.append("user_doctypes", {
                    "document_type": doc,
                    "read": 1,
                    "write": 1,
                    "create": 1,
                    "submit": 1,
                    "cancel": 1,
                    "delete": 1,
                    "amend": 1
                })
                saas_manager.save(ignore_permissions=True)
                frappe.db.commit()
