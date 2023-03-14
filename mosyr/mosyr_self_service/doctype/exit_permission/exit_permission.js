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
	employee: function(frm) {
		if(frm.doc.employee){
			frappe.call({
				doc:frm.doc,
				method:"get_employee_shift",
				args: {
					employee: frm.doc.employee
				},
				callback: function (r) {
					if (r.message) {
						frm.doc.shift = r.message
						frm.refresh_field('shift')
					}
				}
			})
		}
	}
});
