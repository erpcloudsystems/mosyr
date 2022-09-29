// Copyright (c) 2022, AnvilERP and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Cash Custody Expenses"] = {
	"filters": [
		{
			"label": __("Custody Cash"),
			"fieldname": "custody",
			"fieldtype": "Link",
			"options": "Cash Custody"
		},
		{
			"label": __("Responsible Employee"),
			"fieldname": "res_employee",
			"fieldtype": "Link",
			"options": "Employee"
		},
		{
			"label": __("Branch"),
			"fieldname": "branch",
			"fieldtype": "Link",
			"options": "Branch"
		},
		{
			"label": __("Recipient Employee"),
			"fieldname": "rec_employee",
			"fieldtype": "Link",
			"options": "Employee"
		},
		{
			"label": __("From"),
			"fieldname": "from",
			"fieldtype": "Date",
			"default": frappe.datetime.get_today()
		},
		{
			"label": __("To"),
			"fieldname": "to",
			"fieldtype": "Date",
			"default": frappe.datetime.add_months(frappe.datetime.get_today(), 1)
		},
		{
			"label": __("Status"),
			"fieldname": "status",
			"fieldtype": "Select",
			"options": " \nUnSpent\nPartially Spent\nFully Spent"
		}
	]
};
