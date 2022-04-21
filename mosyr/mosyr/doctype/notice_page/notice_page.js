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
				}
				if (result.ids.length){
					result.ids.forEach((row, idx) => {
						render_row(row, idx, "ids")
					})
				}
				if (result.passports.length){
					result.passports.forEach((row, idx) => {
						render_row(row, idx, "passports")
					})
				}
				if (result.insurances.length){
					result.insurances.forEach((row, idx) => {
						render_row(row, idx, "insurance")
					})
				}
			}
		})
	},
});

const render_row= function(row, idx, table) {
	let table_list = ["contracts", "ids", "passports", "insurance"]
	if (table_list.includes(table)) {
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
