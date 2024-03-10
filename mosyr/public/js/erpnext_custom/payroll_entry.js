make_bank_entry = function (frm) {
    var doc = frm.doc;
    if (doc.payment_account) {
        return frappe.call({
            doc: cur_frm.doc,
            method: "make_payment_entry",
            callback: function () {
                frappe.msgprint(__("Payment Entries Created"));
                frm.events.refresh(frm);
            },
            freeze: true,
            freeze_message: __("Creating Payment Entries......")
        });
    } else {
        frappe.msgprint(__("Payment Account is mandatory"));
        frm.scroll_to_field('payment_account');
    }
};

render_employee_attendance = function (frm, data) {
	frm.fields_dict.attendance_detail_html.html(
		frappe.render_template('employees_to_mark_attendance', {
			data: data
		})
	);
};

frappe.ui.form.on("Payroll Entry", {
    refresh: function (frm) {
        $('[data-original-title="Print"]').on('click', function() {
            window.location.reload();
        });
        if (frm.doc.docstatus == 0) {
            frm.clear_custom_buttons();
            if (!frm.is_new()) {
                frm.page.clear_primary_action();
                frm.add_custom_button(__("Get Employees"),
                    function () {
                        frm.events.get_employee_details_v2(frm);
                    }
                ).toggleClass('btn-primary', !(frm.doc.employees || []).length);
            }
            if ((frm.doc.employees || []).length && !frappe.model.has_workflow(frm.doctype)) {
                frm.page.clear_primary_action();
                frm.page.set_primary_action(__('Create Salary Slips'), () => {
                    frm.save('Submit').then(() => {
                        frm.page.clear_primary_action();
                        frm.refresh();
                        frm.events.refresh(frm);
                    });
                });
            }
        }
        if (frm.doc.docstatus == 1) {
            if (frm.custom_buttons) frm.clear_custom_buttons();
            frm.events.add_context_buttons(frm);
        }
        frm.trigger('check_if_leaves');
    },
    get_employee_details_v2: function (frm) {
		return frappe.call({
			doc: frm.doc,
			method: 'fill_employee_details',
		}).then(r => {
			if (r.docs && r.docs[0].employees) {
				frm.employees = r.docs[0].employees;
				frm.dirty();
				frm.save();
				frm.refresh();
				if (r.docs[0].validate_attendance) {
					render_employee_attendance(frm, r.message);
				}
                frm.trigger('check_if_leaves');
			}
		});
	},
    check_if_leaves: function(frm){
        $(`div[data-fieldname="employees"] .rows .grid-row`)
                  .css('background-color', 'transparent');
        frm.doc.employees.forEach(row => {
            if(flt(row.total_leaves_taken) > 0){
                $(`div[data-fieldname="employees"] .rows .grid-row[data-idx="${row.idx}"]`)
                  .css('background-color', 'rgba(255, 0,0 , 0.05)');
            }
        });
    }
});

frappe.ui.form.on("Payroll Employee Detail", {
    employee: function(frm,cdt,cdn) {
        const row = locals[cdt][cdn]
        if (frm.doc.employee != "") {
            frappe.call({
              method: "mosyr.api.get_salary_per_day",
              args: {
                employee: row.employee,
              },
              callback: function (r) {
                const deduction_per_day = flt(r.message);
                row.deduction_per_day =  deduction_per_day;
                frm.refresh_fields();
              },
            });
          } else {
            row.deduction_per_day = 0 
            row.refresh_field("deduction_per_day");
          }
        return frappe.call({
			doc: frm.doc,
			method: 'get_employee_details_for_payroll',
            args:{employee: row['employee']}
		}).then(r => {
            if(r.message && r.message.total_leaves_taken){
                row['total_leaves_taken'] = r.message.total_leaves_taken;
            }else{
                row['total_leaves_taken'] = 0;
            }
            frm.trigger('check_if_leaves');
		});
    },
    employees_remove: function(frm) {
        frm.trigger('check_if_leaves');
    },
    employees_add: function(frm) {
        frm.trigger('check_if_leaves');
    },
    employees_move: function(frm) {
        frm.trigger('check_if_leaves');
    }
});