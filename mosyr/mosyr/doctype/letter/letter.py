# Copyright (c) 2023, AnvilERP and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class Letter(Document):
	pass

@frappe.whitelist()
def set_DF_print_format(pr_name):
	"""Set print format as default"""
	if not frappe.get_list("Print Format", {"doc_type": "Letter", "name": pr_name}):
		pr_name = ""
	doctype = frappe.get_doc("DocType", "Letter")
	doctype.db_set("default_print_format", pr_name)
	frappe.reload_doctype("Letter")
	frappe.db.commit()
