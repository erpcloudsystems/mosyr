# Copyright (c) 2022, AnvilERP and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class CashCustody(Document):
	def on_submit(self):
		self.estimated_value = self.custody_value
		self.save()