
import frappe

def execute():
    if frappe.db.exists("User Type", "SaaS Manager"):
        saas_manager = frappe.get_doc("User Type", "SaaS Manager")
        user_docs = frappe.get_list("User Document Type", filters={"parent": "SaaS Manager"}, pluck="document_type")
        doctypes = ["Loan Interest Accrual", "Loan Repayment"]
        for doc in doctypes:
            if doc not in user_docs:
                saas_manager.append("user_doctypes", {
                    "document_type": doc,
                    "read": 1,
                    "write": 1,
                    "create": 1,
                    "select": 1,
                    "submit": 1,
                    "cancel": 1,
                    "delete": 1,
                    "amend": 1
                })
        saas_manager.save()
        frappe.db.commit()
