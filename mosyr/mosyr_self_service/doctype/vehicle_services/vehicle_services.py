# Copyright (c) 2023, AnvilERP and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class VehicleServices(Document):
	def on_submit(self):
		self.set_vehicle_services_details()
	
	def set_vehicle_services_details(self):
		# set details in vehicle log service detail table
		vlog = frappe.get_doc("Vehicle Log", self.vehicle_log)
		vlog.append("service_detail", {
			"service_item": self.service_item,
			"type": self.type or "",
			"frequency": self.frequency or "",
			"expense_amount": self.expense or 0,
			"attachment": self.attachment,
			"details": self.details or ""
		})
		vlog.flags.ignore_mandatory = True
		vlog.save()
		frappe.db.commit()
