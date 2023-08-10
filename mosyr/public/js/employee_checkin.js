// Copyright (c) 2019, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Employee Checkin', {
	refresh: (frm) => {
		frm.set_df_property('time', 'read_only', frm.doc.attendance ? 1 : 0);
		frm.set_df_property('log_type', 'read_only', frm.doc.attendance ? 1 : 0);
		frm.set_df_property('employee', 'read_only', frm.doc.attendance ? 1 : 0);
		if (frm.doc.attendance) {
			frm.add_custom_button(__("Update Checkin"), () => {
				var d = new frappe.ui.Dialog({
					title: __('Update Checkin Time & Log type '),
					fields: [
						{
							"label": "Time",
							"fieldname": "new_time",
							"fieldtype": "Datetime",
							"reqd": 1,
							"default": frm.doc.time
						},
						{
							"label": "Log Type",
							"fieldname": "new_log_type",
							"fieldtype": "Select",
							"options": "IN\nOUT",
							"default": frm.doc.log_type,
							"reqd": 1
						}	
					],
					primary_action: function() {
						var data = d.get_values();
						if (data.new_time == frm.doc.time && data.new_log_type == frm.doc.log_type) {
							frappe.throw("There is no changes between current Values and Updated Values of time and log type")
						}
						frappe.dom.freeze();
						frappe.call({
							method: "mosyr.api.update_employee_checkin",
							args: {
								docname: frm.doc.name,
								new_time: data.new_time,
								new_log_type: data.new_log_type
							},
							callback: function(r) {
								frappe.dom.unfreeze();
								if(!r.exc) {
									frappe.msgprint("Your Checkin Updated Successfully")
									d.hide();
									frm.reload_doc();
								}
							}
						});
					},
					primary_action_label: __('Update')
				});
				d.show();
			})
		}
	}
});
