import frappe

def execute():
    settings = frappe.get_doc('HR Settings')
    if settings.leave_approver_mandatory_in_leave_application:
        settings.leave_approver_mandatory_in_leave_application = 0
        settings.save()
        frappe.db.commit()