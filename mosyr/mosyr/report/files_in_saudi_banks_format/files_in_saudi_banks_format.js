// Copyright (c) 2022, AnvilERP and contributors
// For license information, please see license.txt
/* eslint-disable */

let d = new Date();
let monthNames=  [
	'January',
	'February',
	'March',
	'April',
	'May',
	'June',
	'July',
	'August',
	'September',
	'October',
	'November',
	'December'
]
frappe.query_reports["Files in Saudi banks format"] = {
	"filters": [
		{
			"fieldname": "bank",
			"label": __("Bank"),
			"fieldtype": "Link",
			"width": "80",
			"options": "Bank",
		},
		{
			"fieldname": "month",
			"label": __("Month"),
			"fieldtype": "Select",
			"width": "80",
			'options': [
                '',
				'January',
				'February',
				'March',
				'April',
				'May',
				'June',
				'July',
				'August',
				'September',
				'October',
				'November',
				'December'
            ],
			'default': monthNames[d.getMonth()]
		},
		{
			"fieldname": "company",
			"label": __("Company"),
			"fieldtype": "Link",
			"width": "80",
			"options": "Company",
			'default': frappe.defaults.get_user_default("Company")
		},
	]
};
