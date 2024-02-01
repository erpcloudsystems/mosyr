// Copyright (c) 2019, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Department', {
    
    refresh: function (frm) {
        const tables = [
            "leave_approvers",
            "expense_approvers",
            "shift_request_approver",
            "contact_details_approver",
            "educational_qualification_approver",
            "emergency_contact_approver",
            "health_insurance_approver",
            "personal_details_approver",
            "salary_details_approver",
            "exit_permission_approver",
            "attendance_request_approver",
            "compensatory_leave_request_approver",
            "travel_request_approver",
            "vehicle_service_approver",
            "letter_approver",
            "loan_approver",
        ]
        console.log(tables.length)

        tables.forEach(table =>{
              
            frm.fields_dict[table].grid.get_field('approver').get_query = function (doc, cdt, cdn) {
                const child = locals[cdt][cdn];
                return {
                    query: "mosyr.api.get_users_2",
      
                };
            };
        })
      
       
    }
  });