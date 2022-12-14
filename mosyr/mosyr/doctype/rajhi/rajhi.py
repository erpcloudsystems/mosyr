# Copyright (c) 2022, AnvilERP and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.model.naming import make_autoname


class Rajhi(Document):
    def autoname(self):
        self.name = make_autoname(self.rajhi_date + ".##")
