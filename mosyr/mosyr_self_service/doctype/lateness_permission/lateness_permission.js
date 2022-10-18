// Copyright (c) 2022, AnvilERP and contributors
// For license information, please see license.txt

frappe.ui.form.on('Lateness Permission', {
    refresh: function (frm) {
        frm.set_query('shift_type', function(doc) {
			return {
				filters: {
					"in_lateness_permission": 1,
				}
			};
		});
    },
});
