# Copyright (c) 2022, AnvilERP and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class CompanyController(Document):
    def validate(self):
        deduction_components = [
            {'component': 'Company Risk',                 'abbr':'CRD'},
            {'component': 'Employee Risk',                'abbr':'ERD'},
            {'component': 'Employee Pension',             'abbr':'EPD'},
            {'component': 'Company Pension',              'abbr':'CPD'},
        ]
        cid = frappe.get_doc('Company Id', self.company_id)
        company_name = cid.company or None

        for component in deduction_components:
            salary_component = component['component']
            do_not_include_in_total = 0
            if salary_component in ['Company Risk', 'Company Pension']:
                do_not_include_in_total = 1
            if not frappe.db.exists('Salary Component', salary_component):
                salary_component_abbr = component['abbr']
                component_type = "Deduction"
				
                salary_component_doc = frappe.new_doc("Salary Component")
                salary_component_doc.update({
                    'salary_component': salary_component,
                    'salary_component_abbr': salary_component_abbr,
                    'type': component_type,
					'do_not_include_in_total': do_not_include_in_total
                })
                if company_name:
                    salary_component_doc.append('accounts', {
                        'company': company_name
                    })
                salary_component_doc.save()
