# Copyright (c) 2022, AnvilERP and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from mosyr.api import _get_employee_from_user


class PassportDetails(Document):
    def before_insert(self):
        self.employee = _get_employee_from_user(frappe.session.user)

    def on_submit(self):
        doc = frappe.get_doc("Employee", self.employee)
        doc.passport = self.passports

        doc.save()
        frappe.db.commit()
