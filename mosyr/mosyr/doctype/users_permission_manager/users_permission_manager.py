# Copyright (c) 2022, AnvilERP and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.installer import update_site_config

from six import iteritems

from erpnext.setup.install import create_custom_role, create_role_permissions_for_doctype, update_select_perm_after_install

class UsersPermissionManager(Document):
	
	@frappe.whitelist()
	def get_permissions(self, user):
		if user == frappe.session.user: return []
		if not frappe.db.exists("User", user): return []
		user = frappe.get_doc("User", user)
		user_type = frappe.get_doc("User Type", user.user_type)
		if user_type.is_standard: return []

		return [{
			"document_type": perm.document_type,
			"is_custom": perm.is_custom,
			"read": perm.read,
			"write": perm.write,
			"create": perm.create,
			"submit": perm.submit,
			"cancel": perm.cancel,
			"amend": perm.amend,
			"delete": perm.delete
		} for perm in user_type.user_doctypes]
	
	@frappe.whitelist()
	def apply_permissions(self, user, perms):
		if not frappe.db.exists("User", user): return ""
		
		user_types = self.get_user_types_data(user, perms)
		user_type_limit = {}
		for user_type, data in iteritems(user_types):
			user_type_limit.setdefault(frappe.scrub(user_type), 10)

		update_site_config("user_type_doctype_limit", user_type_limit)

		new_type = None
		for user_type, data in iteritems(user_types):
			create_custom_role(data)
			new_type = self.create_user_type(user_type, data)
		
		if new_type:
			user = frappe.get_doc("User", user)
			user.db_set("user_type", new_type)
			frappe.db.commit()

	def get_user_types_data(slef, user, perms):
		doctypes_permissions = {
			"Account": ['read'],
			"Company": ['read'],
		}
		allowed_perms = ['read','write', 'create', 'delete', 'submit', 'cancel', 'amend']
		for doctype in perms:
			document_type = doctype.get("document_type", "")
			if document_type:
				prems = []
				for k, v in doctype.items():
					if k not in allowed_perms: continue
					if v == 1:
						prems.append(k)
				doctypes_permissions.update({
					f"{document_type}": prems
				})

		return {
			f"{user}": {
				"role": f"{user}",
				"apply_user_permission_on": "Employee",
				"user_id_field": "user_id",
				"doctypes": doctypes_permissions,
			}
		}
	def create_user_type(self, user_type, data):
		if frappe.db.exists("User Type", user_type):
			doc = frappe.get_cached_doc("User Type", user_type)
			doc.user_doctypes = []
		else:
			doc = frappe.new_doc("User Type")
			doc.update(
				{
					"name": user_type,
					"role": data.get("role"),
					"user_id_field": data.get("user_id_field"),
					"apply_user_permission_on": data.get("apply_user_permission_on"),
				}
			)

		create_role_permissions_for_doctype(doc, data)
		doc.save(ignore_permissions=True)

		update_select_perm_after_install()

		return doc.name