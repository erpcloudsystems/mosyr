// Copyright (c) 2022, AnvilERP and contributors
// For license information, please see license.txt

frappe.ui.form.on("End Of Service", {
    employee: function (frm) {
        // Fetch employee list details
        if (cur_frm.doc.employee) {
            //   frm.add_fetch("employee", "date_of_joining", "date_of_joining");
            //frm.add_fetch("employee", "contract_end_date", "contract_end_date");
            get_salary();
            cur_frm.refresh();
        } else {
            cur_frm.doc.salary_detail = [];
            cur_frm.refresh();
        }
    },
    calculate_salary: function (frm) {
        // change salary_detail
        calculate_salary();
    },
    get_last_salary_slip: function (frm) {
        if (cur_frm.doc.employee) {
            get_salary();
        } else {
            frappe.msgprint(__("Please set Employee"));
        }
    },
    calculate: function (frm) {
        var reason_text = frm.doc.reason_of_end_contract;
        var reason_of_end_contract;
        if (reason_text == "انتهاء مدة العقد , أو باتفاق الطرفين على إنهاء العقد") {
            reason_of_end_contract = 1;
        } else if (reason_text == "فسخ العقد من قبل صاحب العمل") {
            reason_of_end_contract = 2;
        } else if (
            reason_text ==
            "(فسخ العقد من قبل صاحب العمل لأحد الحالات الواردة في المادة (80"
        ) {
            reason_of_end_contract = 3;
        } else if (reason_text == "ترك العامل العمل نتيجة لقوة قاهرة") {
            reason_of_end_contract = 4;
        } else if (
            reason_text ==
            "إنهاء العاملة لعقد العمل خلال ستة أشهر من عقد الزواج أو خلال ثلاثة أشهر من الوضع"
        ) {
            reason_of_end_contract = 5;
        } else if (
            reason_text == "(ترك العامل العمل لأحد الحالات الواردة في المادة (81"
        ) {
            reason_of_end_contract = 6;
        } else if (
            reason_text ==
            "فسخ العقد من قبل العامل أو ترك العامل العمل لغير الحالات الواردة في المادة (81)"
        ) {
            reason_of_end_contract = 7;
        } else if (reason_text == "استقالة العامل") {
            reason_of_end_contract = 8;
        }

        return frappe.call({
            method:
                "mosyr.mosyr.doctype.end_of_service.end_of_service.calculate_end_awards",
            args: {
                salary: frm.doc.salary,
                number_of_years: frm.doc.number_of_years,
                number_of_months: frm.doc.number_of_months,
                number_of_days: frm.doc.number_of_days,
                type_of_contract: frm.doc.type_of_contract,
                reason_of_end_contract: frm.doc.reason_of_end_contract,
                reason_of_end_contract: reason_of_end_contract,
            },
            callback: (r) => {
                cur_frm.doc.value = r.message["value"];
                if (r.message["value"] == "0") {
                    cur_frm.doc.note = "لا يستحق العامل مكافأة نهاية خدمة";
                } else {
                    cur_frm.doc.note = "";
                }

                cur_frm.refresh();
                frm.refresh();
            },
        });
    },
    date_of_joining: function (frm) {
        if (cur_frm.doc.date_of_joining && cur_frm.doc.contract_end_date) {
            calculate_years_months_days();
        }
    },
    contract_end_date: function (frm) {
        if (cur_frm.doc.date_of_joining && cur_frm.doc.contract_end_date) {
            calculate_years_months_days();
        }
    },
    calculate_length: function (frm) {
        calculate_years_months_days();
    },
});

var calculate_years_months_days = function () {
    if (!cur_frm.doc.date_of_joining) {
        frappe.msgprint(__("Please set Date Of Joining"));
        return;
    }

    if (!cur_frm.doc.contract_end_date) {
        frappe.msgprint(__("Please set Contract End Date"));
        return;
    }
    if (cur_frm.doc.contract_end_date <= cur_frm.doc.date_of_joining) {
        frappe.msgprint(__("Contract End Date Must Be After Date Of Joining"));
        return;
    }
    frappe.call({
        method:
            "mosyr.mosyr.doctype.end_of_service.end_of_service.get_diff_year_month_day",
        args: {
            date_of_joining: cur_frm.doc.date_of_joining,
            contract_end_date: cur_frm.doc.contract_end_date,
        },
        callback: (r) => {
            cur_frm.doc.number_of_years = r.message["years"];
            cur_frm.doc.number_of_months = r.message["months"];
            cur_frm.doc.number_of_days = r.message["days"];
            cur_frm.refresh();
            refresh_field("number_of_years");
            refresh_field("number_of_months");
            refresh_field("number_of_days");
        },
    });
};

var get_salary = function () {
    if (!cur_frm.doc.employee) {
        frappe.msgprint(__("Please set Employee"));
        return;
    }

    frappe.call({
        method:
            "mosyr.mosyr.doctype.end_of_service.end_of_service.get_salary",
        args: {
            employee: cur_frm.doc.employee,
        },
        callback: (r) => {
            if (r.message["salary"]) {
                cur_frm.doc.salary = r.message["salary"];
                refresh_field("salary");
                cur_frm.doc.salary_detail = [];
                var d = cur_frm.doc;
                for (var i = 0; i < r.message["earning"].length; i++) {
                    var new_row = frappe.model.add_child(
                        d,
                        "End Awards For Employee Salary",
                        "salary_detail"
                    );
                    new_row.salary_component =
                        r.message["earning"][i]["salary_component"];
                    new_row.amount = r.message["earning"][i]["amount"];
                }
                refresh_field("salary_detail");
            } else {
                frappe.msgprint(__("Employee not have full salary slip"));
            }
        },
    });
};

var calculate_salary = function () {
    amount = 0;
    for (var i = 0; i < cur_frm.doc.salary_detail.length; i++) {
        amount = amount + cur_frm.doc.salary_detail[i]["amount"];
    }
    cur_frm.doc.salary = amount;
    refresh_field("salary");
};
frappe.ui.form.on(
    "End Awards For Employee Salary",
    "amount",
    function (frm, cdt, cdn) {
        calculate_salary();
    }
);
frappe.ui.form.on(
    "End Awards For Employee Salary",
    "salary_component",
    function (frm, cdt, cdn) {
        calculate_salary();
    }
);
