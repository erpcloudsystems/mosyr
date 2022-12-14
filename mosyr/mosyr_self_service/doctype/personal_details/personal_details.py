# Copyright (c) 2022, AnvilERP and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from mosyr.api import _get_employee_from_user


class PersonalDetails(Document):
    def before_insert(self):
        self.employee = _get_employee_from_user(frappe.session.user)

    def on_submit(self):
        doc = frappe.get_doc("Employee", self.employee)
        doc.passport_number = self.passport_number
        doc.date_of_issue = self.date_of_issue
        doc.valid_upto = self.valid_upto
        doc.place_of_issue = self.place_of_issue
        doc.id_number = self.id_number
        doc.id_date_of_issue = self.id_date_of_issue
        doc.id_valid_upto = self.id_valid_upto
        doc.id_place_of_issue = self.id_place_of_issue
        doc.copy_of_id = self.copy_of_id
        doc.driving_licence_number = self.driving_licence_number
        doc.licence_date_of_issue = self.licence_date_of_issue
        doc.licence_valid_upto = self.licence_valid_upto
        doc.licence_copy_image = self.attach_licence_copy
        doc._number_of_dependants = self.number_of_dependants
        doc.copy_of_passport = self.copy_of_passport
        doc.marital_status = self.marital_status
        doc.wedding_certificate = self.wedding_certificate
        doc.spouse_name = self.spouse_name
        doc.spouse_working_status = self.spouse_working_status
        doc.blood_group = self.blood_group
        doc.family_background = self.family_background
        doc.health_details = self.health_details

        doc.save()
        frappe.db.commit()
