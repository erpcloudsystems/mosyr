// Copyright (c) 2023, AnvilERP and contributors
// For license information, please see license.txt

frappe.ui.form.on('Exit Permission', {
	refresh: function(frm) {
		frm.set_query("employee", function() {
			return {
                "filters": {
                    "company": frm.doc.company
                }
            }
		})
	},
});
