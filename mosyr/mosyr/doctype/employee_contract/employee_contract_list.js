// Copyright (c) 2022, AnvilERP and contributors
// For license information, please see license.txt

frappe.listview_settings['Employee Contract'] = {
    get_indicator: function(doc) {
		var colors = {
			"Pending":   "blue",
            "Approved":  "green",
            "Ended":     "blue",
            "Cancelled": "red"
		};
		let status = doc.status;
		if(doc.contract_status == "Valid"){
            return [__(status), colors[status], '1,=,1'];
        }
        return [__("Not Valid"), "red", '1,=,1'];
	},
    hide_name_column: true
};