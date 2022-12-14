# Copyright (c) 2022, AnvilERP and contributors
# For license information, please see license.txt

from dataclasses import field
import frappe
from frappe import _
from frappe.utils import get_host_name
import requests
from frappe.utils import format_datetime, get_datetime_str

def execute(filters=None):
	host_name = get_host_name()
	print(host_name)
	res = requests.get(f"http://3.136.126.6/devices/{host_name}")
	data = []
	for d in res.json():
		fields = d.get('fields', {})
		last_check = fields.get('last_check', False)
		if last_check:
			last_check = format_datetime(get_datetime_str(last_check), "dd-MM-yyyy hh:mm")
			fields.update({
				'last_check': last_check
			})
		data.append(fields)
	columns, data = get_columns(), data
	return columns, data

def get_columns():
	return [
		{
			"label": _("Device SN"),
			"fieldtype": "Data",
			"width": 200,
			"fieldname": "device_sn"
		},
		{
			"label": _("Location"),
			"fieldtype": "Data",
			"width": 200,
			"fieldname": "device_location"
		},
		{
			"label": _("Last Checkin"),
			"fieldtype": "Data",
			"width": 200,
			"fieldname": "last_check"
		}
    ]
