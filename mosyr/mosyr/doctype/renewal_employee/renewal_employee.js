// Copyright (c) 2024, AnvilERP and contributors
// For license information, please see license.txt

frappe.ui.form.on('Renewal Employee', {
	// refresh: function(frm) {

	// }
	refresh: async  function(frm){
		frm.disable_save()
		cur_frm.refresh_fields("employees");
		await frappe.call({
			doc:frm.doc,
			method: "get_employee_will_be_expired",
			freeze: true,
			callback: function(r){
				cur_frm.clear_table("employees");
				r.message.forEach(element => {
					console.log(element)
			      	var childTable = cur_frm.add_child("employees");
					childTable.employee = element.employee
					childTable.end_of_contract = element.end_of_contract
					childTable.employee_name = element.employee_name
				});
				cur_frm.refresh_fields("employees");
			}
		})
		if(frm.doc.employees.length > 0){
			frm.add_custom_button("Update Employee", ()=>{
				frappe.call({
					doc:frm.doc,
					method: "update_end_contract",
					freeze: true,
					callback: function(r){
						
						cur_frm.refresh_fields("employees");
					}
				})
			}).addClass("btn btn-primary")
		}
		
	},
	employee: async  function(frm){
		cur_frm.clear_table("employees");
		cur_frm.refresh_fields("employees");
		await frappe.call({
			doc:frm.doc,
			method: "get_employee_will_be_expired",
			freeze: true,
			callback: function(r){
				cur_frm.clear_table("employees");
				r.message.forEach(element => {
					console.log(element)
			      	var childTable = cur_frm.add_child("employees");
					childTable.employee = element.employee
					childTable.end_of_contract = element.end_of_contract
					childTable.employee_name = element.employee_name
				});
				cur_frm.refresh_fields("employees");
			}
		})
		
	},
	status: async  function(frm){
		cur_frm.clear_table("employees");
		cur_frm.refresh_fields("employees");
		await frappe.call({
			doc:frm.doc,
			method: "get_employee_will_be_expired",
			freeze: true,
			callback: function(r){
				cur_frm.clear_table("employees");
				r.message.forEach(element => {
					console.log(element)
			      	var childTable = cur_frm.add_child("employees");
					childTable.employee = element.employee
					childTable.end_of_contract = element.end_of_contract
					childTable.employee_name = element.employee_name
				});
				cur_frm.refresh_fields("employees");
			}
		})
		cur_frm.refresh_fields("employees");
		
	},
});
