// Copyright (c) 2022, AnvilERP and contributors
// For license information, please see license.txt

frappe.ui.form.on('Payroll Register Tool', {
	onload: function (frm) {
		if (frm.is_new()) {
			frm.set_value('from_date', frappe.datetime.now_date())
		}
		frm.set_query('employee', 'employees', doc => {
			return {
				filters: {
					"company": doc.company,
					"status": "Active"
				}
			}
		});
		frm.set_query('department', doc => {
			return {
				filters: {
					"company": doc.company
				}
			}
		});
		frm.set_query('salary_component', 'earnings', (doc) => {
			return {
				filters: {
					"type": "Earning",
					"disabled": 0
				}
			}
		});
		frm.set_query('salary_component', 'deductions', (doc) => {
			return {
				filters: {
					"type": "Deduction",
					"disabled": 0
				}
			}
		});
	},
	company: function (frm) {
		['department', 'branch', 'designation', 'employees'].forEach(fieldname => {
			frm.set_value(fieldname, '');
			frm.refresh_field(fieldname)
		});

		if (frm.doc.company) {
			frm.trigger('show_employees')
		}
	},
	show_employees: function (frm) {
		let args = {}
		if (frm.doc.company) {
			args = {
				...args,
				"company": frm.doc.company
			};
		}
		if (frm.doc.department) {
			args = {
				...args,
				"department": frm.doc.department
			};
		}
		if (frm.doc.branch) {
			args = {
				...args,
				"branch": frm.doc.branch
			};
		}
		if (frm.doc.designation) {
			args = {
				...args,
				"designation": frm.doc.designation
			};
		}
		if (args && args.company) {
			frappe.call({
				method: "fetch_employees",
				doc: frm.doc,
				args: args,
				callback: function (r) {
					if (r && r.message) {
						frm.clear_table('employees');
						(r.message || []).forEach(row => {
							const new_row = frm.add_child('employees')
							new_row.employee = row.name
							new_row.employee_name = row.employee_name
						})
						frm.refresh_field('employees')
					} else {
						let msg_conds = ''
						for (const [key, value] of Object.entries(args)) {
							msg_conds += `<li><b>${capitalize(key)} : ${value}</b></li>`
						}
						frappe.msgprint(__(`No Active Employee Found based on`) + `<ul>${msg_conds}</ul>`)
					}
				},
				freeze: true,
				freeze_msg: __("Please Wait")
			})
		} else {
			frappe.throw(__("you must select company at least") + ".")
		}
	},

});

const capitalize = word => {
	const lower = `${word}`.toLowerCase();
	return __(`${word}`.charAt(0).toUpperCase() + lower.slice(1));
}
