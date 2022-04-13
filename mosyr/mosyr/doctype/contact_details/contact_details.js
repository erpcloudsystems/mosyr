// Copyright (c) 2022, AnvilERP and contributors
// For license information, please see license.txt

frappe.ui.form.on('Contact Details', {
	prefered_contact_email:function(frm){		
		frm.events.update_contact(frm)		
	},
	company_email:function(frm){
		frm.events.update_contact(frm)
	},
	personal_email:function(frm){
		frm.events.update_contact(frm)
	},
	update_contact:function(frm){
		var prefered_email_fieldname = frappe.model.scrub(frm.doc.prefered_contact_email) || 'user_id';
		frm.set_value("prefered_email",
			frm.fields_dict[prefered_email_fieldname].value)
	},
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
						frm.set_value('cell_number', r.message.cell_number || '')
						frm.set_value('prefered_contact_email', r.message.prefered_contact_email || '')
						frm.set_value('company_email', r.message.company_email || '')
						frm.set_value('personal_email', r.message.personal_email || '')
						frm.set_value('unsubscribed', r.message.unsubscribed || '')
						frm.set_value('second_mobile', r.message.second_mobile || '')
						frm.set_value('permanent_address_is', r.message.permanent_accommodation_type || '')
						frm.set_value('permanent_address', r.message.permanent_address || '')
						frm.set_value('current_address_is', r.message.current_accommodation_type || '')
						frm.set_value('current_address', r.message.current_address || '')
						frm.refresh_fields()
					}
				}
			})
		}
	}
});
