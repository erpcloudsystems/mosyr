# Copyright (c) 2022, AnvilERP and contributors
# For license information, please see license.txt

from datetime import timedelta

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import cint, flt, formatdate, getdate

from erpnext.hr.utils import validate_active_employee


class OverlapError(frappe.ValidationError):
    pass


class LatenessPermission(Document):
    def validate(self):
        validate_active_employee(self.employee)
        self.validate_dates()
        self.validate_overlap_dates()

    def on_submit(self):
        if self.workflow_state == "Approved by HR":
            sr = frappe.new_doc("Shift Request")
            sr.shift_type = self.shift_type
            sr.employee = self.employee
            sr.department = self.department
            sr.company = self.company
            sr.from_date = self.from_date
            sr.to_date = self.to_date
            sr.status = "Approved"
            sr.lateness_permission = self.name
            sr.flags.ignore_mandatory = True
            sr.save()
            sr.submit()

    def on_cancel(self):
        shift_request_list = frappe.get_list(
            "Shift Request", {"lateness_permission": self.name}
        )
        if shift_request_list:
            for shift in shift_request_list:
                shift_request_doc = frappe.get_doc("Shift Request", shift["name"])
                shift_request_doc.cancel()

    def validate_dates(self):
        if (
            self.from_date
            and self.to_date
            and (getdate(self.to_date) < getdate(self.from_date))
        ):
            frappe.throw(_("To date cannot be before from date"))

    def validate_overlap_dates(self):
        if not self.name:
            self.name = "New Lateness Permission"
        d = frappe.db.sql(
            """
                select
                    name, from_date, to_date
                from `tabLateness Permission`
                where employee = %(employee)s and docstatus < 2
                and ((%(from_date)s >= from_date
                    and %(from_date)s <= to_date) or
                    ( %(to_date)s >= from_date
                    and %(to_date)s <= to_date ))
                and name != %(name)s""",
            {
                "employee": self.employee,
                "from_date": self.from_date,
                "to_date": self.to_date,
                "name": self.name,
            },
            as_dict=1,
        )

        for date_overlap in d:
            if date_overlap["name"]:
                self.throw_overlap_error(date_overlap)

    def throw_overlap_error(self, d):
        msg = _(
            "Employee {0} has already applied for Lateness between {1} and {2} : "
        ).format(
            self.employee, formatdate(d["from_date"]), formatdate(d["to_date"])
        ) + """ <b><a href="/app/Form/Lateness Permission/{0}">{0}</a></b>""".format(
            d["name"]
        )
        frappe.throw(msg, OverlapError)
