import frappe 

def after_migrate():
    system_settings = frappe.get_single("System Settings")
    if not system_settings.disable_standard_email_footer:
        system_settings.disable_standard_email_footer = 1
        
    system_settings.save()
    frappe.db.commit()