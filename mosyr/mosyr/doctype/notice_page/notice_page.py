# Copyright (c) 2022, AnvilERP and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from mosyr.api import get_will_expire_docs

class NoticePage(Document):
	
	@frappe.whitelist()
	def get_date(self):
		result = get_will_expire_docs()
		contracts = self.get_contracts(result.get("expire_contracts")) if len(result.get("expire_contracts")) else []
		ids = self.get_ids(result.get("expire_identities")) if len(result.get("expire_identities")) else []
		passports = self.get_passports(result.get("expire_passports")) if len(result.get("expire_passports")) else []
		insurances = self.get_insurances(result.get("expire_Insurances")) if len(result.get("expire_Insurances")) else []


		return {
			"contracts":contracts,
			"ids": ids,
			"passports": passports,
			"insurances": insurances
		}


	def get_contracts(self, contracts):
		contract_list = []
		for contract in contracts:
			contract_doc = frappe.get_doc("Employee Contract", contract.get("name"))
			contract_list.append({
				"employee": contract_doc.employee,
				"employee_name": contract_doc.employee_name,
				"employee_img": frappe.db.get_value("Employee", contract_doc.employee, "image") or None,
				"department": frappe.db.get_value("Employee", contract_doc.employee, "department"),
				"expire_date": contract_doc.contract_end_date
			})

		return contract_list

	def get_ids(self, ids):
		ids_list = []
		for id in ids:
			id_doc = frappe.get_doc("Identity", id.get("name"))
			ids_list.append({
				"employee": id_doc.parent,
				"employee_name": frappe.db.get_value("Employee", id_doc.parent, "employee_name"),
				"employee_img": frappe.db.get_value("Employee", id_doc.parent, "image") or None,
				"department": frappe.db.get_value("Employee", id_doc.parent, "department"),
				"expire_date": id_doc.expire_date
			})

		return ids_list

	def get_passports(self, passports):
		passports_list = []
		for passport in passports:
			passport_doc = frappe.get_doc("Passport", passport.get("name"))
			passports_list.append({
				"employee": passport_doc.parent,
				"employee_name": frappe.db.get_value("Employee", passport_doc.parent, "employee_name"),
				"employee_img": frappe.db.get_value("Employee", passport_doc.parent, "image") or None,
				"department": frappe.db.get_value("Employee", passport_doc.parent, "department"),
				"expire_date": passport_doc.passport_expire
			})

		return passports_list

	def get_insurances(self, insurances):
		insurances_list = []
		for insurance in insurances:
			insurance_doc = frappe.get_doc("Employee", insurance.get("name"))
			insurances_list.append({
				"employee": insurance_doc.name,
				"employee_name": insurance_doc.employee_name,
				"employee_img": insurance_doc.image or None,
				"department": insurance_doc.department,
				"expire_date": insurance_doc.insurance_card_expire
			})

		return insurances_list
