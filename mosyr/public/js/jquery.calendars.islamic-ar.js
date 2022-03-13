/* http://keith-wood.name/calendars.html
   Arabic localisation for Islamic calendar for jQuery v2.1.0.
   Written by Keith Wood (wood.keith{at}optusnet.com.au) August 2009.
   Updated by Fahad Alqahtani April 2016. */
(function($) {
    'use strict';
    $.calendars.calendars.islamic.prototype.regionalOptions.ar = {
        name: 'Islamic',
        epochs: ['BAM', 'AM'],
        monthNames: 'محرم_صفر_ربيع الأول_ربيع الثاني_جمادى الأول_جمادى الآخر_رجب_شعبان_رمضان_شوال_ذو القعدة_ذو الحجة'.split('_'),
        monthNamesShort: 'محرم_صفر_ربيع1_ربيع2_جمادى1_جمادى2_رجب_شعبان_رمضان_شوال_القعدة_الحجة'.split('_'),
        dayNames: ['الأحد', 'الإثنين', 'الثلاثاء', 'الأربعاء', 'الخميس', 'الجمعة', 'السبت'],
        dayNamesShort: 'أحد_إثنين_ثلاثاء_أربعاء_خميس_جمعة_سبت'.split('_'),
        dayNamesMin: 'ح_ن_ث_ر_خ_ج_س'.split('_'),
        digits: $.calendars.substituteDigits(['٠', '١', '٢', '٣', '٤', '٥', '٦', '٧', '٨', '٩']),
        dateFormat: 'dd-mm-yyyy',
        firstDay: 1,
        isRTL: true
    };
})(jQuery);

frappe.ui.form.ControlData.prototype.bind_hijri_change_event = function() {
    const change_handler = e => {
        console.log('this.change', this.change);
        if (this.change) {
            if (this.bind_hijri_changed) {
                this.change(e);
            } else {
                this.bind_hijri_changed = true
            }

        } else {
            if (this.bind_hijri_changed) {
                let value = this.get_input_value();
                this.parse_validate_and_set_in_model(value, e);
            } else {
                this.bind_hijri_changed = true
            }

        }
    };
    this.$input.on("change", change_handler);
    if (this.trigger_change_on_input_event && !this.in_grid()) {
        // debounce to avoid repeated validations on value change
        this.$input.on("input", frappe.utils.debounce(change_handler, 500));
    }
}

frappe.ui.form.ControlData.prototype.make_input = function() {
    if (this.$input) return;

    this.$input = $("<" + this.html_element + ">")
        .attr("type", this.input_type)
        .attr("autocomplete", "off")
        .addClass("input-with-feedback form-control")
        .prependTo(this.input_area);

    this.$input.on('paste', (e) => {
        let pasted_data = frappe.utils.get_clipboard_data(e);
        let maxlength = this.$input.attr('maxlength');
        if (maxlength && pasted_data.length > maxlength) {
            let warning_message = __('The value you pasted was {0} characters long. Max allowed characters is {1}.', [
                cstr(pasted_data.length).bold(),
                cstr(maxlength).bold()
            ]);

            // Only show edit link to users who can update the doctype
            if (this.frm && frappe.model.can_write(this.frm.doctype)) {
                let doctype_edit_link = null;
                if (this.frm.meta.custom) {
                    doctype_edit_link = frappe.utils.get_form_link(
                        'DocType',
                        this.frm.doctype, true,
                        __('this form')
                    );
                } else {
                    doctype_edit_link = frappe.utils.get_form_link('Customize Form', 'Customize Form', true, null, {
                        doc_type: this.frm.doctype
                    });
                }
                let edit_note = __('{0}: You can increase the limit for the field if required via {1}', [
                    __('Note').bold(),
                    doctype_edit_link
                ]);
                warning_message += `<br><br><span class="text-muted text-small">${edit_note}</span>`;
            }

            frappe.msgprint({
                message: warning_message,
                indicator: 'orange',
                title: __('Data Clipped')
            });
        }
    });

    this.set_input_attributes();
    this.input = this.$input.get(0);
    this.has_input = true;
    this.bind_hijri_changed = false
    if (this.df.options == 'Hijri Date') {
        this.bind_hijri_change_event();
    } else {
        this.bind_change_event();
    }

    this.setup_autoname_check();

    if (this.df.options == 'Hijri Date') {
        $(this.$input).calendarsPicker({
            calendar: $.calendars.instance('islamic', 'ar')
        });
    }

    if (this.df.options == 'URL') {
        this.setup_url_field();
    }

    if (this.df.options == 'Barcode') {
        this.setup_barcode_field();
    }
}

frappe.ui.form.ControlData.prototype.validate = function(v) {
    if (!v) {
        return '';
    }
    if (this.df.is_filter) {
        return v;
    }
    if (this.df.options == 'Phone') {
        this.df.invalid = !validate_phone(v);
        return v;
    } else if (this.df.options == 'Name') {
        this.df.invalid = !validate_name(v);
        return v;
    } else if (this.df.options == 'Email') {
        var email_list = frappe.utils.split_emails(v);
        if (!email_list) {
            return '';
        } else {
            let email_invalid = false;
            email_list.forEach(function(email) {
                if (!validate_email(email)) {
                    email_invalid = true;
                }
            });
            this.df.invalid = email_invalid;
            return v;
        }
    } else if (this.df.options == 'URL') {
        this.df.invalid = !validate_url(v);
        return v;
    } else if (this.df.options == 'Hijri Date') {
        // if (v && !frappe.datetime.validate(v)) {
        //     let sysdefaults = frappe.sys_defaults;
        //     let date_format = sysdefaults && sysdefaults.date_format ?
        //         sysdefaults.date_format : 'dd-mm-yyyy';
        //     frappe.msgprint(__("Date {0} must be in format: {1}", [v, date_format]));
        //     return '';
        // }
        return v;
    } else {
        return v;
    }
}