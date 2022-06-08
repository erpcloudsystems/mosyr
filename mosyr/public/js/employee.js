frappe.ui.form.on('Employee', {
    refresh: function(frm) {
        frm.add_custom_button(__('Identity'), function() {
            frm.scroll_to_field('identity');
        }, __('Jump to'));
        frm.add_custom_button(__('Passport'), function() {
            frm.scroll_to_field('passport');
        }, __('Jump to'));
        frm.add_custom_button(__('Status'), function() {
            frm.scroll_to_field('mosyr_employee_status');
        }, __('Jump to'));
        frm.add_custom_button(__('Qualification'), function() {
            frm.scroll_to_field('education');
        }, __('Jump to'));
        frm.add_custom_button(__('Experince'), function() {
            frm.scroll_to_field('external_work_history');
        }, __('Jump to'));
        frm.add_custom_button(__('Contact'), function() {
            frm.scroll_to_field('cell_number');
        }, __('Jump to'));
        frm.add_custom_button(__('Dependent'), function() {
            frm.scroll_to_field('dependent');
        }, __('Jump to'));
        frm.add_custom_button(__('Insurance'), function() {
            frm.scroll_to_field('health_insurance_provider');
        }, __('Jump to'));
        frm.add_custom_button(__('Salary'), function() {
            frm.scroll_to_field('salary_mode');
        }, __('Jump to'));
        // frm.add_custom_button(__('Leave'), function() {
        //     frm.scroll_to_field('mosyr_employee_status');
        // }, __('Jump to'));
    },
    department: function(frm){
        if (frm.doc.department){
            frappe.call({
                method: "mosyr.api.set_employee_approvers",
                args:{
                    department: frm.doc.department
                },
                callback: r =>{
                    if (r.message){
                        frm.doc.leave_approver = r.message[0]
                        frm.doc.expense_approver = r.message[1]
                        frm.doc.shift_request_approver = r.message[2]
                        frm.refresh_fields()
                    }
                }
            })
        }
    }
});