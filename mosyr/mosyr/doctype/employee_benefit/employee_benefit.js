// Copyright (c) 2022, AnvilERP and contributors
// For license information, please see license.txt

frappe.ui.form.on('Employee Benefit', {
    setup: function(frm) {
        if(!frm.doc.date){
            frm.doc.date = frappe.datetime.get_today()
        }
    },
    refresh: function(frm) {
        frm.set_query('employee', function(doc){
            return{
                filters:{
                    'status': 'Active'
                }
            }
        })
    }
});