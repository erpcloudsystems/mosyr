// Copyright (c) 2023, AnvilERP and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Exit Permissions Summary"] = {
	"filters": [
		{
			"fieldname":"from",
			"label": __("From"),
			"fieldtype": "Date",
			"default": frappe.datetime.month_start(),
			"reqd": 1,
			"width": "100px"
		},
		{
			"fieldname":"to",
			"label": __("To"),
			"fieldtype": "Date",
			"default": frappe.datetime.month_end(),
			"reqd": 1,
			"width": "100px"
		},
		{
			"fieldname":"employee",
			"label": __("Employee"),
			"fieldtype": "Link",
			"options": "Employee",
			"width": "100px"
		},
		{
			"fieldname":"workflow_state",
			"label": __("Status"),
			"fieldtype": "Select",
			"options": ["", "Approved By HR","Pending","Rejected"],
			"default": "",
			"width": "100px",
		},
		{
			"fieldname":"company",
			"label": __("Company"),
			"fieldtype": "Link",
			"options": "Company",
			"default": frappe.defaults.get_user_default("Company"),
			"width": "100px",
			"reqd": 1
		}
	]
};
