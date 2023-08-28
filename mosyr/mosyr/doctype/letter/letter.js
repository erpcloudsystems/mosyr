// Copyright (c) 2023, AnvilERP and contributors
// For license information, please see license.txt

frappe.ui.form.on('Letter', {
	setup: function(frm){
		// frm.trigger("set_default_print_format");
	},
	refresh: function(frm){
		// frm.trigger("set_default_print_format");
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
	},
	set_default_print_format: function() {
		// this will be removed with all dependencies after test new method ...
		const print_formats = (cur_frm.meta.__print_formats || []).map(el => el.name)
		const printButton = $("button[data-original-title='Print']");
		const printicon = $("span[data-label='Print']");
		let pr = cur_frm.doc.type
		printButton.on("click", {print_formats, pr}, setDFPrintFormat)
		printicon.on("click", {print_formats, pr}, setDFPrintFormat)
	}
});

const setDFPrintFormat = (params)=> {
	if (params.data.print_formats.includes(params.data.pr)) {
		setTimeout(() => {
			$("select[data-fieldname='print_format']").val(params.data.pr).change();
		}, 500);
	}
	else{
		setTimeout(() => {
			$("select[data-fieldname='print_format']").val("").change();
		}, 500);
	}
}