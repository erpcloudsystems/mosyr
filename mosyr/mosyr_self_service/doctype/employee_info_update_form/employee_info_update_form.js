// Copyright (c) 2022, AnvilERP and contributors
// For license information, please see license.txt

var fields_mapper = {
	"Identity": "Identity",
	"Dependents": "Dependent",
	"Passports": "Passport",
	"Qualifications": "Employee Education",
}
frappe.ui.form.on('Employee Info Update Form', {
	refresh: function (frm) {
		$(".help-box").removeClass("text-muted").addClass("text-danger")
	},
	employee: function (frm) {
		frm.set_value('_update', '')
		frm.refresh_field('_update')
		frm.trigger('update_frm_data')
	},
	_update: function (frm) { frm.trigger('update_frm_data') },
	update_frm_data: function (frm) {
		['', 'identity', 'dependents', 'passports', 'qualifications'].forEach(field_name => {
			frm.clear_table(field_name)
			frm.refresh_field(field_name)
		})
		frm.set_value('clear_if_empty', 0)
		frm.refresh_field('clear_if_empty')

		if (frm.doc.employee) {
			if (["Identity", "Dependents", "Passports", "Qualifications"].includes(frm.doc._update)) {
				let emp_field = fields_mapper[frm.doc._update] || false
				if (emp_field) {
					let field_data = frappe.get_list(emp_field, { 'parent': frm.doc.employee });
					console.log(emp_field, field_data);
				}
				
				// frappe.model.with_doc("Employee", frm.doc.employee, function() {
				// 	let employee_doc = frappe.model.get_doc("Employee", frm.doc.employee);
				// 	let emp_field = fields_mapper[frm.doc._update] || false
				// 	if(emp_field){
				// 		console.log(employee_doc[emp_field]);
				// 	}
				// })
			}
		}
	}
});
