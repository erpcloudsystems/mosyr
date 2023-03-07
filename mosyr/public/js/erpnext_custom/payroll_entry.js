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

frappe.ui.form.on("Payroll Entry", {
    refresh: function (frm) {
        if (frm.doc.docstatus == 0) {
            frm.clear_custom_buttons();
            if (!frm.is_new()) {
                frm.page.clear_primary_action();
                frm.add_custom_button(__("Get Employees"),
                    function () {
                        frm.events.get_employee_details(frm);
                    }
                ).toggleClass('btn-primary', !(frm.doc.employees || []).length);
            }
            if ((frm.doc.employees || []).length && !frappe.model.has_workflow(frm.doctype)) {
                frm.page.clear_primary_action();
                frm.page.set_primary_action(__('Create Salary Slips'), () => {
                    frm.save('Submit').then(() => {
                        frm.page.clear_primary_action();
                        frm.refresh();
                        frm.events.refresh(frm);
                    });
                });
            }
        }
        if (frm.doc.docstatus == 1) {
            if (frm.custom_buttons) frm.clear_custom_buttons();
            frm.events.add_context_buttons(frm);
        }
    },
});

