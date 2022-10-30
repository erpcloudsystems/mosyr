/**
 * frappe.views.ReportView
 */
//  import DataTable from 'frappe-datatable';

//  frappe.provide('frappe.views');

let d = new Date();
let monthNames=  [
	'January',
	'February',
	'March',
	'April',
	'May',
	'June',
	'July',
	'August',
	'September',
	'October',
	'November',
	'December'
]


frappe.query_reports["Files in Saudi banks format"] = {
	
	onload: function(report) {
			report.page.add_inner_button(__("Export For Bank"), function() {
				if (frappe.model.can_export(report.report_name)) {
					frappe.call({
						method: "mosyr.mosyr.report.files_in_saudi_banks_format.files_in_saudi_banks_format.get_bank",
						args:{
							filters:frappe.query_reports['Files in Saudi banks format'].filters
						},
						callback: function(r) {
							if(r.message) {
								let	bank_name = r.message[0]
								let	disbursement_type = r.message[1]
								// CSV
								if (bank_name === "Al Inma Bank") {
									let file_format = 'CSV'
									report.make_access_log('Export', file_format);
									const data = report.get_data_for_csv(include_indentation=false);
									if (disbursement_type === "Payroll"){
										data[0][0]="0"
										data[0] = data[0].slice(0,10)
									}
									else if(disbursement_type === 'WPS'){
										data[0] = data[0].slice(0,11)
									}
									frappe.tools.downloadify(data, null, bank_name.replaceAll(" ","_"));
								}
								else if (bank_name === "The National Commercial Bank"){
									let file_format = 'CSV'
									report.make_access_log('Export', file_format);
									const data = report.get_data_for_csv(include_indentation=false);
									frappe.tools.downloadify(data, null, bank_name.replaceAll(" ","_"));
								}
								// Excel
								else if (bank_name === "Al Araby Bank" && disbursement_type == 'WPS') {
									let file_format = 'Excel'
									let filters = report.get_filter_values(true);
									if (frappe.urllib.get_dict("prepared_report_name")) {
										filters = Object.assign(frappe.urllib.get_dict("prepared_report_name"), filters);
									}
									const visible_idx = report.datatable.bodyRenderer.visibleRowIndices;
									if (visible_idx.length + 1 === report.data.length) {
										visible_idx.push(visible_idx.length);
									}
									
									const args = {
										cmd: 'mosyr.mosyr.report.files_in_saudi_banks_format.files_in_saudi_banks_format.export_query',
										report_name: report.report_name,
										custom_columns: report.custom_columns.length? report.custom_columns: [],
										file_format_type: file_format,
										filters: filters,
										visible_idx,
										include_indentation:false,
									};
					
									open_url_post(frappe.request.url, args);
								}
								// Txt
								else if ((bank_name === "Riyadh Bank" && disbursement_type === "WPS") || 
										 (bank_name === "Samba Financial Group" && disbursement_type === "WPS")||
										 (bank_name === "Al Rajhi Bank")
										){
											let file_format = 'Txt'
											let filters = report.get_filter_values(true);
											if (frappe.urllib.get_dict("prepared_report_name")) {
												filters = Object.assign(frappe.urllib.get_dict("prepared_report_name"), filters);
											}
							
											const visible_idx = report.datatable.bodyRenderer.visibleRowIndices;
											if (visible_idx.length + 1 === report.data.length) {
												visible_idx.push(visible_idx.length);
											}
											
											const args = {
												cmd: 'mosyr.mosyr.report.files_in_saudi_banks_format.files_in_saudi_banks_format.export_query',
												report_name: report.report_name,
												custom_columns: report.custom_columns.length? report.custom_columns: [],
												file_format_type: file_format,
												filters: filters,
												visible_idx,
												include_indentation:false,
											};
							
											open_url_post(frappe.request.url, args);
										}
							}
						}
					});
			}
		})
    },
	filters: [
		{
			"fieldname": "bank",
			"label": __("Bank"),
			"fieldtype": "Link",
			"width": "80",
			"options": "Bank",
		},
		{
			"fieldname": "month",
			"label": __("Month"),
			"fieldtype": "Select",
			"width": "80",
			'options': [
                '',
				'January',
				'February',
				'March',
				'April',
				'May',
				'June',
				'July',
				'August',
				'September',
				'October',
				'November',
				'December'
            ],
			'default': monthNames[d.getMonth()]
		},
		{
			"fieldname": "year",
			"label": __("Year"),
			"fieldtype": "Link",
			"width": "80",
			"options": "Fiscal Year",
			'default': d.getFullYear()
		},
		{
			"fieldname": "company",
			"label": __("Company"),
			"fieldtype": "Link",
			"width": "80",
			"options": "Company",
			'default': frappe.defaults.get_user_default("Company")
		},
	],

	"get_data_for_txt":function(report ,include_indentation) {
		const rows = report.datatable.bodyRenderer.visibleRows;
		if (report.raw_data.add_total_row) {
			rows.push(report.datatable.bodyRenderer.getTotalRow());
		}
		return rows.map(row => {
			const standard_column_count = report.datatable.datamanager.getStandardColumnCount();
			return row
				.slice(standard_column_count)
				.map((cell, i) => {
					if (cell.column.fieldtype === "Duration") {
						cell.content = frappe.utils.get_formatted_duration(cell.content);
					}
					if (include_indentation && i===0) {
						cell.content = '   '.repeat(row.meta.indent) + (cell.content || '');
					}
					return cell.content || '';
				});
		});
}}
