frappe.ui.form.on('Employee', {
	refresh: function(frm) {
		frm.set_query( 'user_id', function(doc) {
			return {
				query: "mosyr.api.get_users_2",

			};
		});
		frm.add_custom_button(__('Identity'), function() {
			frm.scroll_to_field('identity');
		}, __('Jump to'));
		frm.add_custom_button(__('Passport'), function() {
			frm.scroll_to_field('passport');
		}, __('Jump to'));
		frm.add_custom_button(__('Status'), function() {
			frm.scroll_to_field('mosyr_employee_status');
		}, __('Jump to'));
		frm.add_custom_button(__('Qualification'), function() {
			frm.scroll_to_field('education');
		}, __('Jump to'));
		frm.add_custom_button(__('Experince'), function() {
			frm.scroll_to_field('external_work_history');
		}, __('Jump to'));
		frm.add_custom_button(__('Contact'), function() {
			frm.scroll_to_field('cell_number');
		}, __('Jump to'));
		frm.add_custom_button(__('Dependent'), function() {
			frm.scroll_to_field('dependent');
		}, __('Jump to'));
		frm.add_custom_button(__('Insurance'), function() {
			frm.scroll_to_field('health_insurance_provider');
		}, __('Jump to'));
		frm.add_custom_button(__('Salary'), function() {
			frm.scroll_to_field('salary_mode');
		}, __('Jump to'));
		let current_date = frappe.datetime.get_today()
		let passport_expired_list = []
		let msg = ""
		// Check Contract Expired Date
		if(frm.doc.contract_end_date){
			let contract_diff = frappe.datetime.get_diff(frm.doc.contract_end_date, current_date)
			if (contract_diff <= 30 && contract_diff >= 0) {
				msg += __(`Contract Will Be Expired in ${contract_diff} days <br>`)
			}
		}
		// Check Identity Expired Date 
		if (frm.doc.identity) {
			frm.doc.identity.forEach(row => {
				let diff = frappe.datetime.get_diff(row.expire_date, current_date)
				if (diff <= 30 && diff >= 0 ) {
					msg += __(`Identity ${ row.id_number } Will Be Expired in ${diff} days <br>`)
				}
			});
		}
		// Check Passport Expired Date 
		if (frm.doc.passport) {
			frm.doc.passport.forEach(row => {
				let diff = frappe.datetime.get_diff(row.passport_expire, current_date)
				if (diff <= 30 && diff >= 0 ) {
					msg += __(`Passport ${ row.passport_number } Will Be Expired in ${diff} days <br>`)
				}
			});
		}
		// Check Insurance Expired Date 
		if(frm.doc.insurance_card_expire){
			let ins_diff = frappe.datetime.get_diff(frm.doc.insurance_card_expire, current_date)
			if (ins_diff <= 30 && ins_diff >= 0) {
				msg += __(`Insurance Card Will Be Expired in ${ins_diff} days <br>`)
			}
		}
		cur_frm.dashboard.add_comment(__(msg), 'yellow', true);
	},
	date_of_birth: function (frm) { 
		if (frm.doc.date_of_birth){
			frappe.call({
				method: "mosyr.api.convert_date",
				args: {
					gregorian_date: frm.doc.date_of_birth
				},
				callback: r => {
					if (r.message){
						frm.doc.hijri_date_of_birth = r.message
						frm.refresh_field('hijri_date_of_birth')
					}
				}
			})
		}
	 },
	 hijri_date_of_birth: function (frm) { 
		if (frm.doc.hijri_date_of_birth){
			frappe.call({
				method: "mosyr.api.convert_date",
				args: {
					hijri_date: frm.doc.hijri_date_of_birth
				},
				callback: r => {
					if (r.message){
						frm.doc.date_of_birth = r.message
						frm.refresh_field('date_of_birth')
					}
				}
			})
		}
	 },
	department: function(frm){
		if (frm.doc.department){
			frappe.call({
				method: "mosyr.api.set_employee_approvers",
				args:{
					department: frm.doc.department
				},
				callback: r =>{
					if (r.message){
						frm.doc.leave_approver = r.message[0]
						frm.doc.expense_approver = r.message[1]
						frm.doc.shift_request_approver = r.message[2]
						frm.refresh_fields()
					}
				}
			})
		}
	}
});
frappe.ui.form.on('Employee Status', {
	status_date: function (frm, cdt, cdn) {
		let row = locals[cdt][cdn] 
		if (row.status_date){
			frappe.call({
				method: "mosyr.api.convert_date",
				args: {
					gregorian_date: row.status_date
				},
				callback: r => {
					if (r.message){
						row.status_date_h = r.message
						frm.refresh_field('mosyr_employee_status')
					}
				}
			})
		}
	 },
	 status_date_h: function (frm, cdt, cdn) {
		let row = locals[cdt][cdn] 
		if (row.status_date_h){
			frappe.call({
				method: "mosyr.api.convert_date",
				args: {
					hijri_date: row.status_date_h
				},
				callback: r => {
					if (r.message){
						row.status_date = r.message
						frm.refresh_field('mosyr_employee_status')
					}
				}
			})
		}
	 }
})

