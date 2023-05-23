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


@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def fetch_vehicle_log(doctype, txt, searchfield, start, page_len, filters):
	cond = ""
	employee = ""
	user = frappe.get_doc("User", frappe.session.user)
	if user.user_type == "Employee Self Service":
		employees = frappe.get_list("Employee", {"user_id": user.name})
		employee = employees[0].name if any(employees) else ""

	if employee:
		cond = "AND employee = '%s'" % employee

	return frappe.db.sql(
		"""SELECT name from `tabVehicle Log`
			WHERE `{key}` LIKE %(txt)s {cond}
			AND docstatus=1
			ORDER BY name LIMIT %(start)s, %(page_len)s""".format(
			key=searchfield, cond=cond
		),
		{"txt": "%" + txt + "%", "start": start, "page_len": page_len},
	)