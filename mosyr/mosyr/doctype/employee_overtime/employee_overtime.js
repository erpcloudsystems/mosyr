// Copyright (c) 2022, AnvilERP and contributors
// For license information, please see license.txt

frappe.ui.form.on('Employee Overtime', {
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
    },
    overtime_hours_by_1_5(frm) { frm.trigger('calculate_total_amt') },
    overtime_hours_by_2(frm) { frm.trigger('calculate_total_amt') },
    hour_rate(frm) { frm.trigger('calculate_total_amt') },
    calculate_total_amt(frm) {
        const by_1_5 = flt(frm.doc.hour_rate) * 1.5 * flt(frm.doc.overtime_hours_by_1_5)
        const by_2 = flt(frm.doc.hour_rate) * 2 * flt(frm.doc.overtime_hours_by_2)

        frm.set_value('amount', flt(by_1_5 + by_2))
        frm.refresh_field('amount')
    }
});