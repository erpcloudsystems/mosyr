// Copyright (c) 2022, AnvilERP and contributors
// For license information, please see license.txt

frappe.ui.form.on('Employee Benefit', {
    refresh: function(frm) {
        if (frm.doc.docstatus == 1 && frm.doc.status == 'Not Applied') {
            frm.add_custom_button('Apply In System', () => {
                frappe.call({
                    method: 'apply_in_system',
                    doc: frm.doc,
                    callback: () => {
                        frm.reload_doc()
                    }
                })
            })
        }
    }
});