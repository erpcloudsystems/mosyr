import frappe

def execute():
    default_company = frappe.defaults.get_global_default("company")
    company_controller = frappe.db.exists("Company Controller", default_company)
    if company_controller :
        company_controller = frappe.get_doc("Company Controller", default_company)
        company = frappe.get_doc("Company", default_company)
        company.company_id = company_controller.company_id
        company.organization_arabic = company_controller.organization_arabic
        company.organization_english = company_controller.organization_english
        company.sender_name_sms = company_controller.sender_name_sms
        company.mail_sender_name = company_controller.mail_sender_name
        company.mobile = company_controller.mobile
        company.mail_sender_address = company_controller.mail_sender_address
        company.labors_office_file_no = company_controller.labors_office_file_no
        company.logo = company_controller.logo
        company.stamp = company_controller.stamp
        company.cr_document = company_controller.cr_document
        company.baladiya_license = company_controller.baladiya_license
        company.left_header = company_controller.left_header
        company.right_header = company_controller.right_header
        company.disbursement_type = company_controller.disbursement_type
        company.bank_name = company_controller.bank_name
        company.english_name_in_bank = company_controller.english_name_in_bank
        company.month_days = company_controller.month_days
        company.bank_code = company_controller.bank_code
        company.calendar_accreditation = company_controller.calendar_accreditation
        company.establishment_number = company_controller.establishment_number
        company.bank_account_number = company_controller.bank_account_number
        company.risk_percentage_on_employee = company_controller.risk_percentage_on_employee
        company.risk_percentage_on_company = company_controller.risk_percentage_on_company
        company.pension_percentage_on_employee = company_controller.pension_percentage_on_employee
        company.pension_percentage_on_company = company_controller.pension_percentage_on_company
        company.establishment_number = company_controller.establishment_number
        company.agreement_symbol = company_controller.agreement_symbol
        company.agreement_number_for_customer = company_controller.agreement_number_for_customer

        for signature in company_controller.signatures:
            row = company.append("signatures", {})
            row.name1 = signature.name1
            row.job_title = signature.job_title
            row.payrolls_and_reports = signature.payrolls_and_reports
            row.reports = signature.reports
        
        company.save()
        frappe.db.commit()