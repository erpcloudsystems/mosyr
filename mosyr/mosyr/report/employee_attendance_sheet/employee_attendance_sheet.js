// Copyright (c) 2022, AnvilERP and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Employee Attendance Sheet"] = {
    onload: function (report) {
        report.page.add_inner_button(__("Export For Employee"), function () {
            if (frappe.model.can_export(report.report_name)) {
                var d = new frappe.ui.Dialog({
                    title: __('Choose Employee'),
                    fields: [
                        {
                            "label": "Employee",
                            "fieldname": "employee",
                            "fieldtype": "Link",
                            "options": "Employee",
                            "reqd": 1,
                        },
                        {
                            "label": "From Date",
                            "fieldname": "from",
                            "fieldtype": "Date",
                            "reqd": 1,
                        },
                        {
                            "label": "To Date",
                            "fieldname": "to",
                            "fieldtype": "Date",
                            "reqd": 1,
                        }
                    ],
                    primary_action: function () {
                        d.hide()
                        var data = d.get_values();
                        const args = {
                            cmd: 'mosyr.mosyr.report.employee_attendance_sheet.employee_attendance_sheet.export_query',
                            data: data
                        };
                        open_url_post(frappe.request.url, args);
                    },
                    primary_action_label: __('Export')
                });
                d.show();

            }
        })
        return frappe.call({
            method: "erpnext.hr.report.monthly_attendance_sheet.monthly_attendance_sheet.get_attendance_years",
            callback: function (r) {
                var year_filter = frappe.query_report.get_filter('year');
                year_filter.df.options = r.message;
                year_filter.df.default = r.message.split("\n")[0];
                year_filter.refresh();
                year_filter.set_input(year_filter.df.default);
            }
        });
    },
    "filters": [
        {
            "fieldname": "from_date",
            "label": __("From"),
            "fieldtype": "Date",
            "default": frappe.datetime.get_today(),
			"reqd": 1
        },
        {
            "fieldname": "to_date",
            "label": __("To"),
            "fieldtype": "Date",
            "default": frappe.datetime.get_today(),
			"reqd": 1
        },
        {
            "fieldname": "employee",
            "label": __("Employee"),
            "fieldtype": "Link",
            "options": "Employee",
            get_query: () => {
                var company = frappe.query_report.get_filter_value('company');
                return {
                    filters: {
                        'company': company
                    }
                };
            }
        },
        {
            "fieldname": "company",
            "label": __("Company"),
            "fieldtype": "Link",
            "options": "Company",
            "default": frappe.defaults.get_user_default("Company"),
            "reqd": 1
        }
    ],
};
