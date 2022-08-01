frappe.provide("mosyr");
frappe.provide("mosyr.utils");
$.extend(mosyr, {
    download_errors: (data) => {
        let w = window.open(
			frappe.urllib.get_full_url(
				    '/api/method/frappe.utils.print_format.download_pdf?' +
					'doctype=' +
					encodeURIComponent('Mosyr Data Import Log') +
					'&name=' +
					encodeURIComponent('e42237ba5e') +
					'&format=' +
					encodeURIComponent('Data Import Log') +
					'&no_letterhead=1' +
					'&letterhead=' +
					encodeURIComponent('No')
			)
		);
		if (!w) {
			frappe.msgprint(__('Please enable pop-ups'));
			return;
		}
        // console.log(data);
        // const dname = data.data || ''
        // frappe.route_options = {
        //     'print_format': 'Data Import Log'
        // };
        // frappe.set_route(['print', 'Mosyr Data Import Log', dname])
    }
});