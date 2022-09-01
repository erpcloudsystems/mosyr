# Copyright (c) 2022, AnvilERP and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt

class CompanyController(Document):
    def on_update(self):
        
        frappe.db.sql("""
              UPDATE `tabEmployee`
              SET pension_on_employee={}, pension_on_company={},
                  risk_on_employee=0, risk_on_company=0
              WHERE social_insurance_type='Saudi'""".format(flt(self.pension_percentage_on_employee), flt(self.pension_percentage_on_company)))
        
        frappe.db.sql("""
              UPDATE `tabEmployee`
              SET pension_on_employee=0, pension_on_company=0,
                  risk_on_employee={}, risk_on_company={}
              WHERE social_insurance_type='Non Saudi'""".format(flt(self.risk_percentage_on_employee), flt(self.risk_percentage_on_company)))

            