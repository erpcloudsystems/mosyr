frappe.views.ListView.prototype.get_subject_html = function(doc){
    let subject_field = this.columns[0].df;
    let value = doc[subject_field.fieldname];
    if (this.settings.formatters && this.settings.formatters[subject_field.fieldname]) {
        let formatter = this.settings.formatters[subject_field.fieldname];
        value = formatter(value, subject_field, doc);
    }
    if (!value) {
        value = doc.name;
    }
    let subject = strip_html(value.toString());
    let escaped_subject = frappe.utils.escape_html(subject);

    const seen = this.get_seen_class(doc);

    let subject_html = `
        <span class="level-item select-like">
            <input class="list-row-checkbox" type="checkbox"
                data-name="${escape(doc.name)}">
            <span class="list-row-like hidden-xs style="margin-bottom: 1px;">
                ${this.get_like_html(doc)}
            </span>
        </span>
        <span class="level-item ${seen} ellipsis" title="${escaped_subject}">
            <a class="ellipsis"
                href="${this.get_form_link(doc)}"
                title="${escaped_subject}"
                data-doctype="${this.doctype}"
                data-name="${doc.name}">
                ${__(subject)}
            </a>
        </span>
    `;

    return subject_html;
}