// Copyright (c) 2022, AnvilERP and contributors
// For license information, please see license.txt

frappe.ui.form.on('Users Permission Manager', {
	refresh: function(frm){
		frm.disable_save()
		frm.set_query( 'document_type', "permissions", function(doc) {
			return {
				query: "mosyr.api.get_doctypes",

			};
		});
		frm.clear_table('permissions')
		frm.clear_table('page_or_report')
		frm.set_value('user', '')

		frm.refresh_field('permissions')
		frm.refresh_field('page_or_report')
		frm.refresh_field('user')
	},
	// setup: function(frm) {
	// 	frm.disable_save()
	// },
	user:function(frm){
		frm.clear_table('permissions')
		frm.refresh_field('permissions')

		frm.clear_table('page_or_report')
		frm.refresh_field('page_or_report')

		if(frm.doc.user){
			frappe.call({
				doc:frm.doc,
				method: "get_permissions",
				freeze: true,
				args:{user: frm.doc.user},
				callback: function(r){
					(r.message.docs || []).forEach(row => {
						let new_row = frm.add_child("permissions", row)
					});
					frm.refresh_field('permissions');

					(r.message.repage || []).forEach(row => {
						if(row.page){
							let new_row = frm.add_child("page_or_report", {
								'set_role_for': 'Page',
								'page_or_report': row.page
							})
						}else if(row.report){
							let new_row = frm.add_child("page_or_report", {
								'set_role_for':'Report',
								'page_or_report': row.report
							})
						}
						
					});
					frm.refresh_field('page_or_report');
				}
			})

			frm.add_custom_button("Apply Permissions", ()=>{
				frappe.call({
					doc:frm.doc,
					method: "apply_permissions",
					freeze: true,
					args:{user: frm.doc.user, perms: frm.doc.permissions, rps: frm.doc.page_or_report},
					callback: function(r){
						if(r.message) {
							console.log(r.message);
							(r.message || []).forEach(row => {
								let new_row = frm.add_child("permissions", row)
							});
							frm.refresh_field('permissions');
						}
					}
				});
			}).addClass("btn btn-primary")

			
			frm.add_custom_button("Copy From", ()=>{
				let d = new frappe.ui.Dialog({
					title: 'Choose User',
					fields: [
						{
							label: 'User',
							fieldname: 'user',
							fieldtype: 'Link',
							options : "User"
						}
					],
					primary_action_label: 'Get Permissions',
					primary_action(values) {
						frm.clear_table('permissions')
						frm.clear_table('page_or_report')
						frappe.call({
							doc:frm.doc,
							method: "get_permissions",
							freeze: true,
							args:{user: values.user},
							callback: function(r){
								if(r.message){
									(r.message.docs || []).forEach(row => {
										let new_row = frm.add_child("permissions", row)
									});
									
									frm.refresh_field('permissions');
									
									(r.message.repage || []).forEach(row => {
										if(row.page){
											let new_row = frm.add_child("page_or_report", {
												'set_role_for': 'Page',
												'page_or_report': row.page
											})
										}else if(row.report){
											let new_row = frm.add_child("page_or_report", {
												'set_role_for':'Report',
												'page_or_report': row.report
											})
										}
										
									});
									frm.refresh_field('page_or_report');
								}							
							}	
						})
						d.hide();
					}
				});
				
				d.show();


			}).addClass("btn btn-primary")
		}else{
			frm.clear_custom_buttons()
		}
	}
});