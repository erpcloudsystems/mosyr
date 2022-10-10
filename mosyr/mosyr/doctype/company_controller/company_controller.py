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
        
        has_new_letter_head = False
        company_name = self.organization_english if self.organization_english else frappe.db.get_value("Company Id", self.company_id, "company")
        html_header_content = ''
        html_footer_content = ''
        image = ''
        if self.logo:
            has_new_letter_head = True
            image = self.logo
            html_header_content = '''<div class="container-fluid">
    <div class="row">
        <div class="col-sm-6 text-left">
            <img src="{}" style="max-width: 124px; max-height: 124px;">
        </div>
        <div class="col-sm-6 text-right">
            <h3>{}</h3>
        </div>
    </div>
</div>'''.format(self.logo, company_name)
        
        if len(self.signatures) > 0:
            has_new_letter_head = True
            for signature in self.signatures:
                job_title = signature.job_title or ""
                employee_name = frappe.db.get_value("Employee", signature.name1, "employee_name")
                html_footer_content += '''<div class="col-sm-4 text-right">
                                                <p class="text-center" style="font-weight: bold">{}</p>
                                                <p class="text-center" style="font-weight: bold">{}</p>
                                              </div>'''.format(job_title, employee_name)
            
            
            html_footer_content = '<div class="container-fluid"><div class="row">' + html_footer_content + '</div></div>'
        if has_new_letter_head:
            lh = frappe.db.exists("Letter Head", "Mosyr-Main")
            
            if lh:
                lh = frappe.get_doc("Letter Head", "Mosyr-Main")
            else: 
                lh = frappe.new_doc("Letter Head")
                lh.letter_head_name = "Mosyr-Main"
            lh.source = "HTML"
            lh.footer_source = "HTML"
            lh.is_default = 1
            # lh.image = image
            lh.content = html_header_content
            lh.footer = html_footer_content
            lh.save()
            frappe.db.commit()
            lh.db_set('source', "HTML")
            lh.db_set('footer', html_footer_content)
