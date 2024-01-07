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
	read_system_management:function(frm){
		frm.doc.system_management.forEach((row)=>{
			row.read = frm.doc.read_system_management
		})
		frm.refresh_field('system_management');
	},
	write_system_management:function(frm){
		frm.doc.system_management.forEach((row)=>{
			row.write = frm.doc.write_system_management
		})
		frm.refresh_field('system_management');
	},
	create_system_management:function(frm){
		frm.doc.system_management.forEach((row)=>{
			row.create = frm.doc.create_system_management
		})
		frm.refresh_field('system_management');
	},
	read_user_management:function(frm){
		frm.doc.user_management.forEach((row)=>{
			row.read = frm.doc.read_user_management
		})
		frm.refresh_field('user_management');
	},
	write_user_management:function(frm){
		frm.doc.user_management.forEach((row)=>{
			row.write = frm.doc.write_user_management
		})
		frm.refresh_field('user_management');
	},
	create_user_management:function(frm){
		frm.doc.user_management.forEach((row)=>{
			row.create = frm.doc.create_user_management
		})
		frm.refresh_field('user_management');
	},
	read_hr_mangement:function(frm){
		frm.doc.hr_management.forEach((row)=>{
			row.read = frm.doc.read_hr_mangement
		})
		frm.refresh_field('hr_management');
	},
	write_hr_mangement:function(frm){
		frm.doc.hr_management.forEach((row)=>{
			row.write = frm.doc.write_hr_mangement
		})
		frm.refresh_field('hr_management');
	},
	create_hr_mangement:function(frm){
		frm.doc.hr_management.forEach((row)=>{
			row.create = frm.doc.create_hr_mangement
		})
		frm.refresh_field('hr_management');
	},



	read_employees_list:function(frm){
		frm.doc.employees_list.forEach((row)=>{
			row.read = frm.doc.read_employees_list
		})
		frm.refresh_field('employees_list');
	},
	write_employees_list:function(frm){
		frm.doc.employees_list.forEach((row)=>{
			row.write = frm.doc.write_employees_list
		})
		frm.refresh_field('employees_list');
	},
	create_employees_list:function(frm){
		frm.doc.employees_list.forEach((row)=>{
			row.create = frm.doc.create_employees_list
		})
		frm.refresh_field('employees_list');
	},


	read_self_service:function(frm){
		frm.doc.self_service.forEach((row)=>{
			row.read = frm.doc.read_self_service
		})
		frm.refresh_field('self_service');
	},
	write_self_service:function(frm){
		frm.doc.self_service.forEach((row)=>{
			row.write = frm.doc.write_self_service
		})
		frm.refresh_field('self_service');
	},
	create_self_service:function(frm){
		frm.doc.self_service.forEach((row)=>{
			row.create = frm.doc.create_self_service
		})
		frm.refresh_field('self_service');
	},
	read_e_form:function(frm){
		frm.doc.e_form.forEach((row)=>{
			row.read = frm.doc.read_e_form
		})
		frm.refresh_field('e_form');
	},
	write_e_form:function(frm){
		frm.doc.e_form.forEach((row)=>{
			row.write = frm.doc.write_e_form
		})
		frm.refresh_field('e_form');
	},
	create_e_form:function(frm){
		frm.doc.e_form.forEach((row)=>{
			row.create = frm.doc.create_e_form
		})
		frm.refresh_field('e_form');
	},

	read_timesheet_attendees_management:function(frm){
		frm.doc.timesheet_attendees_management.forEach((row)=>{
			row.read = frm.doc.read_timesheet_attendees_management
		})
		frm.refresh_field('timesheet_attendees_management');
	},
	write_timesheet_attendees_management:function(frm){
		frm.doc.timesheet_attendees_management.forEach((row)=>{
			row.write = frm.doc.write_timesheet_attendees_management
		})
		frm.refresh_field('timesheet_attendees_management');
	},
	create_timesheet_attendees_management:function(frm){
		frm.doc.timesheet_attendees_management.forEach((row)=>{
			row.create = frm.doc.create_timesheet_attendees_management
		})
		frm.refresh_field('timesheet_attendees_management');
	},
	read_payroll:function(frm){
		frm.doc.payroll.forEach((row)=>{
			row.read = frm.doc.read_payroll
		})
		frm.refresh_field('payroll');
	},
	write_payroll:function(frm){
		frm.doc.payroll.forEach((row)=>{
			row.write = frm.doc.write_payroll
		})
		frm.refresh_field('payroll');
	},
	create_payroll:function(frm){
		frm.doc.payroll.forEach((row)=>{
			row.create = frm.doc.create_payroll
		})
		frm.refresh_field('payroll');
	},
	read_employees_performance:function(frm){
		frm.doc.employees_performance.forEach((row)=>{
			row.read = frm.doc.read_employees_performance
		})
		frm.refresh_field('employees_performance');
	},
	write_employees_performance:function(frm){
		frm.doc.employees_performance.forEach((row)=>{
			row.write = frm.doc.write_employees_performance
		})
		frm.refresh_field('employees_performance');
	},
	create_employees_performance:function(frm){
		frm.doc.employees_performance.forEach((row)=>{
			row.create = frm.doc.create_employees_performance
		})
		frm.refresh_field('employees_performance');
	},


	read_leave:function(frm){
		frm.doc.leave.forEach((row)=>{
			row.read = frm.doc.read_leave
		})
		frm.refresh_field('leave');
	},
	write_leave:function(frm){
		frm.doc.leave.forEach((row)=>{
			row.write = frm.doc.write_leave
		})
		frm.refresh_field('leave');
	},
	create_leave:function(frm){
		frm.doc.leave.forEach((row)=>{
			row.create = frm.doc.create_leave
		})
		frm.refresh_field('leave');
	},

	read_loans:function(frm){
		frm.doc.loans.forEach((row)=>{
			row.read = frm.doc.read_loans
		})
		frm.refresh_field('loans');
	},
	write_loans:function(frm){
		frm.doc.loans.forEach((row)=>{
			row.write = frm.doc.write_loans
		})
		frm.refresh_field('loans');
	},
	create_loans:function(frm){
		frm.doc.loans.forEach((row)=>{
			row.create = frm.doc.create_loans
		})
		frm.refresh_field('loans');
	},


	read_vehicle_management:function(frm){
		frm.doc.vehicle_management.forEach((row)=>{
			row.read = frm.doc.read_vehicle_management
		})
		frm.refresh_field('vehicle_management');
	},
	write_vehicle_management:function(frm){
		frm.doc.vehicle_management.forEach((row)=>{
			row.write = frm.doc.write_vehicle_management
		})
		frm.refresh_field('vehicle_management');
	},
	create_vehicle_management:function(frm){
		frm.doc.vehicle_management.forEach((row)=>{
			row.create = frm.doc.create_vehicle_management
		})
		frm.refresh_field('vehicle_management');
	},


	read_documents_management:function(frm){
		frm.doc.documents_management.forEach((row)=>{
			row.read = frm.doc.read_documents_management
		})
		frm.refresh_field('documents_management');
	},
	write_documents_management:function(frm){
		frm.doc.documents_management.forEach((row)=>{
			row.write = frm.doc.write_documents_management
		})
		frm.refresh_field('documents_management');
	},
	create_documents_management:function(frm){
		frm.doc.documents_management.forEach((row)=>{
			row.create = frm.doc.create_documents_management
		})
		frm.refresh_field('documents_management');
	},
	read_custody_management:function(frm){
		frm.doc.custody_management.forEach((row)=>{
			row.read = frm.doc.read_custody_management
		})
		frm.refresh_field('custody_management');
	},
	write_custody_management:function(frm){
		frm.doc.custody_management.forEach((row)=>{
			row.write = frm.doc.write_custody_management
		})
		frm.refresh_field('custody_management');
	},
	create_custody_management:function(frm){
		frm.doc.custody_management.forEach((row)=>{
			row.create = frm.doc.create_custody_management
		})
		frm.refresh_field('custody_management');
	},
	read_page_or_report:function(frm){
		frm.doc.page_or_report.forEach((row)=>{
			row.read = frm.doc.read_page_or_report
		})
		frm.refresh_field('page_or_report');
	},
	write_page_or_report:function(frm){
		frm.doc.page_or_report.forEach((row)=>{
			row.write = frm.doc.write_page_or_report
		})
		frm.refresh_field('page_or_report');
	},
	create_page_or_report:function(frm){
		frm.doc.page_or_report.forEach((row)=>{
			row.create = frm.doc.create_page_or_report
		})
		frm.refresh_field('page_or_report');
	},
	onload: function(frm){
		
		// $(document).on('click', '.grid-heading-row [title="Write"] input[type="checkbox"]', async function() {
		// 	// 'this' refers to the clicked checkbox
		// 	const all_read = $(this)
		// 	const parentElement = $(this).closest('[title="Write"]').closest('.data-row').closest('.data-row').closest('.grid-row').closest('.grid-heading-row').closest('.form-grid').closest('.form-grid');
		// 	const child = parentElement.find('.grid-body').find('.grid-row').find('.data-row').find('[data-fieldname="write"]')
		// 	await child.each(async function() {
		// 		$(this).find('.field-area').css("display", "block")
		// 		$(this).find('.field-area').css("display", "none")
		// 		await $(this).click()
		// 		if(all_read.prop('checked')){
		// 			if ($(this).find(".field-area").find('[type="checkbox"]').prop('checked'))
		// 				$(this).find(".field-area").find('[type="checkbox"]').prop('checked', true)
		// 			else
		// 				$(this).find(".field-area").find('[type="checkbox"]').prop('checked', true)

		// 		}else{
		// 			$(this).find(".field-area").find('[type="checkbox"]').prop('checked', false)
		// 		}
		// 	})
		// 	// const child2 = parentElement.find('.grid-body').find('[data-fieldname="write"]').find('input[type="checkbox"]')
		// 	// child2.each(function() {
		// 	// 	if(all_read.prop('checked')){
		// 	// 		// if (!$(this).find(".field-area").find('[type="checkbox"]').prop('checked'))
		// 	// 		console.log("hiiiiiiiiiiiiiiiiiiiii")
		// 	// 			$(this).find(".field-area").find('[type="checkbox"]').prop('checked', true)

		// 	// 	}else{
		// 	// 		$(this).find(".field-area").find('[type="checkbox"]').prop('checked', false)
		// 	// 	}
				
		// 	// 	// $(this).prop('checked', function(i, val) {
		// 	// 	// 	return !val;
		// 	// 	// });
		// 	// })
		// });
		// $(document).on('click', '.grid-heading-row [title="Create"] input[type="checkbox"]', async function() {
		// 	// 'this' refers to the clicked checkbox
		// 	const all_read = $(this)
		// 	const parentElement = $(this).closest('[title="Create"]').closest('.data-row').closest('.data-row').closest('.grid-row').closest('.grid-heading-row').closest('.form-grid').closest('.form-grid');
		// 	const child = parentElement.find('.grid-body').find('.grid-row').find('.data-row').find('[data-fieldname="create"]')
		// 	await child.each(async function() {
		// 		$(this).find('.field-area').css("display", "block")
		// 		$(this).find('.field-area').css("display", "none")
		// 		await $(this).click()
		// 		// if(all_read.prop('checked')){
		// 		// 	console.log("hiiiiiiiiiiiiiiiiiiiii")
		// 		// 	// if (!$(this).find(".field-area").find('[type="checkbox"]').prop('checked'))
		// 		// 		$(this).find(".field-area").find('[type="checkbox"]').prop('checked', true)

		// 		// }else{
		// 		// 	$(this).find(".field-area").find('[type="checkbox"]').prop('checked', false)
		// 		// }
		// 	})
		// 	const child2 = parentElement.find('.grid-body').find('[data-fieldname="create"]').find('input[type="checkbox"]')
		// 	child2.each(function() {
		// 		if(all_read.prop('checked')){
		// 			// if (!$(this).find(".field-area").find('[type="checkbox"]').prop('checked'))
		// 			console.log("hiiiiiiiiiiiiiiiiiiiii")
		// 				$(this).find(".field-area").find('[type="checkbox"]').prop('checked', true)

		// 		}else{
		// 			$(this).find(".field-area").find('[type="checkbox"]').prop('checked', false)
		// 		}
				
		// 		// $(this).prop('checked', function(i, val) {
		// 		// 	return !val;
		// 		// });
		// 	})
		// });
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
					frm.refresh_fields()
					if (r.message) {
						console.log("Success");
						frm.refresh_field('page_or_report');
						
					}
					frm.refresh_fields()
					let index1 = 0
					// $('[title="Read"]').each( async function() {
					// 	// Inside the loop, 'this' refers to the current element
					// 	$(this).append(`<input type="checkbox" class="read-input-${index1}"  >`);
					// 	$(this).addClass('d-flex')
					// 	$(this).addClass('justify-content-around')
					// 	$(this).addClass('align-items-center')

			
					// 	index1 +=1
					// });
					// index1= 0
					// $('[title="Write"]').each(function() {
					// 	// Inside the loop, 'this' refers to the current element
					// 	$(this).append(`<input type="checkbox"  class="write-input-${index1}">`);
					// 	$(this).addClass('d-flex')
					// 	$(this).addClass('justify-content-around')
					// 	$(this).addClass('align-items-center')
					// 	// Inside the loop, 'this' refers to the current element
					// 	index1 +=1
					// });
					// index1 = 0
					// $('[title="Create"]').each(function() {
					// 	// Inside the loop, 'this' refers to the current element
					// 	$(this).append(`<input type="checkbox"  class="create-input-${index1}">`);
					// 	$(this).addClass('d-flex')
					// 	$(this).addClass('justify-content-around')
					// 	$(this).addClass('align-items-center')

					// 	index1 +=1

					// });
				}
			})

			frm.add_custom_button("Apply Permissions", ()=>{
				console.log(frm.doc.system_management.concat(
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
				))
				frappe.call({
					doc:frm.doc,
					method: "apply_permissions",
					freeze: true,
					freeze_message: __("Please Wait..."), 
					args:{
						user: frm.doc.user,
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
						rps: frm.doc.page_or_report
					},
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