frappe.ui.form.on('Dependent', {
	birth_date_g: function (frm, cdt, cdn) {
		let row = locals[cdt][cdn] 
		if (row.birth_date_g){
			frappe.call({
				method: "mosyr.api.convert_date",
				args: {
					gregorian_date: row.birth_date_g
				},
				callback: r => {
					if (r.message){
						row.birth_date_h = r.message
						frm.refresh_field('dependent')
					}
				}
			})
		}
	 },
	 birth_date_h: function (frm, cdt, cdn) {
		let row = locals[cdt][cdn] 
		if (row.birth_date_h){
			frappe.call({
				method: "mosyr.api.convert_date",
				args: {
					hijri_date: row.birth_date_h
				},
				callback: r => {
					if (r.message){
						row.birth_date_g = r.message
						frm.refresh_field('dependent')
					}
				}
			})
		}
	 }
})

frappe.ui.form.on('Identity', {
	expire_date: function (frm, cdt, cdn) {
		let row = locals[cdt][cdn] 
		if (row.expire_date){
			frappe.call({
				method: "mosyr.api.convert_date",
				args: {
					gregorian_date: row.expire_date
				},
				callback: r => {
					if (r.message){
						row.expire_date_h = r.message
						frm.refresh_field('identity')
					}
				}
			})
		}
	 },
	 expire_date_h: function (frm, cdt, cdn) {
		let row = locals[cdt][cdn] 
		if (row.expire_date_h){
			frappe.call({
				method: "mosyr.api.convert_date",
				args: {
					hijri_date: row.expire_date_h
				},
				callback: r => {
					if (r.message){
						row.expire_date = r.message
						frm.refresh_field('identity')
					}
				}
			})
		}
	 },
	 issue_date: function (frm, cdt, cdn) {
		let row = locals[cdt][cdn] 
		if (row.issue_date){
			frappe.call({
				method: "mosyr.api.convert_date",
				args: {
					gregorian_date: row.issue_date
				},
				callback: r => {
					if (r.message){
						row.issue_date_h = r.message
						frm.refresh_field('identity')
					}
				}
			})
		}
	 },
	 issue_date_h: function (frm, cdt, cdn) {
		let row = locals[cdt][cdn] 
		if (row.issue_date_h){
			frappe.call({
				method: "mosyr.api.convert_date",
				args: {
					hijri_date: row.issue_date_h
				},
				callback: r => {
					if (r.message){
						row.issue_date = r.message
						frm.refresh_field('identity')
					}
				}
			})
		}
	 },
	 border_entry_date: function (frm, cdt, cdn) {
		let row = locals[cdt][cdn] 
		if (row.border_entry_date){
			frappe.call({
				method: "mosyr.api.convert_date",
				args: {
					gregorian_date: row.border_entry_date
				},
				callback: r => {
					if (r.message){
						row.border_entry_date_h = r.message
						frm.refresh_field('identity')
					}
				}
			})
		}
	 },
	 border_entry_date_h: function (frm, cdt, cdn) {
		let row = locals[cdt][cdn] 
		if (row.border_entry_date_h){
			frappe.call({
				method: "mosyr.api.convert_date",
				args: {
					hijri_date: row.border_entry_date_h
				},
				callback: r => {
					if (r.message){
						row.border_entry_date = r.message
						frm.refresh_field('identity')
					}
				}
			})
		}
	 }
})
frappe.ui.form.on('Passport', {
	passport_expire: function (frm, cdt, cdn) {
		let row = locals[cdt][cdn] 
		if (row.passport_expire){
			frappe.call({
				method: "mosyr.api.convert_date",
				args: {
					gregorian_date: row.passport_expire
				},
				callback: r => {
					if (r.message){
						row.passport_expire_h = r.message
						frm.refresh_field('passport')
					}
				}
			})
		}
	 },
	passport_expire_h: function (frm, cdt, cdn) {
		let row = locals[cdt][cdn] 
		if (row.passport_expire_h){
			frappe.call({
				method: "mosyr.api.convert_date",
				args: {
					hijri_date: row.passport_expire_h
				},
				callback: r => {
					if (r.message){
						row.passport_expire = r.message
						frm.refresh_field('passport')
					}
				}
			})
		}
	 },
	 passport_issue_date: function (frm, cdt, cdn) {
		let row = locals[cdt][cdn] 
		if (row.passport_issue_date){
			frappe.call({
				method: "mosyr.api.convert_date",
				args: {
					gregorian_date: row.passport_issue_date
				},
				callback: r => {
					if (r.message){
						row.passport_issue_date_h = r.message
						frm.refresh_field('passport')
					}
				}
			})
		}
	 },
	passport_issue_date_h: function (frm, cdt, cdn) {
		let row = locals[cdt][cdn] 
		if (row.passport_issue_date_h){
			frappe.call({
				method: "mosyr.api.convert_date",
				args: {
					hijri_date: row.passport_issue_date_h
				},
				callback: r => {
					if (r.message){
						row.passport_issue_date = r.message
						frm.refresh_field('passport')
					}
				}
			})
		}
	 },
})
