make_bank_entry = function (frm) {
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

frappe.ui.form.on("Payroll Entry", {});

