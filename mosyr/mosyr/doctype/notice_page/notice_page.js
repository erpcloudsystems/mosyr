// Copyright (c) 2022, AnvilERP and contributors
// For license information, please see license.txt

frappe.ui.form.on('Notice Page', {
	refresh: function(frm) {
		frm.disable_save();
		let table_list = ["contracts", "ids", "passports", "insurance"]
		table_list.forEach((table) => {
			$(cur_frm.fields_dict[`${table}`].wrapper).html(`
				<div class="table_container">
					<table class="table  align-items-center mb-0" id=${table}>
						<thead>
						<tr>
							<th class="text-uppercase text-secondary text-xxs font-weight-bolder opacity-7">Employee</th>
							<th class="text-uppercase text-secondary text-xxs font-weight-bolder opacity-7">Department</th>
							<th class="text-uppercase text-secondary text-xxs font-weight-bolder opacity-7">Expiery Date</th>
						</tr>
						</thead>
						<tbody>
							<tr class="c-indicator">
								<td colspan="3" class="indicator-td">
									<div class="indicator_cont">
										<img src="/assets/mosyr/imgs/indicator.gif" />
									</div>
								</td>
							</tr>
						</tbody>
					</table>
				</div>
			`)
		})
		frappe.call({
			method:"get_date",
			doc: frm.doc,
			callback: function(r) {
				let result = r.message
				if(result.contracts.length){
					result.contracts.forEach((row, idx) => {
						render_row(row, idx, "contracts")
					})
				} else {
					render_mo_data_row("contracts")
				}
				if (result.ids.length){
					result.ids.forEach((row, idx) => {
						render_row(row, idx, "ids")
					})
				} else {
					render_mo_data_row("ids")
				}
				if (result.passports.length){
					result.passports.forEach((row, idx) => {
						render_row(row, idx, "passports")
					})
				} else {
					render_mo_data_row("passports")
				}
				if (result.insurances.length){
					result.insurances.forEach((row, idx) => {
						render_row(row, idx, "insurance")
					})
				} else {
					render_mo_data_row("insurance")
				}
			}
		})
	},
});

const render_row= function(row, idx, table) {
	let table_list = ["contracts", "ids", "passports", "insurance"]
	if (table_list.includes(table)) {
		$(`#${table} tbody tr.c-indicator`).remove()
		$(`#${table} tbody`).append(`
			<tr>
				<td id=${idx}>
					<span class="employee-img"></span>
					<a href='/app/employee/${row.employee}' target="_blank" rel="noopener noreferrer" class="text-xs"> ${row.employee_name}</a>
				</td>
				<td>${row.department}</td>
				<td>${row.expire_date}</td>
			</tr>
		`)
		if (row.employee_img) {
			$(`#${table} tbody tr #${idx} .employee-img`).append(`
				<img src="${row.employee_img}" alt="employee image" />
			`)
		} else {
			$(`#${table} tbody tr #${idx} .employee-img`).append(`
				<img src="/assets/mosyr/imgs/blank.png" alt="employee image" />
			`)
		}
	}
}

const render_mo_data_row = function(table) {
	$(`#${table} tbody tr.c-indicator`).remove()
	$(`#${table} tbody`).append(`
		<tr class="no-data">
			<td colspan="3" class="empty-td"> ${__('There are no Documents that will expire soon')} </td>
		</tr>
	`)
}