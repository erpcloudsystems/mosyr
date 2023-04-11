import frappe
from frappe.core.doctype.user.user import User


class CustomUser(User):
    def send_welcome_mail_to_user(self):
        from frappe.utils import get_url
        from frappe.utils.user import get_user_fullname
        from frappe import _

        link = self.reset_password()
        welcome_mails = frappe.db.sql(
            "SELECT * FROM `tabEmail Template` WHERE use_for_welcome_email=1", as_dict=1
        )
        if len(welcome_mails) == 0:
            super().send_welcome_mail_to_user()
        else:
            welcome_mail = frappe._dict(welcome_mails[0])
            if welcome_mail.subject:
                subject = welcome_mail.subject
            else:
                site_name = frappe.db.get_default("site_name") or frappe.get_conf().get(
                    "site_name"
                )
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
            frappe.session.user not in ("Guest", "Administrator", "support@mosyr.io")
            and get_formatted_email(frappe.session.user)
            or None
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
