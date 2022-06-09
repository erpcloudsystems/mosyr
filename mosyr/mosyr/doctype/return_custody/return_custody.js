// Copyright (c) 2022, AnvilERP and contributors
// For license information, please see license.txt

frappe.ui.form.on('Return Custody', {
	// refresh: function(frm) {

	// }
	return_date_g: function (frm) { 
		if (frm.doc.return_date_g){
			frappe.call({
				doc: frm.doc,
				method: "convert_date",
				args: {
					gregorian_date: frm.doc.return_date_g
				},
				callback: r => {
					if (r.message){
						frm.doc.return_date_h = r.message
						frm.refresh_field('return_date_h')
					}
				}
			})
		}
	 },
	 return_date_h: function (frm) { 
		if (frm.doc.return_date_h){
			frappe.call({
				doc: frm.doc,
				method: "convert_date",
				args: {
					hijri_date: frm.doc.return_date_h
				},
				callback: r => {
					if (r.message){
						frm.doc.return_date_g = r.message
						frm.refresh_field('return_date_g')
					}
				}
			})
		}
	 }
});
