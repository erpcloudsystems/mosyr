frappe.ui.form.on('Loan', {
    onload: function(frm ){
        if((frm.doc.total_amount_remaining) > 0){
            frm.add_custom_button(__('Loan Deferral'), function() {
                frappe.call({
                    method: 'mosyr.api.get_repayment_schedule',
                    args:{
                        doc: frm.doc
                    },
                    callback: function (r) {
                        let fields = [
                                    {
                                        fieldtype: 'Read Only',
                                        fieldname: 'idx',
                                        in_list_view: 1,
                                        label: __('Index'),
                                        read_only: 1
                                    }, 
                                    {
                                        fieldtype: 'Read Only',
                                        fieldname: 'payment_date',
                                        label: __('Payment Date'),
                                        in_list_view: 1,
                                        read_only: 1,
                                    },
                                    {
                                        fieldtype: 'Read Only',
                                        fieldname: 'total_payment',
                                        label: __('Total Payment'),
                                        in_list_view: 1,
                                        read_only: 1
                                    },
                                    {
                                        fieldtype: 'Read Only',
                                        fieldname: 'paid_amount',
                                        label: __('Paid Amount'),
                                        in_list_view: 1,
                                        read_only: 1
                                    },
                                    {
                                        fieldtype: 'Date',
                                        fieldname: 'new_payment_date',
                                        label: __('New Payment Date'),
                                        in_list_view: 1,
                                    },
                                ];

                        let d = new frappe.ui.Dialog({
                            title: __('Loan Deferral'),
                            fields: [
                                {
                                    fieldname: 'repayment_table',
                                    fieldtype: 'Table',
                                    label: __('Loan Deferral Table'),
                                    cannot_add_rows: true,
                                    cannot_delete_rows: true,
                                    cannot_edit_rows: true,
                                    in_place_edit: true,
                                    in_editable_grid: false,
                                    reqd: 1,
                                    fields: fields,
                                    data: r.message,
                                    // read_only:1,
                                    // row_display:true,
                                }
                            ],
                            size: 'large',
                            // minimizable: true,
                            primary_action: function(values) {
                                let row = []
                                values.repayment_table.forEach(element => {
                                    let val = element.new_payment_date
                                    let row_name = element.name
                                    if (val){
                                        const date1 = new Date(frappe.datetime.get_today());
                                        const date2 = new Date(val);
                                        const diffTime = date2 - date1;
                                        if (diffTime >= 0){
                                            row.push({"row_name":row_name ,"new_date" :val})
                                        }
                                        else {
                                            frappe.throw("Choose Date In Future")
                                        }
                                    }
                                })
                                frappe.call({
                                    method: 'mosyr.api.set_new_date_in_repayment',
                                    args: {
                                        row: row
                                    },
                                    callback: function(r) {
                                        frappe.msgprint(__('Payment has been deferred'));
                                        location.reload();
                                    }
                                })
                                d.hide();
                            }
                        });
                        d.show();
                    }
                });
            });
        }
    }
})
