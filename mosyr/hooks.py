from . import __version__ as app_version

app_name = "mosyr"
app_title = "Mosyr"
app_publisher = "AnvilERP"
app_description = "Mosyr Customization App"
app_icon = "octicon octicon-file-directory"
app_color = "grey"
app_email = "support@anvilerp.com"
app_license = "MIT"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
app_include_css = [
	"/assets/mosyr/css/mosyr.min.css",
	"/assets/mosyr/css/hcalendar.min.css"
]
app_include_js = [
	"/assets/mosyr/js/mosyr.min.js",
	"/assets/mosyr/js/hcalendar.min.js"
]

# include js, css files in header of web template
# web_include_css = "/assets/mosyr/css/mosyr.css"
# web_include_js = "/assets/mosyr/js/mosyr.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "mosyr/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
doctype_js = {
	"Employee" : "public/js/employee.js",
	"Loan" : "public/js/loan.js",
	"Payroll Entry" : "public/js/erpnext_custom/payroll_entry.js",
	"Company" : "public/js/company.js",
	"Holiday List": "public/js/holiday_list.js",
	"Salary Component": "public/js/salary_component.js"
}

doctype_list_js = {
    "Loan" : "public/js/loan_list.js",
    "Salary Slip" : "public/js/salary_slip_list.js",
    "Payroll Entry" : "public/js/payroll_entry_list.js",
    "Retention Bonus" : "public/js/retention_bonus_list.js",
    "Employee Incentive" : "public/js/employee_incentive_list.js",
	}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------

# before_install = "mosyr.install.before_install"
after_install = "mosyr.install.after_install"

# boot_session = "mosyr.boot.boot_session"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "mosyr.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }
extend_bootinfo = "mosyr.boot.boot_session"

# DocType Class
# ---------------
# Override standard doctype classes

override_doctype_class = {
	"Mode of Payment": 		"mosyr.overrides.accounts.CustomModeofPayment",

	"Company": 				"mosyr.overrides.hr.CustomCompany",
	"Employee": 			"mosyr.overrides.hr.CustomEmployee",
	"Department": 			"mosyr.overrides.hr.CustomDepartment",
	"Travel Request": 		"mosyr.overrides.hr.CustomTravelRequest",
	"Expense Claim": 		"mosyr.overrides.hr.CustomExpenseClaim",
	"Employee Advance": 	"mosyr.overrides.hr.CustomEmployeeAdvance",
	"Expense Claim Type": 	"mosyr.overrides.hr.CustomExpenseClaimType",
	"Attendance Request": 	"mosyr.overrides.hr.CustomAttendanceRequest",
	
	"Loan Type": 			"mosyr.overrides.loans.CustomLoanType",
	"Loan": 				"mosyr.overrides.loans.CustomLoan",
	"Loan Disbursement": 	"mosyr.overrides.loans.CustomLoanDisbursement",
	"Loan Repayment": 		"mosyr.overrides.loans.CustomLoanRepayment",
	"Loan Write Off": 		"mosyr.overrides.loans.CustomLoanWriteOff",
	
	"Salary Component": 			"mosyr.overrides.payrolls.CustomSalaryComponent",
	"Salary Structure": 			"mosyr.overrides.payrolls.CustomSalaryStructure",
	"Salary Structure Assignment": 	"mosyr.overrides.payrolls.CustomSalaryStructureAssignment",
	"Salary Slip": 					"mosyr.overrides.payrolls.CustomSalarySlip",
	"Payroll Entry": 				"mosyr.overrides.payrolls.CustomPayrollEntry",

	"Shift Assignment": 			"mosyr.overrides.shifts.CustomShiftAssignment",
	"Shift Request": 				"mosyr.overrides.shifts.CustomShiftRequest",
	"Attendance": 					"mosyr.overrides.shifts.CustomAttendance",
	"Employee Checkin": 			"mosyr.overrides.shifts.CustomEmployeeCheckin",
	"Shift Type": 					"mosyr.overrides.shifts.CustomShiftType",

	"User Type": 					"mosyr.overrides.core.CustomUserType",
	"User": 					"mosyr.overrides.core.CustomUser",
	
	"Leave Application": 					"mosyr.overrides.hr.CustomLeaveApplication",
}

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
	"Employee": {
		"validate": [
			"mosyr.api.validate_social_insurance",
			"mosyr.api.notify_expired_dates",
			"mosyr.api.set_employee_gender",
			"mosyr.api.translate_employee",
			"mosyr.api.set_employee_number",
			"mosyr.api.set_date_of_joining",
			"mosyr.api.employee_end_contract"
	]},
	"Leave Type": {
		"validate": "mosyr.api.check_other_annual_leaves"
	},
	"User" :{
		"validate" : "mosyr.api.create_user_permission_on_company_in_validate",
		"after_insert" : [
			"mosyr.api.set_user_type",
			"mosyr.api.create_user_permission_on_company_in_create_user"
		]
	},
	"Loan Repayment" : {
		"validate" :[
			"mosyr.api.validate_remaining_loan"
		]
	},
	"User Type" :{
		"on_update" : "mosyr.api.update_user_type_limits"
	},
    "Salary Structure": {
		"validate" : "mosyr.api.create_componants_in_salary_straucture"
	},
    "Payroll Entry" : {
		"on_submit": "mosyr.api.sum_net_pay_payroll_entry"
	},
    "Company" : {
		"validate" : [
                        "mosyr.api.update_employee_data",
    					"mosyr.api.create_letter_head"
		]
	},
    "Department": {
		"validate": "mosyr.api.create_department_workflows"
	},
    "Leave Application": {
		"on_update": "mosyr.api.validate_approver"
	},
}

