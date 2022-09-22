// Copyright (c) 2022, AnvilERP and contributors
// For license information, please see license.txt

frappe.ui.form.on('Lateness Permission', {
    setup: function (frm) {
        frm.set_query("approver", function () {
            return {
                query: "erpnext.hr.doctype.department_approver.department_approver.get_approvers",
                filters: {
                    employee: frm.doc.employee,
                    doctype: "Shift Request",
                }
            };
        });
        frm.set_query("employee", erpnext.queries.employee);
    },
});
