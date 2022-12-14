import frappe


@frappe.whitelist(allow_guest=True)
def add_biometric_data(*args, **kwargs):
    resuest_data = {}
    resuest_data.update(
        {
            "kwargs": kwargs,
            "args": args,
            "req_headers": frappe.request.headers,
            "req_data": frappe.request.data.decode(),
            "req_values": frappe.request.values,
            "req_args": frappe.request.args,
        }
    )
    frappe.logger("mosyr.biometric").debug(resuest_data)
    return "Done :)"