# Scheduled Tasks
# ---------------
scheduler_events = {
	"cron":{	
		"0/5 * * * *" :[
			"mosyr.tasks.process_auto_attendance_for_all_shifts"
		],
		"0 7 * * *": [
			"mosyr.tasks.check_expired_dates"
		]
	},
	"daily": [
		"mosyr.tasks.update_status_for_contracts",
		"mosyr.tasks.notify_expired_dates",
		"mosyr.tasks.employee_end_contract"
	],
	"daily_long": [
		"mosyr.mosyr.doctype.shift_builder.shift_builder.daily_shift_requests_creation"
	]
}
# scheduler_events = {
# 	"all": [
# 		"mosyr.tasks.all"
# 	],
# 	"daily": [
# 		"mosyr.tasks.daily"
# 	],
# 	"hourly": [
# 		"mosyr.tasks.hourly"
# 	],
# 	"weekly": [
# 		"mosyr.tasks.weekly"
# 	]
# 	"monthly": [
# 		"mosyr.tasks.monthly"
# 	]
# }

# Testing
# -------

# before_tests = "mosyr.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "mosyr.event.get_events"
# }
override_whitelisted_methods = {
	"frappe.utils.print_format.download_pdf": "mosyr.api.download_pdf"
}
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "mosyr.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]


# User Data Protection
# --------------------

user_data_fields = [
	{
		"doctype": "{doctype_1}",
		"filter_by": "{filter_by}",
		"redact_fields": ["{field_1}", "{field_2}"],
		"partial": 1,
	},
	{
		"doctype": "{doctype_2}",
		"filter_by": "{filter_by}",
		"partial": 1,
	},
	{
		"doctype": "{doctype_3}",
		"strict": False,
	},
	{
		"doctype": "{doctype_4}"
	}
]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"mosyr.auth.validate"
# ]

