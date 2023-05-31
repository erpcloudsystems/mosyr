// Copyright (c) 2022, AnvilERP and contributors
// For license information, please see license.txt

frappe.ui.form.on('HR Notification Settings', {
	onload: function(frm){
        frm.set_query('notification_default_email', function(doc){
            return{
                filters:{
                    'enable_outgoing': 1,
					'default_outgoing': 1,
                }
            }
        })
    },
});
