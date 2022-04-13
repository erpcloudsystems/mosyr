// Copyright (c) 2022, AnvilERP and contributors
// For license information, please see license.txt

frappe.ui.form.on('Health Insurance', {
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
						frm.set_value('health_insurance_provider', r.message.health_insurance_provider || '')
						frm.set_value('health_insurance_no', r.message.health_insurance_no || '')
						frm.refresh_fields()
					}
				}
			})
		}
	}
});
