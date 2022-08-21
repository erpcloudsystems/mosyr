# Copyright (c) 2022, AnvilERP and contributors
# For license information, please see license.txt
import json

import frappe
from frappe.model.document import Document

class MosyrForm(Document):
	def on_submit(self):
		module = "HR"
		allow_rename = 0
		custom = 1
		copy_doc = frappe.copy_doc(self, ignore_no_copy=False).as_json()
		copy_doc.replace('ERPFormField', 'DocField')
		copy_doc = json.loads(copy_doc)
		copy_doc.update({
			'module': module,
			'allow_rename': allow_rename,
			'name': self.name,
			'custom': custom
		})
		new_doc = frappe.new_doc('DocType')
		new_doc.update(copy_doc)
		new_doc.insert(ignore_permissions=True)
