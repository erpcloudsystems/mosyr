// Copyright (c) 2022, AnvilERP and contributors
// For license information, please see license.txt

frappe.ui.form.on('Users Permission Manager', {
	refresh: function(frm){
		frm.set_query( 'document_type', "permissions", function(doc) {
			return {
				query: "mosyr.api.get_doctypes",

			};
		});
	},
	setup: function(frm) {
		frm.disable_save()
	},
	user:function(frm){
		frm.clear_table('permissions')
		frm.refresh_field('permissions')
		if(frm.doc.user){
			frappe.call({
				doc:frm.doc,
				method: "get_permissions",
				freeze: true,
				args:{user: frm.doc.user},
				callback: function(r){
					(r.message || []).forEach(row => {
						let new_row = frm.add_child("permissions", row)
					});
					frm.refresh_field('permissions');
				}
			})

			frm.add_custom_button("Apply Permissions", ()=>{
				frappe.call({
					doc:frm.doc,
					method: "apply_permissions",
					freeze: true,
					args:{user: frm.doc.user, perms: frm.doc.permissions},
					callback: function(r){
						(r.message || []).forEach(row => {
							let new_row = frm.add_child("permissions", row)
						});
						frm.refresh_field('permissions');
					}
				});
			}).addClass("btn btn-primary")
		}else{
			frm.clear_custom_buttons()
		}
	}
});
