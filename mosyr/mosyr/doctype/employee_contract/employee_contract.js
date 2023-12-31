// Copyright (c) 2022, AnvilERP and contributors
// For license information, please see license.txt

frappe.ui.form.on('Employee Contract', {
    refresh: function (frm) {
        if (frm.doc.docstatus == 1 && frm.doc.status == "Approved" && frm.doc.contract_status == "Valid") {
            frm.add_custom_button(__("Prepare Salary Structuer"), () => {
                frappe.confirm("This will Create Salary Structure and Assign it to Employee,", () => {
                    frappe.call({
                        method: 'create_employee_salary_structure',
                        doc: frm.doc,
                        callback: (r) => {
                            if(r && r.mesasge){
                                frappe.msgprint(__("Salary Structure Created and Assigned to Employee")+` ${r.mesasge.ssa}`)
                            }
                         }
                    })
                })
            })
        }
    },
    after_workflow_action: function(frm){
        if(frm.doc.status == "Approved"){frm.reload_doc()}
    }
});