
import frappe
from frappe.core.doctype.user_type.user_type import UserType
from frappe.core.doctype.user.user import User
class CustomUserType(UserType):
    def add_role_permissions_for_user_doctypes(self):
        perms = ["read", "write", "create", "submit", "cancel", "amend", "delete"]
        for row in self.user_doctypes:
            docperm = add_custom_role_permissions(row.document_type, self.role)

            values = {perm: row.get(perm) or 0 for perm in perms}
            for perm in ["print", "email", "share"]:
                values[perm] = 1

            frappe.db.set_value("Custom DocPerm", docperm, values)

def add_custom_role_permissions(doctype, role):
    name = frappe.get_value("Custom DocPerm", dict(parent=doctype, role=role, permlevel=0))

    if not name:
        name = add_custom_permission(doctype, role, 0)

    return name

def add_custom_permission(doctype, role, permlevel=0, ptype=None):
    """Add a new permission rule to the given doctype
    for the given Role and Permission Level"""
    from frappe.core.doctype.doctype.doctype import validate_permissions_for_doctype
    from frappe.permissions import setup_custom_perms

    setup_custom_perms(doctype)

    if frappe.db.get_value(
        "Custom DocPerm", dict(parent=doctype, role=role, permlevel=permlevel, if_owner=0)
    ):
        return

    if not ptype:
        ptype = "read"

    custom_docperm = frappe.get_doc(
        {
            "doctype": "Custom DocPerm",
            "__islocal": 1,
            "parent": doctype,
            "parenttype": "DocType",
            "parentfield": "permissions",
            "role": role,
            "permlevel": permlevel,
            ptype: 1,
        }
    )

    custom_docperm.save(ignore_permissions=1)

    validate_permissions_for_doctype(doctype)
    return custom_docperm.name

class CustomUser(User):
    def send_welcome_mail_to_user(self):
        from frappe.utils import get_url
        from frappe.utils.user import get_user_fullname
        from frappe import _
        link = self.reset_password()
        welcome_mails = frappe.db.sql("SELECT * FROM `tabEmail Template` WHERE use_for_welcome_email=1", as_dict=1)
        if len(welcome_mails) == 0:
            super().send_welcome_mail_to_user()
        else:
            welcome_mail = frappe._dict(welcome_mails[0])
            if welcome_mail.subject:
                subject = welcome_mail.subject
            else:
                site_name = frappe.db.get_default("site_name") or frappe.get_conf().get("site_name")
                if site_name:
                    subject = _("Welcome to {0}").format(site_name)
                else:
                    subject = _("Complete Registration")
            message = ""
            if welcome_mail.response and isinstance(welcome_mail.response, str):
                jenv = frappe.get_jenv()
                created_by = get_user_fullname(frappe.session["user"])
                if created_by == "Guest":
                    created_by = "Administrator"
                main_args = {
                    "first_name": self.first_name or self.last_name or "user",
                    "user": self.name,
                    "title": subject,
                    "login_url": get_url(),
                    "created_by": created_by,
                }
                args = dict(
                    link=link,
                    site_url=get_url(),
                )
                args.update(frappe._dict(self.as_dict()))
                args.update(frappe._dict(main_args))
                message = jenv.from_string(welcome_mail.response).render(**args)
                self.send_login_custom_mail(
                    subject,
                    message,
                    dict(
                        link=link,
                        site_url=get_url(),
                    ),
                )
    def send_login_custom_mail(self, subject, message, add_args, now=None):
        """send mail with login details"""
        from frappe.utils import get_url
        from frappe.utils.user import get_user_fullname
        from frappe.utils import get_formatted_email
        created_by = get_user_fullname(frappe.session["user"])
        if created_by == "Guest":
            created_by = "Administrator"

        args = {
            "first_name": self.first_name or self.last_name or "user",
            "user": self.name,
            "title": subject,
            "login_url": get_url(),
            "created_by": created_by,
        }

        args.update(add_args)

        sender = (
            frappe.session.user not in ('Guest', 'Administrator', 'support@mosyr.io') and get_formatted_email(frappe.session.user) or None
        )
        frappe.sendmail(
            recipients=self.email,
            sender=sender,
            subject=subject,
            message=message,
            args=args,
            header=[subject, "green"],
            delayed=(not now) if now != None else self.flags.delay_emails,
            retry=3,
        )