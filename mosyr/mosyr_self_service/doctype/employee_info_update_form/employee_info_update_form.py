# Copyright (c) 2022, AnvilERP and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _
from erpnext.hr.utils import validate_active_employee


class EmployeeInfoUpdateForm(Document):
    def validate(self):
        validate_active_employee(self.employee)
        if self.clear_if_empty == 0 and self._update in [
            "Identity",
            "Dependents",
            "Passports",
            "Qualifications",
        ]:
            field_name = self._update.lower()
            if len(self.get(field_name)) == 0:
                frappe.throw(
                    _("check clear if empty for empty {}".format(self._update))
                )

    def on_submit(self):
        if self.status not in ["Approved", "Rejected"]:
            frappe.throw(
                _(
                    "Only Document with status 'Approved' and 'Rejected' can be submitted"
                )
            )

        if self.status == "Approved":
            employee = frappe.get_doc("Employee", self.employee)

            if self._update == "Identity":
                employee.identity = []
                if self.clear_if_empty == 1 and len(self.identity) == 0:
                    employee.save()
                    frappe.db.commit()
                    return
                else:
                    for row in self.identity:
                        employee.append(
                            "identity",
                            {
                                "id_type": row.id_type,
                                "id_number": row.id_number,
                                "issue_place": row.issue_place,
                                "issue_date": row.issue_date,
                                "issue_date_h": row.issue_date_h,
                                "issue_place_english": row.issue_place_english,
                                "expire_date": row.expire_date,
                                "expire_date_h": row.expire_date_h,
                                "border_entry_port": row.border_entry_port,
                                "border_entry_date": row.border_entry_date,
                                "border_entry_date_h": row.border_entry_date_h,
                                "border_entry_number": row.border_entry_number,
                                "identity_name": row.identity_name,
                                "id_photo": row.id_photo,
                                "key": row.key,
                            },
                        )
                    employee.save()
                    frappe.db.commit()
                    return

            elif self._update == "Dependents":
                employee.dependent = []
                if self.clear_if_empty == 1 and len(self.dependents) == 0:
                    employee.save()
                    frappe.db.commit()
                    return
                else:
                    for row in self.dependents:
                        employee.append(
                            "dependent",
                            {
                                "relationship": row.relationship,
                                "birth_date_g": row.birth_date_g,
                                "birth_date_h": row.birth_date_h,
                                "attachment": row.attachment,
                                "first_name_ar": row.first_name_ar,
                                "father_name_ar": row.father_name_ar,
                                "grand_father_name_ar": row.grand_father_name_ar,
                                "family_name_ar": row.family_name_ar,
                                "full_name_ar": row.full_name_ar,
                                "first_name_en": row.first_name_en,
                                "father_name_en": row.father_name_en,
                                "grand_father_name_en": row.grand_father_name_en,
                                "family_name_en": row.family_name_en,
                                "dependant_en": row.dependant_en,
                                "insurance_card_company": row.insurance_card_company,
                                "insurance_card_number": row.insurance_card_number,
                                "insurance_card_class": row.insurance_card_class,
                                "insurance_card_expire": row.insurance_card_expire,
                                "key": row.key,
                            },
                        )
                    employee.save()
                    frappe.db.commit()
                    return

            elif self._update == "Passports":
                employee.passport = []
                if self.clear_if_empty == 1 and len(self.passports) == 0:
                    employee.save()
                    frappe.db.commit()
                    return
                else:
                    for row in self.passports:
                        employee.append(
                            "passport",
                            {
                                "passport_number": row.passport_number,
                                "passport_issue_date": row.passport_issue_date,
                                "passport_issue_date_h": row.passport_issue_date_h,
                                "jobtitle": row.jobtitle,
                                "passport_issue_place": row.passport_issue_place,
                                "passport_expire": row.passport_expire,
                                "passport_expire_h": row.passport_expire_h,
                                "passport_photo": row.passport_photo,
                                "key": row.key,
                            },
                        )
                    employee.save()
                    frappe.db.commit()
                    return

            elif self._update == "Qualifications":
                employee.education = []
                if self.clear_if_empty == 1 and len(self.qualifications) == 0:
                    employee.save()
                    frappe.db.commit()
                    return
                else:
                    for row in self.qualifications:
                        employee.append(
                            "education",
                            {
                                "passport_number": row.passport_number,
                                "passport_issue_date": row.passport_issue_date,
                                "passport_issue_date_h": row.passport_issue_date_h,
                                "jobtitle": row.jobtitle,
                                "passport_issue_place": row.passport_issue_place,
                                "passport_expire": row.passport_expire,
                                "passport_expire_h": row.passport_expire_h,
                                "passport_photo": row.passport_photo,
                                "key": row.key,
                            },
                        )
                    employee.save()
                    frappe.db.commit()
                    return
            elif self._update == "Contacts":
                pass

    def fetch_employee_details(self, employee, field):
        pass
