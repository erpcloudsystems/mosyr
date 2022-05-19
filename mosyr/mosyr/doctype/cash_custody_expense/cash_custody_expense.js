// Copyright (c) 2022, AnvilERP and contributors
// For license information, please see license.txt

frappe.ui.form.on('Cash Custody Expense', {
	refresh: function(frm) {
		frm.fields_dict.cash_custody.get_query = function(frm) {
			return {
				filters: [
					["estimated_value", ">", 0]
				]
			}
		}
	}
});
