frappe.ui.get_print_settings = function (
    pdf,
    callback,
    letter_head,
    pick_columns
) {
    var print_settings = locals[":Print Settings"]["Print Settings"];

    var default_letter_head =
        locals[":Company"] && frappe.defaults.get_default("company")
            ? locals[":Company"][frappe.defaults.get_default("company")]["default_letter_head"]
            : "";

    var columns = [
        {
            fieldtype: "Check",
            fieldname: "with_letter_head",
            label: __("With Letter head")
        },
        {
            fieldtype: "Select",
            fieldname: "letter_head",
            label: __("Letter Head"),
            depends_on: "with_letter_head",
            options: Object.keys(frappe.boot.letter_heads),
            default: letter_head || default_letter_head
        },
        {
            fieldtype: "Select",
            fieldname: "orientation",
            label: __("Orientation"),
            options: [
                { value: "Landscape", label: __("Landscape") },
                { value: "Portrait", label: __("Portrait") }
            ],
            default: "Landscape"
        }
    ];

    if (pick_columns) {
        columns.push(
            {
                label: __("Pick Columns"),
                fieldtype: "Check",
                fieldname: "pick_columns",
                onchange: function () {
                    if (cur_dialog) {
                        $(cur_dialog.body).find(':checkbox[data-fieldname="pick_all"]')
                            .prop("checked", 1)
                            .trigger('click');
                    }

                }
            },
            {
                label: __("Pick All Columns"),
                fieldtype: "Check",
                fieldname: "pick_all",
                depends_on: "pick_columns",
                onchange: function () {
                    if (cur_dialog) {
                        const checked = this.value == 1 ? false : true;
                        $(cur_dialog.body).find('[data-fieldtype="MultiCheck"]').map((index, element) => {
                            $(element).find(`:checkbox`)
                                .prop("checked", this.value == 1 ? false : true)
                                .trigger('click');
                        });
                    }
                }
            },
            {
                label: __("Select Columns"),
                fieldtype: "MultiCheck",
                fieldname: "columns",
                depends_on: "pick_columns",
                columns: 2,
                options: pick_columns.map(df => ({
                    label: __(df.label),
                    value: df.fieldname
                }))
            }
        );
    }

    return frappe.prompt(
        columns,
        function (data) {
            data = $.extend(print_settings, data);
            if (!data.with_letter_head) {
                data.letter_head = null;
            }
            if (data.letter_head) {
                data.letter_head =
                    frappe.boot.letter_heads[print_settings.letter_head];
            }
            callback(data);
        },
        __("Print Settings")
    );
}; 