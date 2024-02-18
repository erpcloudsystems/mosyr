// Copyright (c) 2024, AnvilERP and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Loan Details"] = {
	"filters": [
		{
			fieldname: "from_date",
			label: __("From Date"),
			fieldtype: "Date",
			reqd: 1,
			default: frappe.datetime.add_months(frappe.datetime.get_today(), -1)
		},
		{
			fieldname: "to_date",
			label: __("To Date"),
			fieldtype: "Date",
			reqd: 1,
			default: frappe.datetime.get_today()
		},
		{
			"fieldname":"company",
			"label": __("Company"),
			"fieldtype": "Link",
			"options": "Company",
			"reqd": 1,
			"default": frappe.defaults.get_user_default("Company")
		},
		{
			"fieldname":"applicant_type",
			"label": __("Applicant Type"),
			"fieldtype": "Select",
			"options": ["Employee"],
			"reqd": 1,
			"default": "Employee",
			on_change: function() {
				frappe.query_report.set_filter_value('applicant', "");
			}
		},
		{
			"fieldname": "applicant",
			"label": __("Applicant"),
			"fieldtype": "Dynamic Link",
			"get_options": function() {
				var applicant_type = frappe.query_report.get_filter_value('applicant_type');
				var applicant = frappe.query_report.get_filter_value('applicant');
				if(applicant && !applicant_type) {
					frappe.throw(__("Please select Applicant Type first"));
				}
				return applicant_type;
			}

		},
	]
};
