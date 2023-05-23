import frappe

def execute():
    if frappe.db.exists("User Type", "Employee Self Service"):
        user_type = frappe.get_doc("User Type", "Employee Self Service")
        doc_list = frappe.get_list("User Document Type", filters={"parent": "Employee Self Service"}, pluck="document_type")
        doctypes = [
            {"doctype": "Vehicle Services", "read": 1, "write": 1, "create": 1},
            {"doctype": "Vehicle Log", "read": 1, "write": 0, "create": 0},
        ]
        for row in doctypes:
            if row.get("doctype") in doc_list: continue
            user_type.append("user_doctypes",
                            {"document_type": row.get("doctype"),
                                "read": row.get("read"),
                                "write": row.get("write"),
                                "create": row.get("create")
                            }
                        )
            user_type.save()
            frappe.db.commit()
