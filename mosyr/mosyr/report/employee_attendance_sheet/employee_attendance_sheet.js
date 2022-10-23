// Copyright (c) 2022, AnvilERP and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Employee Attendance Sheet"] = {
	"filters": [
		{
			"fieldname":"from",
			"label": __("From"),
			"fieldtype": "Date",
			"default" : frappe.datetime.get_today()
		},
		{
			"fieldname":"to",
			"label": __("To"),
			"fieldtype": "Date",
			"default" : frappe.datetime.get_today()
		},
		{
			"fieldname":"employee",
			"label": __("Employee"),
			"fieldtype": "Link",
			"options": "Employee",
			get_query: () => {
				var company = frappe.query_report.get_filter_value('company');
				return {
					filters: {
						'company': company,
						'status':"Active"
					}
				};
			}
		},
		{
			"fieldname":"company",
			"label": __("Company"),
			"fieldtype": "Link",
			"options": "Company",
			"default": frappe.defaults.get_user_default("Company"),
			"reqd": 1
		},
		{
			"fieldname":"department",
			"label": __("Department"),
			"fieldtype": "Link",
			"options": "Department",
			"reqd": 0
		},
		{
			"fieldname":"branch",
			"label": __("Branch"),
			"fieldtype": "Link",
			"options": "Branch",
			"reqd": 0
		},
		{
			"fieldname":"summarized_view",
			"label": __("Summarized View"),
			"fieldtype": "Check",
			"Default": 0,
		}
	],
};
