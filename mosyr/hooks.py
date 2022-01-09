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
# app_include_css = "/assets/mosyr/css/mosyr.css"
# app_include_js = "/assets/mosyr/js/mosyr.js"

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
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
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
# after_install = "mosyr.install.after_install"

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

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
#	}
# }

# Scheduled Tasks
# ---------------

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
				"Company-company_name_in_arabic",

				"Address-address_in_arabic",

				"Sales Invoice-qr_code",

				"Payment Entry-customer_gstin",
				"Payment Entry-customer_address",
				"Payment Entry-place_of_supply",
				"Payment Entry-company_gstin",
				"Payment Entry-company_address",
				"Payment Entry-gst_section",

				"Branch-location",

				"Loan Application-workflow_state",
				
				"Leave Application-workflow_state",

				"Employee-handicap",
				"Employee-birth_place",
				"Employee-nationality",
				"Employee-birth_date_hijri",
				"Employee-full_name_en",
				"Employee-payment_type",
				"Employee-self_service",
				"Employee-nid",
				"Employee-from_api",
				"Employee-valid_data",
				"Employee-from_api",
				"Employee-direct_manager",
				"Employee-moyser_employee_status"
				"Employee-branch_working_place",
				"Employee-health_certificate",
				"Employee-payroll_card_number",
				"Employee-insurance_card_expire",
				"Employee-insurance_card_class",
				"Employee-employee_class",


            ]]
        ]
    },
	{
		"dt": "Workflow State",
		"filters": [
            ["name", "in", [
				"Open", "Cancelled", "First Approved", "First Approval", "Last Approval",
				"Approved by HR User", "Approved by HR Manager", "Rejected by HR User"
            ]]
        ]
	},
	{
		"dt": "Workflow Action Master",
		"filters": [
            ["name", "in", [
				"Cancel"
            ]]
        ]
	},
	{
        "dt": "Workflow",
        "filters": [
            ["name", "in", [
				"Loan Approval", "Leave Approval"
            ]]
        ]
    }
]


