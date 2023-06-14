import frappe 
import json

def after_migrate():
    disable_email_footer()
    create_email_account()


def disable_email_footer():
    system_settings = frappe.get_single("System Settings")
    if not system_settings.disable_standard_email_footer:
        system_settings.disable_standard_email_footer = 1
        system_settings.save()
        frappe.db.commit()

def create_email_account():
    """
    Create email account for outgoing and incoming emails in system
    get data from site configuration
    * Note this process not working in after install functionality
    """
    email_config = frappe.conf.get("email_acc_config", False)
    if not email_config:
        return
    try:
        email_config = json.loads(email_config)
        email_acc_name =  email_config.get("name", False)
        if frappe.db.exists("Email Account", email_acc_name):
            return

        email_acc = frappe.new_doc("Email Account")
        email_acc.update(email_config)
        email_acc.flags.ignore_permissions = True
        email_acc.save()
        frappe.db.commit()

    except:
        frappe.db.rollback()
        traceback = frappe.get_traceback()
        frappe.log_error(
            title=("Error while creating email account for {}").format(email_config.get("email_account_name")),
            message=traceback
        )
