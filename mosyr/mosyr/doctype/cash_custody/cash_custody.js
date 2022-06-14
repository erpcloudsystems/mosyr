// Copyright (c) 2022, AnvilERP and contributors
// For license information, please see license.txt

frappe.ui.form.on('Cash Custody', {
	// refresh: function(frm) {

	// }
	receipt_date_g: function (frm) { 
		if (frm.doc.receipt_date_g){
			frappe.call({
				method: "mosyr.api.convert_date",
				args: {
					gregorian_date: frm.doc.receipt_date_g
				},
				callback: r => {
					if (r.message){
						frm.doc.receipt_date_h = r.message
						frm.refresh_field('receipt_date_h')
					}
				}
			})
		}
	 },
	 receipt_date_h: function (frm) { 
		if (frm.doc.receipt_date_h){
			frappe.call({
				method: "mosyr.api.convert_date",
				args: {
					hijri_date: frm.doc.receipt_date_h
				},
				callback: r => {
					if (r.message){
						frm.doc.receipt_date_g = r.message
						frm.refresh_field('receipt_date_g')
					}
				}
			})
		}
	 },
});
