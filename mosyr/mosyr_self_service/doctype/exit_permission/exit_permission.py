# Copyright (c) 2023, AnvilERP and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from datetime import timedelta
from frappe import _
from erpnext.hr.utils import validate_active_employee

class OverlapError(frappe.ValidationError):
    pass

class ExitPermission(Document):
    def validate(self):
        validate_active_employee(self.employee)
        self.validate_dates()
        # self.validate_overlap_dates()


    def validate_dates(self):
        if self.from_time and self.to_time and frappe.utils.time_diff_in_seconds(self.to_time , self.from_time) < 0:
            frappe.throw(_("To time cannot be before from time"))

    # def validate_overlap_dates(self):
    #     if not self.name:
    #         self.name = "New Lateness Permission"
    #     d = frappe.db.sql(
    #         """
    #             select
    #                 name, from_date, to_date
    #             from `tabLateness Permission`
    #             where employee = %(employee)s and docstatus < 2
    #             and ((%(from_date)s >= from_date
    #                 and %(from_date)s <= to_date) or
    #                 ( %(to_date)s >= from_date
    #                 and %(to_date)s <= to_date ))
    #             and name != %(name)s""",
    #         {
    #             "employee": self.employee,
    #             "from_date": self.from_date,
    #             "to_date": self.to_date,
    #             "name": self.name,
    #         },
    #         as_dict=1,
    #     )

    #     for date_overlap in d:
    #         if date_overlap["name"]:
    #             self.throw_overlap_error(date_overlap)

    # def throw_overlap_error(self, d):
    #     msg = _("Employee {0} has already applied for Exit Permission between {1} and {2} : ").format(
    #         self.employee, formatdate(d["from_date"]), formatdate(d["to_date"])
    #     ) + """ <b><a href="/app/Form/Lateness Permission/{0}">{0}</a></b>""".format(d["name"])
    #     frappe.throw(msg, OverlapError)

