// Copyright (c) 2022, AnvilERP and contributors
// For license information, please see license.txt

frappe.ui.form.on('Moysr Data Import', {
	refresh: function(frm) {
		$('.control-input button').addClass('col-md-6 col-xs-12 btn-primary').removeClass('btn-default')
        $('div[data-fieldname="import_branches"]').css({
            'margin-top': '25px'
        })
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
    }

});


