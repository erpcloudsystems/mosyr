# Copyright (c) 2023, AnvilERP and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _
from erpnext.hr.utils import validate_active_employee

class ExitPermission(Document):
    def validate(self):
        validate_active_employee(self.employee)
        self.validate_dates()


    def validate_dates(self):
        if self.from_time and self.to_time and frappe.utils.time_diff_in_seconds(self.to_time , self.from_time) < 0:
            frappe.throw(_("To time cannot be before from time"))
