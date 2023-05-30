import frappe 

def after_migrate():
    system_settings = frappe.get_doc("System Settings")
    if not system_settings.disable_standard_email_footer:
        system_settings.disable_standard_email_footer = 0
        
    system_settings.save()
    frappe.db.commit()