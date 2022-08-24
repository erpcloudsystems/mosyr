# Copyright (c) 2022, AnvilERP and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class CompanyController(Document):
    def validate(self):
        employees = frappe.get_list("Employee", filters={'company': self.company})
        for employee in employees:
            employee = frappe.get_doc('Employee', employee.name)
            if employee.social_insurance_type == "Saudi":
                employee.risk_on_employee = 0
                employee.risk_on_company = 0
                employee.pension_on_employee = self.pension_percentage_on_employee
                employee.pension_on_company = self.pension_percentage_on_company
            elif employee.social_insurance_type == "Non Saudi":
                employee.risk_on_employee = self.risk_percentage_on_employee
                employee.risk_on_company = self.risk_percentage_on_company
                employee.pension_on_employee = 0
                employee.pension_on_company = 0
            