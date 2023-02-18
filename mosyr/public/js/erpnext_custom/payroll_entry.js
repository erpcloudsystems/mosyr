frappe.ui.form.on("Payroll Entry", {
    setup: function (frm) {
        let make_bank_entry_v2 = function (frm) {
            var doc = frm.doc;
            if (doc.payment_account) {
                return frappe.call({
                    doc: cur_frm.doc,
                    method: "make_payment_entry",
                    callback: function () {
                        frappe.msgprint(__("Payment Entries Created"));
                        frm.events.refresh(frm);
                    },
                    freeze: true,
                    freeze_message: __("Creating Payment Entries......")
                });
            } else {
                frappe.msgprint(__("Payment Account is mandatory"));
                frm.scroll_to_field('payment_account');
            }
        };
        cur_frm.cscript.frm.events.add_context_buttons = function (frm) {
            frappe.call({
                method: 'erpnext.payroll.doctype.payroll_entry.payroll_entry.payroll_entry_has_bank_entries',
                args: {
                    'name': frm.doc.name
                },
                callback: function (r) {
                    if (r.message && !r.message.submitted) {
                        frm.add_custom_button("Make Bank Entry", function () {
                            make_bank_entry_v2(frm);
                        }).addClass("btn-primary");
                    }
                }
            });
        }
    },
});
