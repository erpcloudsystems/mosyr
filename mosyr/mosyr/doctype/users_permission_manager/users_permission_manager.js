// Copyright (c) 2022, AnvilERP and contributors
// For license information, please see license.txt

frappe.ui.form.on('Users Permission Manager', {
	refresh: function(frm){
		frm.disable_save()
		frm.set_query( 'user', function(doc) {
			return {
				query: "mosyr.api.get_users",

			};
		});
		frm.clear_table('page_or_report')
		frm.set_value('user', '')

		frm.refresh_field('page_or_report')
		frm.refresh_field('user')
	},

	user:function(frm){
		frm.clear_table('page_or_report')
		frm.refresh_field('page_or_report')

		if(frm.doc.user){
			frappe.call({
				doc:frm.doc,
				method: "get_permissions",
				freeze: true,
				args:{user: frm.doc.user},
				callback: function(r){
					if (r.message) {
						for (const [key, value] of Object.entries(r.message.doctypes)) {
							for (const [key2, value2] of Object.entries(value)) {
								frm.clear_table(key2)
								value2.forEach(e => {
									const new_row = frm.add_child(key2)
									new_row.document_type = e
									frm.refresh_field(key2)

								})
							}
						}
						
						for (const [key, value] of Object.entries(r.message.permission[0])) {
							if(value.length > 0) {
								value.forEach(row => {
									getchildren("User Permission Document Type", "Users Permission Manager", key).forEach(e => {
										if(e.document_type==row.document_type){
											e.is_custom =  row.is_custom,
											e.read =  row.read,
											e.write =  row.write,
											e.create =  row.create,
											e.submit =  row.submit,
											e.cancel =  row.cancel,
											e.amend =  row.amend,
											e.delete =  row.delete
										}
									}
									)
								})
							}
						}
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
					frm.refresh_fields()
				}
			})

			frm.add_custom_button("Apply Permissions", ()=>{
				frappe.call({
					doc:frm.doc,
					method: "apply_permissions",
					freeze: true,
					freeze_message: __("Please Wait..."), 
					args:{user: frm.doc.user,
						 perms:frm.doc.system_management.concat(
							frm.doc.user_management,
							frm.doc.hr_management,
							frm.doc.employees_list,
							frm.doc.self_service,
							frm.doc.e_form,
							frm.doc.timesheet_attendees_management,
							frm.doc.payroll,
							frm.doc.employees_performance,
							frm.doc.leave,
							frm.doc.loans,
							frm.doc.vehicle_management,
							frm.doc.documents_management,
							frm.doc.custody_management,
							),
						 rps: frm.doc.page_or_report},
					callback: function(r){
						if(r.message) {
							var msg = (__("Permission has been successfully released for user {0}", [frm.doc.user]));
							frappe.show_alert({message: msg, indicator:'green'});
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
						frappe.call({
							doc:frm.doc,
							method: "get_permissions",
							freeze: true,
							args:{user: values.user},
							callback: function(r){
								if (r.message) {
									for (const [key, value] of Object.entries(r.message.doctypes)) {
										for (const [key2, value2] of Object.entries(value)) {
											frm.clear_table(key2)
											value2.forEach(e => {
												const new_row = frm.add_child(key2)
												new_row.document_type = e
												frm.refresh_field(key2)
											})
										}
									}
									for (const [key, value] of Object.entries(r.message.permission[0])) {
										if(value.length > 0) {
											value.forEach(row => {
												getchildren("User Permission Document Type", "Users Permission Manager", key).forEach(e => {
													if(e.document_type==row.document_type){
														e.is_custom =  row.is_custom,
														e.read =  row.read,
														e.write =  row.write,
														e.create =  row.create,
														e.submit =  row.submit,
														e.cancel =  row.cancel,
														e.amend =  row.amend,
														e.delete =  row.delete
													}
												})
											})
										}
									}
									// frm.clear_table('page_or_report')
									// (r.message.repage || []).forEach(row => {
									// 	if(row.page){
									// 	let new_row = frm.add_child("page_or_report", {
									// 			'set_role_for': 'Page',
									// 			'page_or_report': row.page
									// 		})
									// 	}else if(row.report){
									// 		let new_row = frm.add_child("page_or_report", {
									// 			'set_role_for':'Report',
									// 			'page_or_report': row.report
									// 		})
									// 	}
										
									// });
									// frm.refresh_field('page_or_report');
								}
								frm.refresh_fields()						
							}	
						})
						d.hide();
					}
				});
				
				d.show();
			}).addClass("btn btn-primary")
		}
	}})

var getchildren = function(doctype, parent, parentfield) {
	var children = [];
	$.each(locals[doctype] || {}, function(i, d) {
		if(d.parent === parent && d.parentfield === parentfield) {
			children.push(d);
		}
	});
	return children;
}