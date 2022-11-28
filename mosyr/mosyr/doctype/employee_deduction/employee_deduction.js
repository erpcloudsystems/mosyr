// Copyright (c) 2022, AnvilERP and contributors
// For license information, please see license.txt

frappe.ui.form.on("Employee Deduction", {
  setup: function (frm) {
    if (!frm.doc.date) {
      frm.doc.date = frappe.datetime.get_today();
    }
  },
  employee: function (frm) {
    if (frm.doc.employee != "") {
      frappe.call({
        method: "get_salary_per_day",
        doc: frm.doc,
        args: {
          employee: frm.doc.employee,
        },
        callback: function (r) {
          const daily_rate = flt(r.message);
          frm.set_value("daily_rate", daily_rate);
          frm.refresh_field("daily_rate");
        },
      });
    } else {
      frm.set_value("daily_rate", 0);
      frm.refresh_field("daily_rate");
    }
  },
  days: function (frm) {
    frm.trigger("calc_amount");
  },
  hours: function (frm) {
    console.log("444");
    frm.trigger("calc_amount");
  },
  minutes: function (frm) {
    frm.trigger("calc_amount");
  },
  calc_amount: function (frm) {
    const daily_rate = flt(frm.doc.daily_rate);
    const days = cint(frm.doc.days);
    const hours = cint(frm.doc.hours);
    const minutes = cint(frm.doc.minutes);

    let amt =
      flt(days * daily_rate) +
      flt((hours * daily_rate) / 24) +
      flt((minutes * daily_rate) / (24 * 60));
    frm.set_value("amount", amt);
    frm.refresh_field("amount");
  },
});
