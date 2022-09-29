// Copyright (c) 2022, AnvilERP and contributors
// For license information, please see license.txt

frappe.ui.form.on('Work Experience', {
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
						r.message.external_work_history.forEach((d) => {
							cur_frm.add_child("external_work_history", d);
						});
						frm.refresh_fields()
					}
				}
			})
		}
	}
});
