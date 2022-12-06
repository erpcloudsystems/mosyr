frappe.ui.form.on("Loan", {
  refresh: function (frm) {
    if (frm.doc.docstatus != 1 && frm.doc.total_amount_remaining > 0) {
      return;
    }
    frm.add_custom_button(__("Loan Deferral"), function () {
      frappe.call({
        method: "mosyr.api.get_repayment_schedule",
        args: {
          doc_name: frm.doc.name,
        },
        callback: function (r) {
          const fields = frm.events.get_table_fields();
          const d = frm.events.create_dialog(fields, r.message || []);
          d.show();
        },
        freeze: true,
        msg_freeze: __("Wait to fetch data"),
      });
    });
  },
  get_table_fields: function () {
    return [
      {
        fieldtype: "Read Only",
        fieldname: "idx",
        in_list_view: 0,
        label: __("Index"),
        read_only: 1,
      },
      {
        fieldtype: "Read Only",
        fieldname: "payment_date",
        label: __("Payment Date"),
        in_list_view: 1,
        read_only: 1,
      },
      {
        fieldtype: "Read Only",
        fieldname: "total_payment",
        label: __("Total Payment"),
        in_list_view: 1,
        read_only: 1,
      },
      {
        fieldtype: "Read Only",
        fieldname: "paid_amount",
        label: __("Paid Amount"),
        in_list_view: 1,
        read_only: 1,
      },
      {
        fieldtype: "Date",
        fieldname: "new_payment_date",
        label: __("New Payment Date"),
        in_list_view: 1,
      },
    ];
  },
  create_dialog: function (fields, data) {
    const d = new frappe.ui.Dialog({
      title: __("Loan Deferral"),
      fields: [
        {
          fieldname: "repayment_table",
          fieldtype: "Table",
          label: __("Loan Deferral Table"),
          cannot_add_rows: true,
          cannot_delete_rows: true,
          cannot_edit_rows: true,
          in_place_edit: true,
          in_editable_grid: false,
          reqd: 1,
          fields: fields,
          data: data,
        },
      ],
      size: "large",
      primary_action: function (values) {
        let rows = [];
        values.repayment_table.forEach((element) => {
          let val = element.new_payment_date;
          let row_name = element.name;
          rows.push({ row_name: row_name, new_date: val });
        //   if (val) {
        //     const today = new Date(frappe.datetime.get_today());
        //     const payment_date = new Date(val);
        //     const diffTime = payment_date - today;
        //     if (diffTime >= 0) {
              
        //     } else {
        //       frappe.throw(__("Choose Date In Future"));
        //     }
        //   }
        });
        frappe.call({
          method: "mosyr.api.set_new_date_in_repayment",
          args: {
            rows: rows,
            doc_name: cur_frm.doc.name,
          },
          callback: function (r) {
            frappe.msgprint(__("Payment has been deferred"));
            cur_frm.reload_doc();
            if(r.message != "err"){
                d.hide();
            }
          },
          freeze: true,
          msg_freeze: __("Wait to update the document"),
        });
      },
    });
    d.$wrapper.find(".row-index").remove();
    d.$wrapper.find('[data-fieldname="payment_date"]').addClass('disabled-inpt')

    
    return d;
  },
});
