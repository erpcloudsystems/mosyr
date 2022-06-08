# Copyright (c) 2022, AnvilERP and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe import sendmail, msgprint

class ReturnCustody(Document):
	def on_submit(self):
		# change returned custody's status -> Returned & returned custody -> name
		custody = frappe.get_doc('Custody', self.custody)
		custody.status = "Returned"
		custody.returned_custody = self.name
		custody.save()
		# send email for recipent employee
		self.send_email()
	
	def send_email(self):
		recipent = frappe.get_value('Employee', self.recipt_employee, 'user_id')
		if recipent:
			sendmail(
				recipients=[recipent],
				subject=_("Return Custody for {0}").format(self.custody),
				message=_(""),
				reference_name=self.custody,
			)
			msgprint(_("email sent successfully for {}".format(self.recipt_employee)))
