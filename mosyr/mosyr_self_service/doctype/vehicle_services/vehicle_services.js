// Copyright (c) 2023, AnvilERP and contributors
// For license information, please see license.txt

frappe.ui.form.on('Vehicle Services', {
	// refresh: function(frm) {

	// }
	service_item: function(frm) {
		if (frm.doc.service_item == 'Accident'){
			frm.doc.expense = 0
			frm.refresh_field('expense')
		}
	}
});
