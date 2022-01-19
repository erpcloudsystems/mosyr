// Copyright (c) 2022, AnvilERP and contributors
// For license information, please see license.txt

frappe.ui.form.on('Moysr Data Import', {
    refresh: function(frm) {
        $('.control-input button').addClass('col-md-6 col-xs-12 btn-primary').removeClass('btn-default')
        $(`div[data-fieldname="master_data"]`).html(`<h3>${__("Master Data")}</h3>`)
        $(`div[data-fieldname="employee_data"]`).html(`<h3>${__("Employee Data")}</h3>`)
        // $(`div[data-fieldname="employee_details"]`).html(`<h3>${__("Employee Details")}</h3>`)
        // $('div[data-fieldname="import_branches"]').css({
        //     'margin-top': '25px'
        // })
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
    import_branches(frm) {
        frm.events.data_import_call(frm, 'import_branches', "Start fetch Branches")
    },
    import_employees(frm) {
        frm.events.data_import_call(frm, 'import_employees', "Start fetch Employee")
    },
    import_contracts(frm) {
        frm.events.data_import_call(frm, 'import_contracts', "Start fetch Contracts")
    },
    import_benefits(frm) {
        frm.events.data_import_call(frm, 'import_benefits', "Start fetch Benefits")
    },
    import_deductions(frm) {
        frm.events.data_import_call(frm, 'import_deductions', "Start fetch Deductions")
    },
    import_identity(frm) {
        frm.events.data_import_call(frm, 'import_identity', "Start fetch identity")
    },
    import_passport(frm) {
        frm.events.data_import_call(frm, 'import_passport', "Start fetch passport")
    },
    import_dependents(frm) {
        frm.events.data_import_call(frm, 'import_dependents', "Start fetch dependents")
    },
    import_employee_status(frm) {
        frm.events.data_import_call(frm, 'import_employee_status', "Start fetch employee status")
    },
    import_experiences(frm) {
        frm.events.data_import_call(frm, 'import_experiences', "Start fetch experiences")
    },
    import_identity(frm) {
        frm.events.data_import_call(frm, 'import_identity', "Start fetch identity")
    },
    import_employee_qualifications(frm) {
        frm.events.data_import_call(frm, 'import_employee_qualifications', "Start fetch qualifications")
    },
    import_employee_class(frm) {
        frm.events.data_import_call(frm, 'import_employee_class', "Start fetch employee classes")
    }

});