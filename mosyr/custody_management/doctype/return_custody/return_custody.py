# Copyright (c) 2022, AnvilERP and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe import sendmail, msgprint
from frappe.utils import getdate
from hijri_converter import Hijri, Gregorian


class ReturnCustody(Document):
    def on_submit(self):
        # change returned custody's status -> Returned & returned custody -> name
        custody = frappe.get_doc("Custody", self.custody)
        custody.status = "Returned"
        custody.returned_custody = self.name
        custody.save()
        # send email for recipent employee
        self.send_email()

    def send_email(self):
        recipent = frappe.get_value("Employee", self.recipt_employee, "user_id")
        if recipent:
            sendmail(
                recipients=[recipent],
                subject=_("Return Custody for {0}").format(self.custody),
                message=_(""),
                reference_name=self.custody,
            )
            msgprint(_("email sent successfully for {}".format(self.recipt_employee)))

    @frappe.whitelist()
    def convert_date(self, gregorian_date=None, hijri_date=None):
        if gregorian_date:
            gd, gm, gy = (
                getdate(gregorian_date).day,
                getdate(gregorian_date).month,
                getdate(gregorian_date).year,
            )
            hijri = Gregorian(gy, gm, gd).to_hijri()
            return str(hijri)

        if hijri_date:
            hd, hm, hy = (
                getdate(hijri_date).day,
                getdate(hijri_date).month,
                getdate(hijri_date).year,
            )
            gregorian = Hijri(hy, hd, hm).to_gregorian()
            return str(gregorian)
