// Copyright (c) 2022, AnvilERP and contributors
// For license information, please see license.txt
/* eslint-disable */

const default_url = "/api/method/mosyr.mosyr.report.employee_attendance_sheet.employee_attendance_sheet.export_report"
const render_pdf = function (url, filters) {
    //Create a form to place the HTML content
    var formData = new FormData();

    //Push the HTML content into an element
    const report_name = filters.report_name;
    const orientation = filters.orientation;
    // filters = JSON.stringify(filters)
    formData.append("filters", JSON.stringify(filters));
    if (orientation) {
        formData.append("orientation", filters.orientation);
    }
    var blob = new Blob([], { type: "text/xml" });
    formData.append("blob", blob);

    var xhr = new XMLHttpRequest();
    xhr.open("POST", url || '/api/method/frappe.utils.print_format.report_to_pdf');
    xhr.setRequestHeader("X-Frappe-CSRF-Token", frappe.csrf_token);
    // xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    xhr.responseType = "arraybuffer";

    xhr.onload = function (success) {
        if (this.status === 200) {
            var blob = new Blob([success.currentTarget.response], { type: "application/pdf" });
            var objectUrl = URL.createObjectURL(blob);

            // Create a hidden a tag to force set report name
            // https://stackoverflow.com/questions/19327749/javascript-blob-filename-without-link
            let hidden_a_tag = document.createElement("a");
            document.body.appendChild(hidden_a_tag);
            hidden_a_tag.style = "display: none";
            hidden_a_tag.href = objectUrl;
            hidden_a_tag.download = report_name || "report.pdf";

            // Open report in a new window
            hidden_a_tag.click();
            window.URL.revokeObjectURL(objectUrl);
        }
    };
    xhr.send(formData);
}
frappe.query_reports["Employee Attendance Sheet"] = {
    onload: function (report) {
        // if (frappe.model.can_export(report.report_name)) {
            var company = frappe.query_report.get_filter_value("company")
            // console.log(frappe.query_report.get_filter("company"));
            report.page.add_inner_button(__("Summary Attendance"), function () {
                var d = new frappe.ui.Dialog({
                    title: __("Export Summary Attendance"),
                    fields: [
                        {
                            "label": __("From Date"),
                            "fieldname": "from_date",
                            "fieldtype": "Date",
                            "reqd": 1,
                            "default": frappe.datetime.month_start()
                        },
                        {
                            "fieldname": "cb1",
                            "fieldtype": "Column Break",
                        },
                        {
                            "label": __("To Date"),
                            "fieldname": "to_date",
                            "fieldtype": "Date",
                            "reqd": 1,
                            "default": frappe.datetime.month_end()
                        },
                        {
                            "fieldname": "sb1",
                            "fieldtype": "Section Break",
                        },
                        {
                            "label": __("Company"),
                            "fieldname": "company",
                            "fieldtype": "Link",
                            "options": "Company",
                            "default": frappe.query_report.get_filter_value("company"),
                            "reqd": 1,
                            onchange() {
                                company = d.get_value('company') || null;
                            }
                        },
                        {
                            "label": `${__("Employees")} (${__("Optional")})`,
                            "fieldname": "employees",
                            "fieldtype": "Table MultiSelect",
                            "options": "Mosyr Employee Multiselect",
                            get_query: () => {
                                return {
                                    filters: {
                                        "company": frappe.query_report.get_filter_value("company")
                                    }
                                };
                            }
                        },
                    ],
                    primary_action: function () {
                        const from_date = d.get_values().from_date ? d.get_values().from_date + '_' : '';
                        const to_date = d.get_values().to_date ? d.get_values().to_date + '_' : '';

                        let filters = {
                            "report_type": "Summary Attendance",
                            "report_name": `${from_date}${to_date}summary_attendance.pdf`,
                            "employees": [],
                            ...d.get_values()
                        }

                        render_pdf(default_url, filters)
                    },
                    primary_action_label: __("Export")
                });
                d.show();
            }, __("Export"));

            report.page.add_inner_button(__("Monthly Attendance"), function () {
                var d = new frappe.ui.Dialog({
                    title: __("Export Monthly Attendance"),
                    fields: [
                        {
                            "label": __("From Date"),
                            "fieldname": "from_date",
                            "fieldtype": "Date",
                            "reqd": 1,
                            "default": frappe.datetime.month_start()
                        },
                        {
                            "fieldname": "cb1",
                            "fieldtype": "Column Break",
                        },
                        {
                            "label": __("To Date"),
                            "fieldname": "to_date",
                            "fieldtype": "Date",
                            "reqd": 1,
                            "default": frappe.datetime.month_end()
                        },
                        {
                            "fieldname": "sb1",
                            "fieldtype": "Section Break",
                        },
                        {
                            "label": __("Company"),
                            "fieldname": "company",
                            "fieldtype": "Link",
                            "options": "Company",
                            "default": company,
                            "reqd": 1,
                            onchange() {
                                company = d.get_value('company') || null;
                            }
                        },
                        {
                            "label": `${__("Employees")} (${__("Optional")})`,
                            "fieldname": "employees",
                            "fieldtype": "Table MultiSelect",
                            "options": "Mosyr Employee Multiselect",
                            get_query: () => {
                                return {
                                    filters: {
                                        "company": company
                                    }
                                };
                            }
                        }
                    ],
                    primary_action: function () {
                        const from_date = d.get_values().from_date ? d.get_values().from_date + '_' : '';
                        const to_date = d.get_values().to_date ? d.get_values().to_date + '_' : '';
                        let filters = {
                            "report_type": "Monthly Attendance",
                            "report_name": `${from_date}${to_date}monthly_attendance.pdf`,
                            "employees": [],
                            ...d.get_values()
                        }
                        render_pdf(default_url, filters)
                    },
                    primary_action_label: __("Export")
                });
                d.show();
            }, __("Export"));

            report.page.add_inner_button(__("Daily Attendance"), function () {
                var d = new frappe.ui.Dialog({
                    title: __("Export for Day"),
                    fields: [
                        {
                            "label": __("Select Date"),
                            "fieldname": "from_date",
                            "fieldtype": "Date",
                            "reqd": 1,
                            "default": frappe.datetime.now_date(),
                        },
                        {
                            "fieldname": "cb1",
                            "fieldtype": "Column Break",
                        },
                        {
                            "label": __("Company"),
                            "fieldname": "company",
                            "fieldtype": "Link",
                            "options": "Company",
                            "default": company,
                            "reqd": 1,
                            onchange() {
                                company = d.get_value('company') || null;
                            }
                        },
                        {
                            "label": `${__("Employees")} (${__("Optional")})`,
                            "fieldname": "employees",
                            "fieldtype": "Table MultiSelect",
                            "options": "Mosyr Employee Multiselect",
                            get_query: () => {
                                return {
                                    filters: {
                                        "company": company
                                    }
                                };
                            }
                        }
                    ],
                    primary_action: function () {
                        const from_date = d.get_values().from_date ? d.get_values().from_date + '_' : '';
                        let filters = {
                            "report_type": "Daily Attendance",
                            "report_name": `${from_date}daily_attendance.pdf`,
                            "employees": [],
                            ...d.get_values()
                        }
                        render_pdf(default_url, filters)
                    },
                    primary_action_label: __("Export")
                });
                d.show();
            }, __("Export"));
        // }
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
                return {
                    filters: {
                        "company": company
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
