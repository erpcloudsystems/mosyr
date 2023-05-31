# Copyright (c) 2022, AnvilERP and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from mosyr.api import _get_employee_from_user, send_notification_and_email

class EmergencyContact(Document):
	def before_insert(self):
		self.employee = _get_employee_from_user(frappe.session.user)
	
	def on_update(self):
		send_notification_and_email(self)

	def on_submit(self):
		doc = frappe.get_doc("Employee", self.employee)
		doc.emergency_phone_number = self.emergency_phone
		doc.person_to_be_contacted = self.emergency_contact_name
		doc.relation = self.relation
		doc.save()
		frappe.db.commit()
