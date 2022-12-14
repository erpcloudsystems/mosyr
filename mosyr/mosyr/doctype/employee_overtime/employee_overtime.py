# Copyright (c) 2022, AnvilERP and contributors
# For license information, please see license.txt
import datetime

import frappe
from frappe import _
from frappe.utils import flt, cint

from frappe.model.document import Document


class EmployeeOvertime(Document):
    def validate(self):
        try:
            datetime.datetime.strptime(self.payroll_month, "%Y-%m")
        except ValueError:
            frappe.throw(_("Incorrect data format, should be YYYY-MM"))
            return
        if (self.from_biometric) == 0:
            by_1_5 = flt(self.hour_rate) * 1.5 * flt(self.overtime_hours_by_1_5)
            by_2 = flt(self.hour_rate) * 2 * flt(self.overtime_hours_by_2)
            self.amount = by_1_5 + by_2

    @frappe.whitelist()
    def apply_in_system(self):
        # adds = frappe.get_list('Additional Salary', filters={'employee_deduction': self.name})
        # if len(adds) > 0:
        #     frappe.throw(_('{} Applied in the System see <a href="/app/additional-salary/EB-2022-02-01">Additional Salary<a/>'.format(self.name, adds[0])))

        eadd = frappe.new_doc("Additional Salary")
        eadd.employee = self.employee
        eadd.amount = flt(self.amount)
        eadd.salary_component = "Overtime"
        eadd.payroll_date = datetime.datetime.strptime(
            f"{self.payroll_month}-01", "%Y-%m-%d"
        )
        eadd.reason = self.notes
        eadd.employee_overtime = self.name
        eadd.save()
        eadd.submit()
        self.db_set("status", "Applied In System", update_modified=False)
        frappe.db.commit()
        return "Applied In System"
