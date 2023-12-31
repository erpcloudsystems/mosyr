// Copyright (c) 2023, AnvilERP and contributors
// For license information, please see license.txt

frappe.ui.form.on('Shift Builder', {
	refresh: function (frm) {
		$('div[data-fieldtype="Heading"] h4').css('font-weight', 'normal');
		$('div[data-fieldtype="Heading"] h4').css('font-size', '13px');
		// $('div[data-fieldtype="Heading"] h4').css('margin', '0');
		const toHide = ['sunday_entering_the_second_period', 'sunday_entering_the_first_period', 'sunday_entering_the_first_period', 'sunday_entry_grace_period', 'sunday_exit_the_first_period', 'sunday_exit_the_second_period', 'sunday_exit_grace_period', 'monday_entering_the_first_period', 'monday_entering_the_second_period', 'monday_entering_the_first_period', 'monday_entry_grace_period', 'monday_exit_the_first_period', 'monday_exit_the_second_period', 'monday_exit_grace_period',
			'tuesday_entering_the_first_period', 'tuesday_entering_the_second_period', 'tuesday_entering_the_first_period', 'tuesday_entry_grace_period', 'tuesday_exit_the_first_period', 'tuesday_exit_the_second_period', 'tuesday_exit_grace_period',
			'wednesday_entering_the_first_period', 'wednesday_entering_the_second_period', 'wednesday_entering_the_first_period', 'wednesday_entry_grace_period', 'wednesday_exit_the_first_period', 'wednesday_exit_the_second_period', 'wednesday_exit_grace_period',
			'thursday_entering_the_second_period', 'thursday_entering_the_first_period', 'thursday_entry_grace_period', 'thursday_exit_the_first_period', 'thursday_exit_the_second_period', 'thursday_exit_grace_period',
			'saturday_entering_the_second_period', 'saturday_entering_the_first_period', 'saturday_entry_grace_period', 'saturday_exit_the_first_period', 'saturday_exit_the_second_period', 'saturday_exit_grace_period',
			'friday_entering_the_first_period', 'friday_entering_the_second_period', 'friday_entering_the_first_period', 'friday_entry_grace_period', 'friday_exit_the_first_period', 'friday_exit_the_second_period', 'friday_exit_grace_period'
		];
		const marginTop10 = ['f1_h', 'f2_h', 'f3_h', 'f4_h', 'f5_h', 'f6_h', 'f7_h'];
		const marginTop35 = ['s1_h', 'g1_h', 's2_h', 'g2_h', 's3_h', 'g3_h', 's4_h', 'g4_h', 's5_h', 'g5_h', 's6_h', 'g6_h', 's7_h', 'g7_h'];
		toHide.forEach(field => {
			$(`div[data-fieldname="${field}"] .clearfix`).css('display', 'none');
			$(`div[data-fieldname="${field}"] .help-box`).css('display', 'none');
		})

		marginTop10.forEach(field => {
			$(`div[data-fieldname="${field}"]`).css('margin-top', '10px');
		})
		marginTop35.forEach(field => {
			$(`div[data-fieldname="${field}"]`).css('margin-top', '35px');
		})
	},
	fetch_employees_based_on: function (frm) {
		frm.set_value("based_on", "")
		frm.refresh_field("based_on")
		if (frm.doc.fetch_employees_based_on) {
			frm.fields_dict.based_on.set_label(__(frm.doc.fetch_employees_based_on));
		} else {
			frm.fields_dict.based_on.set_label(__("Based on"));
		}
	},
	fetch_employees: function (frm) {
		if (!frm.doc.based_on) {
			frappe.throw(__("Please Select " + frm.doc.fetch_employees_based_on))
		}
		// Get Employees Based on options
		let option = frm.doc.fetch_employees_based_on.toLowerCase()
		frappe.call({
			method: "mosyr.api.get_emps_based_on_option",
			args: {
				option: option,
				value: frm.doc.based_on
			},
			callback: (r) => {
				let current_emps_list = []
				if (frm.doc.shift_builder_employees) {
					frm.doc.shift_builder_employees.forEach(row => {
						current_emps_list.push(row.employee)
					});
				}
				if (r.message.emps_list.length > 0) {
					r.message.emps_list.forEach(row => {
						if (!current_emps_list.includes(row.name)) {
							frm.add_child("shift_builder_employees", { "employee": row.name, "employee_name": row.first_name });
						}
					});
				} else {
					let option_value = frm.doc.based_on
					frm.set_value("based_on", "")
					frm.refresh_field("based_on")
					frappe.msgprint(__(frm.doc.fetch_employees_based_on + ": " + "<b>" + option_value + "</b> doesn't have any employees"))
				}
				frm.refresh_field("shift_builder_employees")
			}
		})
	}
});


