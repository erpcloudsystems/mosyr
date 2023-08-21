// Copyright (c) 2023, AnvilERP and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Employees Attendance"] = {
	"filters": [
		{
			"fieldname": "employee",
            "label": __("Employee"),
            "fieldtype": "Link",
            "options": "Employee",
            get_query: () => {
                return {
                    filters: {
                        "company": frappe.defaults.get_user_default("Company")
                    }
                };
            }
		},
		{
            "fieldname": "from_date",
            "label": __("From"),
            "fieldtype": "Date",
            "default": frappe.datetime.get_today(),
            "reqd": 1
        },
        {
            "fieldname": "to_date",
            "label": __("To"),
            "fieldtype": "Date",
            "default": frappe.datetime.get_today(),
            "reqd": 1
        },
		{
            "fieldname": "company",
            "label": __("Company"),
            "fieldtype": "Link",
            "options": "Company",
            "default": frappe.defaults.get_user_default("Company"),
            "reqd": 1
        }
	]
};
