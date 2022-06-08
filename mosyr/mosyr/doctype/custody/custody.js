// Copyright (c) 2022, AnvilERP and contributors
// For license information, please see license.txt

frappe.ui.form.on('Custody', {
	refresh: function(frm) {
		if (frm.doc.docstatus==1 && frm.doc.status != "Returned"){
			frm.add_custom_button(__("Return Custody"), ()=>{
				frappe.run_serially([
					()=> frappe.new_doc("Return Custody"),
					() => frappe.timeout(1),
					()=> cur_frm.set_value("custody", frm.doc.name)
				])
			}).addClass('btn btn-danger')
		}
	}
});
