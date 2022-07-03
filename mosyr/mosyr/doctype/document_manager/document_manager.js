// Copyright (c) 2022, AnvilERP and contributors
// For license information, please see license.txt

frappe.ui.form.on('Document Manager', {
	employee: function(frm){
		if(!frm.doc.employee){
			frm.doc.employee_name = ""
		}
		frm.refresh_field("employee_name")
	},
	assign_employee: function(frm){
		if (!frm.doc.assign_employee){
			frm.doc.employee = ""
			frm.trigger("employee")
		}
		frm.refresh_field("employee")
	},
	posting_date_g: function (frm) { 
		if (frm.doc.posting_date_g){
			frappe.call({
				method: "mosyr.api.convert_date",
				args: {
					gregorian_date: frm.doc.posting_date_g
				},
				callback: r => {
					if (r.message){
						frm.doc.posting_date_h = r.message
						frm.refresh_field('posting_date_h')
					}
				}
			})
		}
	 },
	 posting_date_h: function (frm) { 
		if (frm.doc.posting_date_h){
			frappe.call({
				method: "mosyr.api.convert_date",
				args: {
					hijri_date: frm.doc.posting_date_h
				},
				callback: r => {
					if (r.message){
						frm.doc.posting_date_g = r.message
						frm.refresh_field('posting_date_g')
					}
				}
			})
		}
	 },
	due_date_g: function (frm) { 
		if (frm.doc.due_date_g){
			frappe.call({
				method: "mosyr.api.convert_date",
				args: {
					gregorian_date: frm.doc.due_date_g
				},
				callback: r => {
					if (r.message){
						frm.doc.due_date_h = r.message
						frm.refresh_field('due_date_h')
					}
				}
			})
		}
	 },
	 due_date_h: function (frm) { 
		if (frm.doc.due_date_h){
			frappe.call({
				method: "mosyr.api.convert_date",
				args: {
					hijri_date: frm.doc.due_date_h
				},
				callback: r => {
					if (r.message){
						frm.doc.due_date_g = r.message
						frm.refresh_field('due_date_g')
					}
				}
			})
		}
	 }
});
