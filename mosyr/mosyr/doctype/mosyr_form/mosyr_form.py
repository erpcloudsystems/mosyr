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
			clean_opts = ""
			if field.options is not None:
				clean_opts = f"{field.options}".strip().replace("\n", "")

			if field.fieldtype in ["Select", "Table MultiSelect"] and (clean_opts == "" or field.options is None):
				frappe.throw(_("Options is Required for {} field.".format(field.fieldtype)))

	def autoname(self):
		self.name = make_autoname("MOSYRFRM.YY.MM.DD.#####")

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
			'__newname': self.name,
			'custom': custom
		})
		# for field in copy_doc.fields:
		# 	if field.fieldtype == "Table MultiSelect" and field.options != "":
		# 		self.prepare_for_multiselect(field)

		new_doc = frappe.new_doc('DocType')
		new_doc.update(copy_doc)
		new_doc.insert(ignore_permissions=True)
		self.prepare_trans_for_docname(new_doc.name, self.form_title)
	
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
		trans_to_lang = ["en", "ar"]
		sys_lang = l = frappe.get_value("System Settings", "System Settings", "language")
		if sys_lang not in trans_to_lang:
			trans_to_lang.append(sys_lang)

		for lang in trans_to_lang:
			trans_doc = frappe.new_doc("Translation")
			trans_doc.language = lang
			trans_doc.source_text = f"{text}"
			trans_doc.translated_text = f"{transtext}"
			trans_doc.flags.ignore_mandatory = True
			trans_doc.flags.ignore_validate = True
			# trans_doc.flags.ignore_permissions = True
			trans_doc.save(ignore_permissions=True)
		frappe.db.commit()
