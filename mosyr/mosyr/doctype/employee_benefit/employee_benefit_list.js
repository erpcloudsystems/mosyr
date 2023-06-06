// Copyright (c) 2022, AnvilERP and contributors
// For license information, please see license.txt

frappe.listview_settings['Employee Benefit'] = {
    get_indicator: function(doc) {
        if (doc.docstatus == 0) {
            return [__("Draft"), "red", "1,=,1"];
        } else if (doc.status === "Not Applied") {
            // Closed
            return [__("Not Applied"), "orange", "status,=,Not Applied"];
        } else if (doc.status === "Applied In System") {
            // on hold
            return [__("Applied In System"), "green", "status,=,Applied In System"];
        }
    },
    hide_name_column: true

};