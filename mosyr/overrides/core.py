import frappe
from frappe.core.doctype.user.user import User
from frappe.utils import cint
from frappe import STANDARD_USERS, _


class CustomUser(User):
	def send_welcome_mail_to_user(self):
		from frappe.utils import get_url
		from frappe import _

		link = self.reset_password()
		welcome_mails = frappe.db.sql(
			"SELECT * FROM `tabEmail Template` WHERE use_for_welcome_email=1", as_dict=1
		)
		if len(welcome_mails) == 0:
			super().send_welcome_mail_to_user()
		else:
			subject = None
			welcome_mail = frappe._dict(welcome_mails[0])
			if welcome_mail.subject:
				subject = welcome_mail.subject
			else:
				method = frappe.get_hooks("welcome_email")
				if method:
					subject = frappe.get_attr(method[-1])()
				if not subject:
					site_name = frappe.db.get_default("site_name") or frappe.get_conf().get("site_name")
					if site_name:
						subject = _("Welcome to {0}").format(site_name)
					else:
						subject = _("Complete Registration")

			self.send_login_mail(
				subject,
				"Create Subscription",
				dict(
					link=link,
					site_url=get_url(),
				),
			)

	def send_login_mail(self, subject, template, add_args, now=None):
		"""send mail with login details"""
		from frappe.utils import get_url
		from frappe.utils.user import get_user_fullname

		created_by = get_user_fullname(frappe.session["user"])
		if created_by == "Guest":
			created_by = "Administrator"

		email_template = frappe.get_doc("Email Template", template)

		args = {
			"first_name": self.first_name or self.last_name or "user",
			"user": self.name
		}

		args.update(add_args)

		content = frappe.render_template(email_template.response_html, args)
		
		hr_settings = frappe.get_doc("HR Notification Settings")
		sender = frappe.get_value("Email Account", hr_settings.notification_default_email, "email_id")
		
		frappe.sendmail(
			recipients=self.email,
			subject=subject,
			message=content,
			sender=sender,
			now=1,
			retry=3,
		)
	
	def add_system_manager_role(self):
		# if adding system manager, do nothing
		if not cint(self.enabled) or (
			"System Manager" in [user_role.role for user_role in self.get("roles")]
		):
			return

		if (
			self.name not in STANDARD_USERS
			and self.user_type == "System User"
			and not self.get_other_system_managers()
			and cint(frappe.db.get_single_value("System Settings", "setup_complete"))
		):

			self.append("roles", {"doctype": "Has Role", "role": "System Manager"})

		if self.name == "Administrator":
			# Administrator should always have System Manager Role
			self.extend(
				"roles",
				[
					{"doctype": "Has Role", "role": "System Manager"},
					{"doctype": "Has Role", "role": "Administrator"},
				],
			)
			
	def validate_roles(self):
		if self.role_profile_name:
			role_profile = frappe.get_doc("Role Profile", self.role_profile_name)
			self.append_roles(*[role.role for role in role_profile.roles])