// Copyright (c) 2023, AnvilERP and contributors
// For license information, please see license.txt

frappe.ui.form.on('Employee Shift Change Tool', {
	setup: function (frm) {
		$(cur_frm.fields_dict["employees_shift_table"].wrapper).html(`
			<div class="table_container">
				<table class="table table-bordered borderless" id="employees_shift_table"}>
					<thead>
					<tr>
						<th width="25%" class="th_borderless">Employee</th>
						<th width="13%" class="th_borderless">From Date</th>
						<th width="13%" class="th_borderless">To Date</th>
						<th width="15%" class="th_borderless">Shift Name</th>
						<th width="14%" class="th_borderless">Status</th>
						<th width="20%" class="th_borderless">Actions</th>
					</tr>
					</thead>
					<tbody>
					</tbody>
				</table>
			</div>
		`);
	},
	refresh: function (frm) {
		frm.trigger("render_employees_shift_table")
	},
	render_employees_shift_table: function (frm) {
		frappe.call({
			method: "fetch_employees_shift",
			doc: frm.doc,
			args: {
				company: frm.doc.company
			},
			callback: function (r) {
				if (!r.exc) {
					// $(`#employees_shift_table tbody`).html("")
					if (r.message.data.length > 0) {
						r.message.data.forEach(row => {
							if (row.emp_shifts.length > 1) {
								row.emp_shifts.forEach((d, idx) => {
									if (idx == 0) {
										$(`#employees_shift_table tbody`).append(`
											<tr>
												<td rowspan="${row.emp_shift_count}" class="bold">${d.employee_name}</td>
												<td>${d.start_date}</td>
												<td>${d.end_date}</td>
												<td>${d.shift_type}</td>
												<td>${d.status}</td>
												<td><button class="btn btn-primary btn-sm update-shift" data-employee="${d.employee}" data-sha-id="${d.name}">Update</button></td>
											</tr>
										`)
									} else {
										$(`#employees_shift_table tbody`).append(`
											<tr>
												<td>${d.start_date}</td>
												<td>${d.end_date}</td>
												<td>${d.shift_type}</td>
												<td>${d.status}</td>
												<td><button class="btn btn-primary btn-sm update-shift" data-employee="${d.employee}" data-sha-id="${d.name}">Update</button></td>
											</tr>
										`)
									}
								});
							} else {
								let shift = row.emp_shifts[0]
								$(`#employees_shift_table tbody`).append(`
									<tr>
										<td class="bold">${shift.employee_name}</td>
										<td>${shift.start_date}</td>
										<td>${shift.end_date}</td>
										<td>${shift.shift_type}</td>
										<td>${shift.status}</td>
										<td><button class="btn btn-primary btn-sm update-shift" data-employee="${shift.employee}" data-sha-id="${shift.name}">Update</button></td>
									</tr>
								`)
							}
						});
					}
					$(".update-shift").on("click", function (e) {
						var shift_id = $(this).data('sha-id');
						var employee = $(this).data('employee');
						frm.events.open_change_shift_dialoge(frm, employee);
					});
				}
			}
		})
	},
	open_change_shift_dialoge: function (frm, employee) {
		var d = new frappe.ui.Dialog({
			title: __('Select New Shift'),
			fields: [
				{
					"label": "Shift",
					"fieldname": "shift_name",
					"fieldtype": "Link",
					"options": "Shift Type",
					"reqd": 1
				},
				{
					"label": "Start Date",
					"fieldname": "start_date",
					"fieldtype": "Date",
					"reqd": 1
				},
				{
					"label": "End Date",
					"fieldname": "end_date",
					"fieldtype": "Date",
					"reqd": 1
				},
				{
					"label": "Recalculate the previous period",
					"fieldname": "recalculate_period",
					"fieldtype": "Check",
					"defualt": 0
				}
			],
			primary_action: function () {
				var data = d.get_values();
				frappe.call({
					method: "update_employee_shift_and_recalculate_period",
					doc: frm.doc,
					args: {
						employee: employee,
						new_shift: data.shift_name,
						start_date: data.start_date,
						end_date: data.end_date,
						recalculate_period: data.recalculate_period
					},
					callback: function (r) {
						if (!r.exc) {
							if (r.message) {
								cur_frm.reload_doc();
							}
							d.hide();
						}
					}
				});
			},
			primary_action_label: __('Save')
		});
		d.show();
	}
});