# Copyright (c) 2023, AnvilERP and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _
from erpnext.hr.utils import validate_active_employee
from frappe.utils import time_diff_in_hours

class ExitPermission(Document):
    def validate(self):
        validate_active_employee(self.employee)
        self.validate_exit_times()


    def validate_exit_times(self):
        if not self.to_time or not self.from_time:
            return
        
        exit_hours = time_diff_in_hours(self.to_time, self.from_time)
        if exit_hours <= 0:
            frappe.throw(_("To Time must be after From Time"))
        self.exit_hours = exit_hours
