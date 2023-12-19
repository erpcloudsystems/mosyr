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
		},
		{
			fieldname: "shift",
			label: __("Shift"),
			fieldtype: "Link",
			options:"Shift Type",
		},
		{
			fieldname: "department",
			label: __("Department"),
			fieldtype: "Link",
			options:"Department",
		},
	],
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
