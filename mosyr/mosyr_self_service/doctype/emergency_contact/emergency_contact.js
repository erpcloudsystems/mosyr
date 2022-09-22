// Copyright (c) 2022, AnvilERP and contributors
// For license information, please see license.txt

frappe.ui.form.on('Emergency Contact', {
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
						frm.set_value('emergency_phone', r.message.emergency_phone_number || '')
						frm.set_value('emergency_contact_name', r.message.person_to_be_contacted || '')
						frm.set_value('relation', r.message.relation || '')
						frm.refresh_fields()
					}
				}
			})
		}
	}
});
