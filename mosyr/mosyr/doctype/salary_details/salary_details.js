// Copyright (c) 2022, AnvilERP and contributors
// For license information, please see license.txt

frappe.ui.form.on('Salary Details', {
	refresh: function(frm){
		if(frm.doc.employee && frm.doc.docstatus == 0 && frm.is_new()){
			frappe.call({
				method: 'frappe.client.get',
				args:{
					doctype: 'Employee',
					name: frm.doc.employee
				},
				callback: function(r){
					if(r.message){
						frm.set_value('salary_mode', r.message.emergency_phone_number || '')
						frm.set_value('bank_name', r.message.bank_name || '')
						frm.set_value('bank_ac_no', r.message.bank_ac_no || '')
						frm.refresh_fields()
					}
				}
			})
		}
	}
});
