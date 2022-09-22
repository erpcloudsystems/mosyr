// Copyright (c) 2022, AnvilERP and contributors
// For license information, please see license.txt

frappe.ui.form.on('Custody', {
	refresh: function (frm) {
		if (frm.doc.docstatus == 1 && frm.doc.status != "Returned") {
			frm.add_custom_button(__("Return Custody"), () => {
				frappe.run_serially([
					() => frappe.new_doc("Return Custody"),
					() => frappe.timeout(1),
					() => cur_frm.set_value("custody", frm.doc.name)
				])
			}).addClass('btn btn-danger')
		}
	},
	receipt_date_g: function (frm) {
		if (frm.doc.receipt_date_g) {
			frappe.call({
				method: "mosyr.api.convert_date",
				args: {
					gregorian_date: frm.doc.receipt_date_g
				},
				callback: r => {
					if (r.message) {
						frm.doc.receipt_date_h = r.message
						frm.refresh_field('receipt_date_h')
					}
				}
			})
		}
	},
	receipt_date_h: function (frm) {
		if (frm.doc.receipt_date_h) {
			frappe.call({
				method: "mosyr.api.convert_date",
				args: {
					hijri_date: frm.doc.receipt_date_h
				},
				callback: r => {
					if (r.message) {
						frm.doc.receipt_date_g = r.message
						frm.refresh_field('receipt_date_g')
					}
				}
			})
		}
	},
});