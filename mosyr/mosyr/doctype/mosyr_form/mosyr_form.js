// Copyright (c) 2022, AnvilERP and contributors
// For license information, please see license.txt

frappe.ui.form.on('Mosyr Form', {
	refresh: function (frm) {
		frm.set_query('role', 'permissions', function (doc) {
			if (doc.custom && frappe.session.user != 'Administrator') {
				return {
					query: "frappe.core.doctype.role.role.role_query",
					filters: [['Role', 'name', '!=', 'All']]
				};
			}
		});
		if (frm.is_new()) {
			if (!(frm.doc.permissions && frm.doc.permissions.length)) {
				frm.add_child('permissions', { role: 'System Manager' });
			}
		} else {
			frm.toggle_enable("engine", 0);
		}
	},
	autoname: function (frm) {
		frm.set_df_property('fields', 'reqd', frm.doc.autoname !== 'Prompt');
	}
});
