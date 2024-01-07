// Copyright (c) 2023, AnvilERP and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Daily Attendance"] = {
	
	"filters": [
		{
			fieldname: "from_date",
			label: __("Date"),
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

// Function to toggle the sidebar visibility
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

// Initial toggle based on the query parameter
toggleSidebar();

// Toggle sidebar when the button is clicked
$('#toggleSidebarBtn').on('click', function () {
    const urlParams = new URLSearchParams(window.location.search);
    const queryParamValue = urlParams.get('sidebar');

    // Toggle the query parameter value
    if (queryParamValue === 'no') {
        urlParams.set('sidebar', 'yes');
    } else {
        urlParams.set('sidebar', 'no');
    }

    // Update the URL with the new query parameter
    const newUrl = `${window.location.pathname}?${urlParams.toString()}${window.location.hash}`;
    window.history.replaceState({}, '', newUrl);

    // Toggle the sidebar visibility
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

		if (column.fieldname == "lates" && data && data.lates != "0:0:0") {
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

		return value;
	}
};
