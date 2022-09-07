// Copyright (c) 2022, AnvilERP and contributors
// For license information, please see license.txt

frappe.ui.form.on('Payroll Register Tool', {
	onload: function (frm) {
		frm.disable_save()
		frm.set_value('company', '')
		frm.set_value('from_date', frappe.datetime.now_date())
		frm.set_query('employee', 'employees', (doc) => {
			return {
				filters: {
					"company": doc.company,
					"status": "Active"
				}
			}
		})
		frm.set_query('department', (doc) => {
			return {
				filters: {
					"company": doc.company
				}
			}
		})
		frm.set_query('salary_component', 'earnings', (doc) => {
			return {
				filters: {
					"type": "Earning",
					"disabled": 0
				}
			}
		})
		frm.set_query('salary_component', 'deductions', (doc) => {
			return {
				filters: {
					"type": "Deduction",
					"disabled": 0
				}
			}
		})
	},
	refresh: function (frm) {
		frm.page.clear_primary_action();
	},
	prepare_salary_structures: function (frm) {
		if (!frm.doc.from_date) {
			frappe.throw(__("From Date is mandatory to prepare Salary Structures") + ".")
			return
		}
		if (!frm.doc.company) {
			frappe.throw(__("Company is mandatory to prepare Salary Structures") + ".")
			return
		}

		if ((frm.doc.employees || []).length > 0) {
			let args = {}

			if (frm.doc.company) {
				args = {
					...args,
					"company": frm.doc.company
				};
			} else {
				frappe.throw(__("Company is mandatory to prepare Salary Structures") + ".")
				return
			}

			if (frm.doc.from_date) {
				args = {
					...args,
					"from_date": frm.doc.from_date
				};
			} else {
				frappe.throw(__("From Date is mandatory to prepare Salary Structures") + ".")
				return
			}
			if (frm.doc.currency) { args = { ...args, "currency": frm.doc.currency }; }
			if (frm.doc.payroll_frequency) { args = { ...args, "frequency": frm.doc.payroll_frequency || "Monthly" }; }			
			if (frm.doc.base) { args = { ...args, "base": frm.doc.base || "0" }; }
			if (frm.doc.variables) { args = { ...args, "variables": frm.doc.variables || "0" }; }
			if (frm.doc.salary_component) { args = { ...args, "ts_component": frm.doc.salary_component }; }
			if (frm.doc.hour_rate) { args = { ...args, "hour_rate": frm.doc.hour_rate }; }
			if (frm.doc.encashment_per_day) { args = { ...args, "encashment_per_day": frm.doc.leave_encashment_amount_per_day }; }
			if (frm.doc.max_benefits) { args = { ...args, "max_benefits": frm.doc.max_benefits }; }
			args = { ...args, "based_on_timesheet": frm.doc.salary_slip_based_on_timesheet == 1 ? 1 : 0 };
			let employees = (frm.doc.employees || []).map((data) => {
				return {
					'employee_name': data.employee,
				}
			})

			let earnings = (frm.doc.earnings || []).map((data) => {
				return data
			})

			let deductions = (frm.doc.deductions || []).map((data) => {
				return data
			})
			args = {
				...args,
				"employees": employees || [],
				"earnings": earnings || [],
				"deductions": deductions || []
			};
			if (args && args.company) {
				frappe.call({
					method: "prepare_salary_structures",
					doc: frm.doc,
					args: args,
					callback: function (r) {
						// if (r && r.status) { frm.reload_doc() }
					},
					freeze: true,
					freeze_message: __("Please Wait")
				})
			}
			else {
				frappe.throw(__("you must select company at least") + ".")
			}
		} else {
			frappe.throw(__("Can not prepare Salary Structures for 0 Employee") + ".")
		}
	},
	company: function (frm) {
		frm.page.clear_primary_action();

		frm.set_value('department', '')
		frm.set_value('branch', '')
		frm.set_value('designation', '')
		frm.clear_table('employees')

		frm.refresh_field('department')
		frm.refresh_field('branch')
		frm.refresh_field('designation')
		frm.refresh_field('employees')
		if (frm.doc.company) {
			frm.page.set_primary_action(__("Prepare Salary Structures"), function () {
				frm.trigger('prepare_salary_structures');
			});
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
						frappe.msgprint(`No Active Employee Found based on ${msg_conds}`)
						frm.page.clear_primary_action();
					}
				},
				freeze: true,
				freeze_msg: __("Please Wait")
			})
		} else {
			frappe.throw(__("you must select company at least") + ".")
			frm.page.clear_primary_action();
		}
	},

});

function capitalize(word) {
	const lower = `${word}`.toLowerCase();
	return `${word}`.charAt(0).toUpperCase() + lower.slice(1);
}