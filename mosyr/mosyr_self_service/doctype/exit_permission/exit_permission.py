# Copyright (c) 2023, AnvilERP and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _
from erpnext.hr.utils import validate_active_employee
from frappe.utils import time_diff_in_hours
from frappe.utils import get_datetime ,time_diff_in_seconds, datetime
from erpnext.hr.doctype.shift_assignment.shift_assignment import get_actual_start_end_datetime_of_shift

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
                if time_diff_in_seconds(str(self.from_time), str(shift_type.start_time)) <= 0:
                    if time_diff_in_seconds(str(self.to_time), str(shift_type.start_time)) >= 0:
                        shift_datetime = f'{self.date} {shift_type.start_time}'
                        shift_datetime = datetime.datetime.strptime(shift_datetime, "%Y-%m-%d %H:%M:%S")
                        create_checkin(self.employee, "IN", shift_datetime)
                if time_diff_in_seconds(str(self.from_time), str(shift_type.end_time)) <= 0:
                    if time_diff_in_seconds(str(self.to_time), str(shift_type.end_time)) >= 0:
                        shift_datetime = f'{self.date} {shift_type.end_time}'
                        shift_datetime = datetime.datetime.strptime(shift_datetime, "%Y-%m-%d %H:%M:%S")
                        create_checkin(self.employee, "OUT", shift_datetime)
    # @frappe.whitelist()
    # def get_employee_shift(self, employee):
    #     shift_actual_timings = get_actual_start_end_datetime_of_shift(
    #     employee, get_datetime(self.from_time), True
    #     )
    #     if shift_actual_timings[0] and shift_actual_timings[1]:
    #         return shift_actual_timings[2].shift_type.name
    #     return False