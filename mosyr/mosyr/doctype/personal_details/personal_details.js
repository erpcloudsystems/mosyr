// Copyright (c) 2022, AnvilERP and contributors
// For license information, please see license.txt

frappe.ui.form.on('Personal Details', {
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
						frm.set_value('passport_number', r.message.passport_number || '')
						frm.set_value('date_of_issue', r.message.date_of_issue || '')
						frm.set_value('valid_upto', r.message.valid_upto || '')
						frm.set_value('place_of_issue', r.message.place_of_issue || '')
						frm.set_value('id_number', r.message.id_number || '')
						frm.set_value('id_date_of_issue', r.message.id_date_of_issue || '')
						frm.set_value('id_valid_upto', r.message.id_valid_upto || '')
						frm.set_value('id_place_of_issue', r.message.id_place_of_issue || '')
						frm.set_value('copy_of_id', r.message.copy_of_id || '')
						frm.set_value('driving_licence_number', r.message.driving_licence_number || '')
						frm.set_value('licence_date_of_issue', r.message.licence_date_of_issue || '')
						frm.set_value('licence_valid_upto', r.message.licence_valid_upto || '')
						frm.set_value('attach_licence_copy', r.message.licence_copy_image || '')
						frm.set_value('number_of_dependants', r.message._number_of_dependants || '')
						frm.set_value('copy_of_passport', r.message.copy_of_passport || '')
						frm.set_value('marital_status', r.message.marital_status || '')
						frm.set_value('wedding_certificate', r.message.wedding_certificate || '')
						frm.set_value('spouse_name', r.message.spouse_name || '')
						frm.set_value('spouse_working_status', r.message.spouse_working_status || '')
						frm.set_value('blood_group', r.message.blood_group || '')
						frm.set_value('family_background', r.message.family_background || '')
						frm.set_value('health_details', r.message.health_details || '')
						frm.refresh_fields()
					}
				}
			})
		}
	}
});
