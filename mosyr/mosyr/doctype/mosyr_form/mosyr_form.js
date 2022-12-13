// Copyright (c) 2022, AnvilERP and contributors
// For license information, please see license.txt

frappe.ui.form.on('Mosyr Form', {
	onload: function(frm){
		if (frm.is_new()) {
			if (!(frm.doc.permissions && frm.doc.permissions.length)) {
				frm.add_child('permissions', { role: 'System Manager' });
			}
		}
	},
	refresh: function (frm) {
		frm.set_query('role', 'permissions', function (doc) {
			if (doc.custom && frappe.session.user != 'Administrator') {
				return {
					query: "frappe.core.doctype.role.role.role_query",
					filters: [['Role', 'name', '!=', 'All']]
				};
			}
		});
		frm.set_query( 'role', "permissions", function(doc) {
			return {
				query: "mosyr.api.get_roles",
			};
		});
		if (frm.is_new()) {
			if (!(frm.doc.permissions && frm.doc.permissions.length)) {
				frm.add_child('permissions', { role: 'System Manager' });
			}
		}
	},
	autoname: function (frm) {
		frm.set_df_property('fields', 'reqd', frm.doc.autoname !== 'Prompt');
	}
});
