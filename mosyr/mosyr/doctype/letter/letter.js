// Copyright (c) 2023, AnvilERP and contributors
// For license information, please see license.txt

frappe.ui.form.on('Letter', {
	refresh: function(frm){
		if (frm.doc.docstatus == 1){
			frm.add_custom_button(__("Print"), function () {
				frappe.call({
					doc: frm.doc,
					method: "make_default",
					args: {
						pr_name: frm.doc.type
					},
					callback: function() {
						frm.refresh();
						setTimeout(()=> {
							frm.print_doc()
							$("select[data-fieldname='print_format']").val(__(frm.doc.type)).change();
						}, 500)
					}
				});
			}).addClass("btn-danger");
		}
	},
	date_g: function (frm) {
		if (frm.doc.date_g) {
			frappe.call({
				method: "mosyr.api.convert_date",
				args: {
					gregorian_date: frm.doc.date_g
				},
				callback: r => {
					if (r.message) {
						frm.doc.date_h = r.message
						frm.refresh_field('date_h')
					}
				}
			})
		}
	},
	date_h: function (frm) {
		if (frm.doc.date_h) {
			frappe.call({
				method: "mosyr.api.convert_date",
				args: {
					hijri_date: frm.doc.date_h
				},
				callback: r => {
					if (r.message) {
						frm.doc.date_g = r.message
						frm.refresh_field('date_g')
					}
				}
			})
		}
	}
});
