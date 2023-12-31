// Copyright (c) 2023, AnvilERP and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Summerize Employee Attendance"] = {
	"filters": [
		{
			fieldname: "from_date",
			label: __("From Date"),
			fieldtype: "Date",
			reqd: 1,
			default: frappe.datetime.add_months(frappe.datetime.get_today(), -1)
		},
		{
			fieldname: "to_date",
			label: __("To Date"),
			fieldtype: "Date",
			reqd: 1,
			default: frappe.datetime.get_today()
		},
		{
			fieldname: "employee",
			label: __("Employee"),
			fieldtype: "Link",
			options:"Employee",
			// hidden:1

		},
		{
			fieldname: "shift",
			label: __("Shift"),
			fieldtype: "Link",
			options:"Shift Type",
			hidden:1

		},
		{
			fieldname: "department",
			label: __("Department"),
			fieldtype: "Link",
			options:"Department",
			// hidden:1
		},
	],
	onload: function(){
		$('.custom-actions').append(`<button id="toggleSidebarBtn" class="btn btn-default btn-sm">Toggle Screen</button>`);

		function toggleSidebar() {
			const urlParams = new URLSearchParams(window.location.search);
			const queryParamValue = urlParams.get('sidebar');

			if (queryParamValue === 'no') {
				$("#mosyrsidebar").addClass('d-none');
				$('.page-body').addClass('container-fluid');
				$('.page-body').removeClass('container');;
				$(".layout-page").addClass('pl-0')
			} else {
				$(".layout-page").removeClass('pl-0')
				$("#mosyrsidebar").removeClass('d-none');
				$('.page-body').removeClass('container-fluid');
				$('.page-body').addClass('container');
			}
		}

		toggleSidebar();

		$('#toggleSidebarBtn').on('click', function () {
			const urlParams = new URLSearchParams(window.location.search);
			const queryParamValue = urlParams.get('sidebar');

			if (queryParamValue === 'no') {
				urlParams.set('sidebar', 'yes');
			} else {
				urlParams.set('sidebar', 'no');
			}

			const newUrl = `${window.location.pathname}?${urlParams.toString()}${window.location.hash}`;
			window.history.replaceState({}, '', newUrl);

			toggleSidebar();
			$('[data-original-title="Refresh"]').click()
	});
	},
	"formatter": function (value, row, column, data, default_formatter) {
		value = default_formatter(value, row, column, data);

		if (column.fieldname == "status" && data && data.status == "Present") {
			value = "<span style='color:green'>" + value + "</span>";
		}
		else if (column.fieldname == "status" && data && data.status =="Absent") {
			value = "<span style='color:red'>" + value + "</span>";
		}

		if (column.fieldname == "lates" && data && (data.lates != "0:0:0")) {
				value = "<span style='color:red'>" + value + "</span>";
			}

		if (column.fieldname == "early_leave" && data && data.early_leave != "0:0:0") {
				value = "<span style='color:red'>" + value + "</span>";
		}

		if (column.fieldname == "overtime" && data && data.overtime != "0:0:0") {
			value = "<span style='color:green'>" + value + "</span>";
		}
		if (column.fieldname == "early_come" && data && data.early_come != "0:0:0") {
			value = "<span style='color:green'>" + value + "</span>";
		}

		if (column.fieldname == "early_come" && data && data.early_come != "0:0:0") {
			value = "<span style='color:green'>" + value + "</span>";
		}
		if (column.fieldname == "count_absent" && data && value > 0 ) {
			value = "<span style='color:red'>" + value + "</span>";
		}
		if (column.fieldname == "count_present" && data && value > 0 ) {
			value = "<span style='color:green'>" + value + "</span>";
		}
		if ((column.fieldname == "missed_finger_print_entry" && data && value > 0) ) {
			value = "<span style='color:red'>" + value + "</span>";
		}
		if ((column.fieldname == "missed_finger_print" && data && value > 0) ) {
			value = "<span style='color:red'>" + value + "</span>";
		}
		if ((column.fieldname == "records_with_early_leave" && data && value > 0) ) {
			value = "<span style='color:red'>" + value + "</span>";
		}
		if ((column.fieldname == "records_with_early_come" && data && value > 0) ) {
			value = "<span style='color:green'>" + value + "</span>";
		}

		if ((column.fieldname == "records_with_lates" && data && value > 0 ) ) {
			value = "<span style='color:red'>" + value + "</span>";
		}
		if ((column.fieldname == "records_with_overtime" && data && value > 0) ) {
			value = "<span style='color:green'>" + value + "</span>";
		}
		return value;
	}
};
