frappe.ui.form.on("Salary Component", {
    refresh: function (frm) {
        frm.trigger("set_formula")
        frm.trigger("handle_form_change")

    },
    after_save: function (frm) {
        if(frm.doc.amount_based_on_formula){
            let amount = $("#formula_amount").val()
            let operation = $("#formula_operation").val()
            let abbr = $("#formula_abbr").val()
    
            frappe.call({
                method: "mosyr.api.handle_formula",
                args: {
                    docname: frm.doc.name,
                    amount,
                    operation,
                    abbr
                },
                callback: function (r) {
                    if (!r.exc && r.message) {
                        frm.refresh_fields()
                    }
                },
            })
        }
	},
    set_formula: function (frm){
        // set formula from text field in formula from
        if(frm.doc.amount_based_on_formula && frm.doc.formula){
            let formula = frm.doc.formula
            let abbr = formula.split(" ")[0]
            let operation = formula.split(" ")[1]
            let amount = formula.split(" ")[2]

            $("#formula_amount").val(amount)
            $("#formula_operation").val(operation)
            $("#formula_abbr").val(abbr)
        }
    },
    handle_form_change: function(frm){
        // set document as unsaved to active save button
        $("#formula_amount").on("change", e => {
            if (parseFloat(e.target.value) > 0) {
                frm.doc.__unsaved = 1
            }
        })
        $("#formula_operation").on("change", e => {
            frm.doc.__unsaved = 1
        })
    }
});