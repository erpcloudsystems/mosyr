// Copyright (c) 2022, AnvilERP and contributors
// For license information, please see license.txt

frappe.ui.form.on('Mosyr Data Import', {
    refresh: function(frm) {
        frm.disable_form()
        frappe.call({
            doc: frm.doc,
            method: 'get_company_id',
            callback: function(r) {
                if (r.message) {
                    frm.set_value('company_id', r.message)
                    frm.refresh_field('company_id')
                    frm.toggle_enable('company_id', 0)
                } else {
                    frm.toggle_enable('company_id', 1)
                    frm.toggle_reqd('company_id', 1)
                }
            },
            freeze: true,
            freeze_message: __("Get Company id"),
        })
    },
    data_import_call(frm, methode, msg = "") {
        frappe.call({
            doc: frm.doc,
            method: methode,
            args: {
                company_id: frm.doc.company_id || ''
            },
            freeze: true,
            freeze_message: __(msg),
        })
    },
    psc(frm) {
        frm.events.data_import_call(frm, 'psc', "Start Salary Components Preparing")
    },
    import_branches(frm) {
        frm.events.data_import_call(frm, 'import_branches', "Start Branches Importing")
    },
    import_departments(frm) {
        frm.events.data_import_call(frm, 'import_departments', "Start Employee Classes Importing")
    },
    import_employees(frm) {
        frm.events.data_import_call(frm, 'import_employees', "Start Employees Importing")
    },
    import_identity(frm) {
        frm.events.data_import_call(frm, 'import_identity', "Start Employee Identities Importing")
    },
    import_dependents(frm) {
        frm.events.data_import_call(frm, 'import_dependents', "Start Employee Dependents Importing")
    },
    import_employee_status(frm) {
        frm.events.data_import_call(frm, 'import_employee_status', "Start Employee Statuses Importing")
    },
    import_experiences(frm) {
        frm.events.data_import_call(frm, 'import_experiences', "Start Employee Experiences Importing")
    },
    import_passport(frm) {
        frm.events.data_import_call(frm, 'import_passport', "Start Employee Passports Importing")
    },
    import_employee_qualifications(frm) {
        frm.events.data_import_call(frm, 'import_employee_qualifications', "Start Employee Qualifications Importing")
    },
    import_contracts(frm) {
        frm.events.data_import_call(frm, 'import_contracts', "Start Employee Contracts Importing")
    },
    import_letters(frm) {
        frm.events.data_import_call(frm, 'import_letters', "Start Employee Letters Importing")
    },
    import_overtime(frm) {
        frm.events.data_import_call(frm, 'import_overtime', "Start Employee Overtime Importing")
    },
    import_deductions(frm) {
        frm.events.data_import_call(frm, 'import_deductions', "Start Employee Deductions Importing")
    },
    import_benefits(frm) {
        frm.events.data_import_call(frm, 'import_benefits', "Start Employee Benefits Importing")
    },

    import_leave(frm) {
        frm.events.data_import_call(frm, 'import_leave', "Start fetch leave Type")
    },
    import_leave_application(frm) {
        frm.events.data_import_call(frm, 'import_leave_application', "Start fetch leave")
    }

});