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
	}
});
