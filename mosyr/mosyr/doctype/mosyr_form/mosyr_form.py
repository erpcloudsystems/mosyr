# Copyright (c) 2022, AnvilERP and contributors
# For license information, please see license.txt
import json

import frappe
from frappe import _

from frappe.model.document import Document

from frappe.model.naming import make_autoname

class MosyrForm(Document):
	def validate(self):
		for field in self.fields:
			if field.fieldtype in ["Select", "Table MultiSelect"] and field.options == "":
				frappe.throw(_("Options is Required for {} field.".format(field.fieldtype)))

	def on_submit(self):
		module = "Mosyr Forms"
		allow_rename = 0
		custom = 1
		copy_doc = frappe.copy_doc(self, ignore_no_copy=False).as_json()
		copy_doc.replace('ERPFormField', 'DocField')
		copy_doc = json.loads(copy_doc)
		doc_name = make_autoname("MOSYRFRM.YY.MM.DD.#####")
		copy_doc.update({
			'__newname': doc_name,
			'module': module,
			'allow_rename': allow_rename,
			# 'name': self.name,
			'custom': custom
		})
		for field in copy_doc.fields:
			if field.fieldtype == "Table MultiSelect" and field.options != "":
				self.prepare_for_multiselect(field)

		new_doc = frappe.new_doc('DocType')
		new_doc.update(copy_doc)
		new_doc.insert(ignore_permissions=True)
	
	def prepare_for_multiselect(self, field:dict)-> list:
		doc_name = make_autoname("FRMOPT.YY.MM.DD.#####")
		# TODO(1) Make Doctype
		copy_doc = {
			'__newname': doc_name,
			'module': "Mosyr Forms",
			'allow_rename': 0,
			'custom': 1
		}
		new_doc = frappe.new_doc('DocType')
		new_doc.update(copy_doc)
		new_doc.insert(ignore_permissions=True)
		# TODO(2) Use Options to insert data to doctype
		# TODO(3) Make Childtable Withlink
		# TODO(4) repalce field options in DocType
		pass

	def use_name_as_fieldname_in_childtable(self, doc):
		fields = []
		for field in doc.fields:
			field.update({
				"fieldname": field.name
			})
			fields.append(field)
		return fields

	def prepare_trans_for_docname(self, text, transtext):
		pass
