// Copyright (c) 2023, AnvilERP and contributors
// For license information, please see license.txt

frappe.ui.form.on('Vehicle Services', {
	refresh: function(frm) {
		frm.set_query('vehicle_log', function() {
			return {
				query: "mosyr.mosyr_self_service.doctype.vehicle_services.vehicle_services.fetch_vehicle_log",
			}
		})
	},
	service_item: function(frm) {
		if (frm.doc.service_item == 'Accident'){
			frm.doc.expense = 0
			frm.refresh_field('expense')
		}
	}
});
