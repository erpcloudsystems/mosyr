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
	}
doctype_list_js = {"Loan" : "public/js/loan_list.js"}
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
	]},
	"Leave Type": {
		"validate": "mosyr.api.check_other_annual_leaves"
	},
	"User" :{
		"after_insert" : "mosyr.api.set_user_type"
	},
	"Loan Repayment" : {
		"validate" :[
			"mosyr.api.validate_remaining_loan"
		]
	},
	"User Type" :{
		"on_update" : "mosyr.api.update_user_type_limits"
	},
}

# Scheduled Tasks
# ---------------
scheduler_events = {
	"cron":{	
		"0/1 * * * *" :[
			"mosyr.cron.process_auto_attendance_for_all_shifts"
		]
	},
	"daily": [
		"mosyr.daily.update_status_for_contracts",
		"mosyr.daily.notify_expired_dates",
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
				"Employee-nationality",
				"Employee-payment_type",
				"Employee-religion",
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
					# "Loan-rate_of_interest-hidden",
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
					"Loan Type-is_term_loan-default",
					"Repayment Schedule-interest_amount-hidden"
					"Loan Type-is_term_loan-default",
					"Repayment Schedule-balance_loan_amount-hidden",
                    
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
				]]
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
					"Employee ID"
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
					"Data Import Log"
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
]