fixtures = [
    {
        "dt": "Custom Field",
        "filters": [
            ["name", "in", [
				"Employee-full_name_en",
				"Employee-from_api",
				"Employee-key",
				"Employee-valid_data",
				"Employee-hijri_date_of_birth",
				"Employee-employee_signature",
				"Employee-api_employee_status",
				"Employee-birth_place",
				"Employee-direct_manager",
				# "Employee-nationality",
				# "Employee-religion",
				"Employee-handicap",
				"Employee-self_service",
				"Employee-payroll_card_number",
				"Employee-insurance_card_expire",
				"Employee-insurance_card_class",
				"Employee-health_certificate",
				"Employee-employee_status",
				"Employee-passport",
				"Employee-employee_passport",
				"Employee-identity",
				"Employee-employee_identity",
				"Employee-dependent",
				"Employee-employee_dependent",
				"Employee-mosyr_employee_status",
				"Employee-moyser_employee_status",
				
				"Employee-social_insurance",
				"Employee-include_housing",
				"Employee-s_subscription_date",
				"Employee-s_insurance_no",
				"Employee-column_break_88",
				
				"Employee-social_insurance_type",
				"Employee-include_housing",
				"Employee-risk_on_company",
				"Employee-pension_on_company",
				"Employee-risk_on_employee",
				"Employee-pension_on_employee",
				"Employee-e_gender",

				"Employee Education-attachment",
				"Employee Education-qualification_location",
				"Employee Education-qualification_institute",
				"Employee Education-gpa_rate",
				"Employee Education-qualification_held_date",
				"Employee Education-qualification_attendance_date",
				"Employee Education-qualification_degree",
				"Employee Education-key",
				"Employee Education-column_break_7",

				"Employee External Work History-reason_of_termination",
				"Employee External Work History-end_date",
				"Employee External Work History-start_date",
				"Employee External Work History-notes",
				"Employee External Work History-certificate_experience",
				"Employee External Work History-key",
				"Employee External Work History-column_break_7",
				
				"Employee-notify_id",
				"Employee-notify_passport",
				"Employee-notify_insurance_d",
				"Employee-notify_insurance_e",

				"Leave Application-key",
				"Leave Application-leave_attachments",

				"Additional Salary-reason",
				"Additional Salary-employee_benefit",
				"Employee-departement_location",

				"Leave Type-is_annual_leave",

				"Shift Assignment-lateness_permission",
				"Shift Type-in_lateness_permission",
				"Shift Request-lateness_permission",
				"Additional Salary-employee_deduction",
				"Employee-employee_bank",
				"Employee-number",
				"Employee-custom_date_of_joining",
				"Loan-total_amount_remaining",
				"Repayment Schedule-paid_amount",

				"Attendance-mosyr_employee_multiselect",
				"Shift Type-max_working_hours",
				"Email Template-use_for_welcome_email",

				"Payroll Entry-branches",
				"Payroll Entry-departments",
				"Payroll Entry-designations",
                
				"Payroll Employee Detail-leaves",
                "Payroll Employee Detail-total_leaves_taken",
                "Payroll Employee Detail-deduct_from_salary",
                "Payroll Employee Detail-column_break_8",
                "Payroll Employee Detail-deduction_days",
                "Payroll Employee Detail-deduction_per_day",
                "Salary Detail-is_leave_deduction",
                "Employee-payment_type_2",
                "Payroll Entry-total_amount",
                "Payroll Entry-total_netpay",
                "Company-pension_percentage_on_company",
                "Company-column_break_0gjgh",
                "Company-pension_percentage_on_employee",
                "Company-column_break_h1hb6",
                "Company-risk_percentage_on_company",
                "Company-column_break_z45y7",
                "Company-risk_percentage_on_employee",
                "Company-social_insurance_settings",
                "Company-banks_type_salary_card",
                "Company-bank_account_number",
                "Company-column_break_endoh",
                "Company-banks_type_payroll",
                "Company-calendar_accreditation",
                "Company-column_break_xxoi2",
                "Company-bank_code",
                "Company-month_days",
                "Company-column_break_homhp",
                "Company-english_name_in_bank",
                "Company-bank_name",
                "Company-disbursement_type",
                "Company-payroll_and_financial_settings",
                "Company-right_header",
                "Company-column_break_baa2t",
                "Company-left_header",
                "Company-header",
                "Company-baladiya_license",
                "Company-column_break_piicu",
                "Company-cr_document",
                "Company-column_break_mdtj1",
                "Company-stamp",
                "Company-column_break_8kblg",
                "Company-logo",
                "Company-logos_brands",
                "Company-signatures",
                "Company-signature",
                "Company-labors_office_file_number",
                "Company-mail_sender_address",
                "Company-column_break_gsref",
                "Company-mobile",
                "Company-_mail_sender_name",
                "Company-column_break_4zb38",
                "Company-sender_name_sms",
                "Company-organization_english",
                "Company-column_break_obynz",
                "Company-organization_arabic",
                "Company-company_id",
                "Company-account_info",
                "Company-company_name_in_arabic",
                "Company-establishment_number",
                "Company-agreement_symbol",
                "Company-agreement_number_for_customer",
                "Company-unaccounted_deductions",
                "Company-employee_day_wedding_leave",
                "Company-end_of_services",
                "Company-employee_day_death_leave",
				"Company-employee_day_benefits_with_out_pay_leave",
                "Company-column_break_xltde",
                "Company-employee_day_sick_leave",
                "Company-employee_day_urgent_leave",
                "Company-employee_day_hajj_leave",
                "Company-employee_day_childbirth_vacation",
                "Company-employee_day_annual_vacation",
                "Company-employee_day_working",
                "Company-settings",
                
                "Holiday List-add_time_period_holidays",
                "Holiday List-period_description",
                "Holiday List-start_from",
                "Holiday List-ends_on",
                "Holiday List-add_period_holidays",
                "Holiday List-column_break_c8bxj",

                "Salary Component-custom_formula",

                "Department-contact_details_approver",
                "Department-educational_qualification_approver",
                "Department-emergency_contact_approver",
                "Department-health_insurance_approver",
                "Department-personal_details_approver",
                "Department-salary_details_approver",
                "Department-exit_permission_approver",
                "Department-attendance_request_approver",
                "Department-compensatory_leave_request_approver",
                "Department-travel_request_approver",
                
                "Workflow Document State-related_to",
                "Workflow Transition-related_to",
                "Workflow Document State-approver",
                "Vehicle Service-attachment",
                "Vehicle Service-details",
                "Department-vehicle_service_approver"
         ]]
        ]
    },
	{
	"dt": "Property Setter",
			"filters": [
				["name", "in", [
					"Employee-employee_name-hidden",
					"Employee-last_name-hidden",
					"Employee-middle_name-hidden",
					"Employee-first_name-label",
					"Employee-erpnext_user-label",
					"Employee-company-in_standard_filter",
					"Employee-gender-hidden",
					"Employee-gender-default",
					"Employee-bank_name-hidden",
					"Employee-employee_number-hidden",
					"Employee-job_applicant-hidden",
					"Employee-scheduled_confirmation_date-hidden",
					"Employee-notice_number_of_days-hidden",
					"Employee-date_of_retirement-hidden",
					"Employee-date_of_joining-default",
					"Employee-date_of_joining-hidden",
					"Loan-applicant_type-default",
					"Loan-applicant_type-read_only",
					"Loan-rate_of_interest-default",
					"Loan-main-title_field",
					"Loan-total_payment-in_list_view",
					"Loan-loan_type-in_list_view",
					"Loan-total_amount_paid-in_list_view",
					"Loan-total_interest_payable-hidden",
					"Loan Type-disabled-hidden",
					"Loan Type-is_term_loan-hidden",
					"Loan Type-grace_period_in_days-hidden",
					"Loan-posting_date-in_list_view",
					"Loan Application-applicant_type-default",
					"Loan Application-applicant_type-read_only",
					"Repayment Schedule-is_accrued-hidden",
					"Repayment Schedule-balance_loan_amount-hidden",
					"Loan Type-is_term_loan-default",
					# Hide from Printing!
					"Salary Detail-tax_on_additional_salary-print_hide",
					"Salary Detail-tax_on_flexible_benefit-print_hide",
					"Salary Slip-base_gross_pay-print_hide",
					"Salary Slip-total_loan_repayment-print_hide",
					"Salary Slip-leave_details-print_hide",
					"Salary Slip-base_total_in_words-print_hide",
					"Salary Slip-total_in_words-print_hide",
					"Salary Slip-base_month_to_date-print_hide",
					"Salary Slip-month_to_date-print_hide",
					"Salary Slip-base_rounded_total-print_hide",
					"Salary Slip-base_year_to_date-print_hide",
					"Salary Slip-base_net_pay-print_hide",
					"Salary Slip-total_interest_amount-print_hide",
					"Salary Slip-total_principal_amount-print_hide",
					"Salary Slip-base_total_deduction-print_hide",
					"Salary Slip-total_deduction-print_hide_if_no_value",
					"Salary Slip-base_gross_year_to_date-print_hide",
					"Salary Slip-payroll_cost_center-print_hide",
					"Payroll Entry-payroll_payable_account-print_hide",
					"Payroll Entry-payment_account-print_hide",
					"Payroll Entry-bank_account-print_hide",
					"Payroll Entry-salary_slips_created-print_hide",
					"Payroll Entry-salary_slips_submitted-print_hide",
                    "Payroll Entry-cost_center-print_hide",
					"Payroll Entry-main-default_print_format",
                    "Payroll Entry-designation-hidden",
                    "Payroll Entry-department-hidden",
                    "Payroll Entry-branch-hidden",
                    "User Permission Document Type-document_type-read_only",
                    "User Permission Document Type-read-default",
                    "Loan Application-is_term_loan-default",
                    "Loan Application-is_secured_loan-hidden",
                    "Loan Application-is_term_loan-hidden",
                    "Loan-is_secured_loan-hidden",
                    "Loan-is_term_loan-default",
                    "Loan-is_term_loan-hidden",
                    "Employee Incentive-employee_name-in_list_view",
                    "Employee Incentive-employee-in_list_view",
                    "Employee Incentive-payroll_date-in_list_view",
                    "Employee Incentive-incentive_amount-in_list_view",
                    "Retention Bonus-employee-in_list_view",
                    "Retention Bonus-employee_name-in_list_view",
                    "Retention Bonus-bonus_payment_date-in_list_view",
                    "Retention Bonus-bonus_amount-in_list_view",
                    "Salary Slip-net_pay-in_list_view",
                    "Salary Slip-employee-in_list_view",
                    "Salary Slip-salary_structure-in_list_view",
                    "Salary Slip-payroll_frequency-default",
                    "Salary Slip-payroll_frequency-hidden",
                    "Payroll Entry-branch-in_list_view",
                    "Payroll Entry-posting_date-in_list_view",
                    "Payroll Entry-currency-in_list_view",
                    "Payroll Entry-payroll_frequency-hidden",
                    "Payroll Entry-payroll_frequency-default",
                    "Salary Slip Loan-interest_amount-hidden",
                    "Salary Slip Loan-interest_income_account-hidden",
                    "Salary Slip Loan-loan_account-hidden",
                    "Salary Slip-total_interest_amount-hidden",
                    "Company-section_break_28-hidden",
                    "Company-registration_info-hidden",
                    "Company-default_letter_head-hidden",
                    "Repayment Schedule-interest_amount-hidden",
                    "Payroll Entry-main-title_field",
                    "Retention Bonus-main-title_field",
                    "Leave Type-allow_over_allocation-hidden",
                    "Leave Type-earned_leave-hidden",
                    "Employee-grade-hidden",
                    "Employee-personal_details-hidden",
                    "Employee-unsubscribed-hidden",
                    "Employee-prefered_contact_email-hidden",
                    "Employee-job_profile-label",
                    "Salary Component-formula-hidden",
                    "Salary Component-help-hidden",
                    "Vehicle Log-service_detail-allow_on_submit",
                    "Vehicle Service-type-reqd",
                    "Vehicle Service-frequency-reqd",
                    "Vehicle Service-expense_amount-reqd"
				]
			]
		]
	},
	{
	"dt": "Workflow",
	"filters": 
		[
			["name", "in", 
				[
					"Employee Contract",
					"Personal Details",
					"Health Insurance",
					"Salary Details",
					"Educational Qualification",
					"Emergency Contact",
					"Contact Details",
					"Dependants Details",
					"Passport Details",
					"Work Experience",
					"Lateness Permission",
					"Employee ID",
                    "Exit Permission"
				]
			]
		]
	},
	{
	"dt": "Workflow State",
	"filters": 
		[
			["name", "in", 
				[
					"Draft",
					"Approved And Applied",
					"Approved And Not Applied",
					"Cancelled",
					"Approved by HR",
					"Ended"
				]
			]
		]
	},
	{
	"dt": "Workflow Action Master",
	"filters": 
		[
			["name", "in", 
				[
					"Approve No Apply", "Cancel"
				]
			]
		]
	},
	{
	"dt": "Role",
	"filters": 
		[
			["name", "in", 
				[
					"HR Notification"
				]
			]
		]
	},
	{
	"dt": "Print Format",
	"filters": 
		[
			["name", "in", 
				[
					"Data Import Log",
                    			"Standard Printing for Payroll",
				]
			]
		]
	},
	{
	"dt": "Module Def",
	"filters": 
		[
			["name", "in", 
				[
					"Mosyr Forms"
				]
			]
		]
	},
    {
	"dt": "Nationality",
	"filters": []
	},
    {
	"dt": "Salary Component",
	"filters": 
    	[
			["name", "in", 
				[
					"Company Pension Insurance",
					"Employee Pension Insurance",
                    "Risk On Company",
                    "Risk On Employee"
				]
			]
		]
	},
]
