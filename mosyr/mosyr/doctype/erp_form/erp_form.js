// Copyright (c) 2022, AnvilERP and contributors
// For license information, please see license.txt

frappe.ui.form.on('ERP Form', {
	refresh: function (frm) {
		frm.set_query('role', 'permissions', function (doc) {
			if (doc.custom && frappe.session.user != 'Administrator') {
				return {
					query: "frappe.core.doctype.role.role.role_query",
					filters: [['Role', 'name', '!=', 'All']]
				};
			}
		});
		if (!frm.is_new() && !frm.doc.istable) {
			if (frm.doc.issingle) {
				frm.add_custom_button(__('Go to {0}', [__(frm.doc.name)]), () => {
					window.open(`/app/${frappe.router.slug(frm.doc.name)}`);
				});
			} else {
				frm.add_custom_button(__('Go to {0} List', [__(frm.doc.name)]), () => {
					window.open(`/app/${frappe.router.slug(frm.doc.name)}`);
				});
			}
		}
		if (frm.is_new()) {
			if (!(frm.doc.permissions && frm.doc.permissions.length)) {
				frm.add_child('permissions', { role: 'System Manager' });
			}
		} else {
			frm.toggle_enable("engine", 0);
		}
		// set label for "In List View" for child tables
		frm.get_docfield('fields', 'in_list_view').label = frm.doc.istable ?
			__('In Grid View') : __('In List View');
		frm.events.autoname(frm);
	},
	autoname: function (frm) {
		frm.set_df_property('fields', 'reqd', frm.doc.autoname !== 'Prompt');
	}
});
