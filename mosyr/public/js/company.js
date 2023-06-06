frappe.ui.form.on("Company", {
    refresh: function (frm) {
        frm.clear_custom_buttons()
        cur_frm.dashboard.hide()
    }
});