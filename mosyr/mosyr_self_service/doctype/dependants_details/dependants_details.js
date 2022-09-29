// Copyright (c) 2022, AnvilERP and contributors
// For license information, please see license.txt

frappe.ui.form.on('Dependants Details', {
	refresh: function (frm) {
		if (frm.doc.employee && frm.doc.docstatus == 0 && frm.is_new()) {
			frappe.call({
				method: 'frappe.client.get',
				args: {
					doctype: 'Employee',
					name: frm.doc.employee
				},
				callback: function (r) {
					if (r.message) {
						r.message.dependent.forEach((d) => {
							cur_frm.add_child("dependents", d);
						});
						frm.refresh_fields()
					}
				}
			})
		}
	}
});
