// Copyright (c) 2022, AnvilERP and contributors
// For license information, please see license.txt

frappe.ui.form.on('Educational Qualification', {
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
						r.message.education.forEach((d) => {
							cur_frm.add_child("education",d);
						});
						frm.refresh_fields()
					}
				}
			})
		}
	}
});
