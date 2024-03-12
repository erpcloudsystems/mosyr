// Copyright (c) 2024, AnvilERP and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Employee Leaves Balances"] = {
	filters: [
		{
			fieldname: "from_date",
			label: __("From Date"),
			fieldtype: "Date",
			reqd: 1,
			default: frappe.defaults.get_default("year_start_date")
		},
		{
			fieldname: "to_date",
			label: __("To Date"),
			fieldtype: "Date",
			reqd: 1,
			default: frappe.defaults.get_default("year_end_date")
		},
		{
			label: __("Company"),
			fieldname: "company",
			fieldtype: "Link",
			options: "Company",
			reqd: 1,
			default: frappe.defaults.get_user_default("Company")
		},
		{
			fieldname: "department",
			label: __("Department"),
			fieldtype: "Link",
			options: "Department",
		},
		{
			fieldname: "employee",
			label: __("Employee"),
			fieldtype: "Link",
			options: "Employee",
		},
		{
			fieldname: "employee_status",
			label: __("Employee Status"),
			fieldtype: "Select",
			options: [
				"",
				{ "value": "Active", "label": __("Active") },
				{ "value": "Inactive", "label": __("Inactive") },
				{ "value": "Suspended", "label": __("Suspended") },
				{ "value": "Left", "label": __("Left") },
			],
			default: "Active",
		},
		{
			fieldname: "consolidate_leave_types",
			label: __("Consolidate Leave Types"),
			fieldtype: "Check",
			default: 1,
			depends_on: "eval: !doc.employee",
		}
	],

	onload: () => {
		frappe.call({
			type: "GET",
			method: "erpnext.hr.utils.get_leave_period",
			args: {
				"from_date": frappe.defaults.get_default("year_start_date"),
				"to_date": frappe.defaults.get_default("year_end_date"),
				"company": frappe.defaults.get_user_default("Company")
			},
			freeze: true,
			callback: (data) => {
				frappe.query_report.set_filter_value("from_date", data.message[0].from_date);
				frappe.query_report.set_filter_value("to_date", data.message[0].to_date);
			}
		});
	}
};
