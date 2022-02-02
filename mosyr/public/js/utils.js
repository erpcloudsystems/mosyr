frappe.provide("mosyr");
frappe.provide("mosyr.utils");

$.extend(mosyr.utils, {
    download_errors: (data) => {
        frappe.ui.hide_open_dialog();
        console.log(data.data)
        frappe.call({
            "method": 'mosyr.mosyr.doctype.mosyr_data_import.mosyr_data_import.download_errors',
            "args": { data: data }
        })
    }
});