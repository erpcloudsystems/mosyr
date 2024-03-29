# Copyright (c) 2023, AnvilERP and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _
from erpnext.hr.utils import validate_active_employee
from frappe.utils import time_diff_in_seconds, get_datetime_str, time_diff_in_hours
from mosyr.api import send_notification_and_email

class ExitPermission(Document):
    def validate(self):
        validate_active_employee(self.employee)
        self.validate_exit_times()
        self.shift = self.get_shift(self.employee)
    def validate_exit_times(self):
        if not self.to_time or not self.from_time:
            return
        
        exit_hours = time_diff_in_hours(self.to_time, self.from_time)
        if exit_hours <= 0:
            frappe.throw(_("To Time must be after From Time"))
        self.exit_hours = exit_hours

    def on_update(self):
        send_notification_and_email(self)
        pass
    
    def on_submit(self):
        def create_checkin(employee, log_type, time ):
            doc = frappe.new_doc("Employee Checkin")
            doc.employee = employee
            doc.log_type = log_type
            doc.time = time
            doc.save()
            frappe.db.commit()
        if self.workflow_state == "Approved by HR":
            if self.shift:
                shift_type = frappe.get_doc("Shift Type", self.shift)
                exit_permission_datetime_from = get_datetime_str(f'{self.date} {self.from_time}')
                exit_permission_datetime_to = get_datetime_str(f'{self.date} {self.to_time}')
                shift_datetime_start_time = get_datetime_str(f'{self.date} {shift_type.start_time}')
                shift_datetime_end_time = get_datetime_str(f'{self.date} {shift_type.end_time}')

                if time_diff_in_seconds(exit_permission_datetime_from, shift_datetime_start_time) <= 0:
                    if time_diff_in_seconds(exit_permission_datetime_to, shift_datetime_start_time) >= 0:
                        create_checkin(self.employee, "IN", shift_datetime_start_time)
                if time_diff_in_seconds(exit_permission_datetime_from, shift_datetime_end_time) <= 0:
                    if time_diff_in_seconds(exit_permission_datetime_to, shift_datetime_end_time) >= 0:
                        create_checkin(self.employee, "OUT", shift_datetime_end_time)
                        
    def get_shift(self, employee):
        from erpnext.hr.doctype.shift_assignment.shift_assignment import get_employee_shift
        shift_actual_timings = get_employee_shift(employee, frappe.utils.getdate(self.date), False, None)
        if shift_actual_timings:
            return shift_actual_timings.shift_type.name
        return 