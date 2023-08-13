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
						<tr>
							<td>Tessst</td>
							<td>Tessst</td>
							<td>Tessst</td>
							<td>Tessst</td>
							<td>Tessst</td>
							<td><button class="btn btn-primary btn-sm update-shift" data-item-code="xxxx">Update</button></td>
						</tr>
					</tbody>
				</table>
			</div>
		`);
	},
	refresh: function (frm) {
		frm.trigger("render_employees_shift_table")
		$(".update-shift").on("click", function (e) {
			console.log("78888888888888888888888888888888888888");
			var id = $(this).data('item-code');
			console.log('ID is ' + id);
		});
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
					$(`#employees_shift_table tbody`).html("")
					if (r.message.data.length > 0) {
						r.message.data.forEach(row => {
							if (row.emp_shifts.length > 1) {
								row.emp_shifts.forEach((d, idx) => {
									if(idx == 0) {
										console.log("MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM", idx);
										$(`#employees_shift_table tbody`).append(`
											<tr>
												<td rowspan="${row.emp_shift_count}" class="bold">${d.employee_name}</td>
												<td>${d.start_date}</td>
												<td>${d.end_date}</td>
												<td>${d.shift_type}</td>
												<td>${d.status}</td>
												<td><button class="btn btn-primary btn-sm update-shift" data-sha-id="${d.name}">Update</button></td>
											</tr>
										`)
									}else {
										console.log("iiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiii", idx);
										$(`#employees_shift_table tbody`).append(`
											<tr>
												<td>${d.start_date}</td>
												<td>${d.end_date}</td>
												<td>${d.shift_type}</td>
												<td>${d.status}</td>
												<td><button class="btn btn-primary btn-sm update-shift" data-sha-id="${d.name}">Update</button></td>
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
										<td><button class="btn btn-primary btn-sm update-shift" data-sha-id="${shift.name}">Update</button></td>
									</tr>
								`)
							}
						});
					}
				}
			}
		})
	}
});