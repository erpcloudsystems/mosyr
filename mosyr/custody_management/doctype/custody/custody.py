# Copyright (c) 2022, AnvilERP and contributors
# For license information, please see license.txt

import frappe
from frappe import _, throw
from frappe.model.document import Document

class Custody(Document):
    def validate(self):
        if self.employee == self.recipient:
            throw(_("Responsible Employee Can't be the Same of Recipient Employee"))