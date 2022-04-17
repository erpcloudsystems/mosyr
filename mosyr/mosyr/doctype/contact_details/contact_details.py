# Copyright (c) 2022, AnvilERP and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from mosyr.api import _get_employee_from_user

class ContactDetails(Document):
	def before_insert(self):
		self.employee = _get_employee_from_user(frappe.session.user)

	def on_submit(self):
		doc = frappe.get_doc("Employee", self.employee)
		doc.cell_number = self.cell_number
		doc.prefered_contact_email = self.prefered_contact_email
		doc.prefered_email = self.prefered_email
		doc.company_email = self.company_email
		doc.personal_email = self.personal_email
		doc.unsubscribed = self.unsubscribed
		doc.second_mobile = self.second_mobile
		doc.permanent_address_is = self.permanent_address_is
		doc.permanent_address = self.permanent_address
		doc.current_address_is = self.current_address_is
		doc.current_address = self.current_address

		doc.save()
		frappe.db.commit()

