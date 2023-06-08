// Copyright (c) 2022, AnvilERP and contributors
// For license information, please see license.txt

frappe.ui.form.on('Mosyr Form', {
	onload: function (frm) {
		if (frm.is_new()) {
			if (!(frm.doc.permissions && frm.doc.permissions.length)) {
				frm.add_child('permissions', { role: 'System Manager' });
			}
		}
	},
	refresh: function (frm) {
		let roles = ["Saas Manager", "Self Service", "SaaS User"]
		frm.set_query("allowed","workflow_transition", function(doc) {
			return {
				filters: {
					name: ["in", roles],
				}
			};
		});
		if (!frm.is_new() && !frm.doc.istable && frm.doc.docstatus == 1) {
			frm.add_custom_button(__('Go to {0} List', [frm.doc.form_title]), () => {
				window.open(`/app/${frappe.router.slug(frm.doc.name)}`);
			});
		}
		frm.set_query('role', 'permissions', function (doc) {
			if (doc.custom && frappe.session.user != 'Administrator') {
				return {
					query: "frappe.core.doctype.role.role.role_query",
					filters: [['Role', 'name', '!=', 'All']]
				};
			}
		});
		frm.set_query('role', "permissions", function (doc) {
			return {
				query: "mosyr.api.get_roles",
			};
		});
		// if (frm.is_new()) {
		// 	if (!(frm.doc.permissions && frm.doc.permissions.length)) {
		// 		frm.add_child('permissions', { role: 'System Manager' });
		// 	}
		// }
	},
	autoname: function (frm) {
		frm.set_df_property('fields', 'reqd', frm.doc.autoname !== 'Prompt');
	}
});