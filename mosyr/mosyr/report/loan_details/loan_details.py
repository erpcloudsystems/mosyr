# Copyright (c) 2024, AnvilERP and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)
	return columns, data


def get_columns():
	return [
		{"label": _("Posting Date"), "fieldtype": "Date", "fieldname": "posting_date", "width": 100},
		{
			"label": _("Loan Repayment"),
			"fieldtype": "Link",
			"fieldname": "loan_repayment",
			"options": "Loan Repayment",
			"width": 100,
		},
		{
			"label": _("Against Loan"),
			"fieldtype": "Link",
			"fieldname": "against_loan",
			"options": "Loan",
			"width": 200,
		},
		{"label": _("Applicant"), "fieldtype": "Data", "fieldname": "applicant", "width": 150},
		{"label": _("Applicant Name"), "fieldtype": "Data", "fieldname": "applicant_name", "width": 150},
		{
			"label": _("Principal Amount"),
			"fieldtype": "Currency",
			"fieldname": "principal_amount",
			"options": "currency",
			"width": 100,
		},
		{
			"label": _("Interest Amount"),
			"fieldtype": "Currency",
			"fieldname": "interest",
			"options": "currency",
			"width": 100,
		},
		{
			"label": _("Payable Amount"),
			"fieldtype": "Currency",
			"fieldname": "payable_amount",
			"options": "currency",
			"width": 100,
		},
		{
			"label": _("Paid Amount"),
			"fieldtype": "Currency",
			"fieldname": "paid_amount",
			"options": "currency",
			"width": 100,
		},
		{
			"label": _("Currency"),
			"fieldtype": "Link",
			"fieldname": "currency",
			"options": "Currency",
			"width": 100,
		},
	]




def get_data(filters):
	data = []

	query_filters = {
		"lr.docstatus": 1,
		"lr.company": filters.get("company"),
	}

	if filters.get("applicant"):
		query_filters.update({"lr.applicant": filters.get("applicant")})
	if filters.get("from_date") and filters.get("to_date"):
		query_filters.update({
			"lr.posting_date": ["between", [filters.get("from_date"), filters.get("to_date")]]
		})
	elif filters.get("from_date"):
		query_filters.update({"lr.posting_date": [">=", filters.get("from_date")]})
	elif filters.get("to_date"):
		query_filters.update({"lr.posting_date": ["<=", filters.get("to_date")]})

	loan_repayments = frappe.db.sql("""SELECT DISTINCT
                    lr.posting_date AS posting_date,
                    lr.applicant AS applicant,
                    lr.name AS name,
                    lr.against_loan AS against_loan,
                    lr.payable_amount AS payable_amount,
                    lr.pending_principal_amount AS pending_principal_amount,
                    lr.interest_payable AS interest_payable,
                    lr.penalty_amount AS penalty_amount,
                    lr.amount_paid AS amount_paid,
                    L.applicant_name AS applicant_name
                 FROM
                    `tabLoan Repayment` AS lr
                 LEFT JOIN
                    `tabLoan` AS L
                 ON
                    lr.applicant = L.applicant
                 WHERE
                    lr.docstatus = 1
                    AND lr.company = %s
                    AND (lr.applicant = %s OR %s IS NULL)
                    AND (lr.posting_date BETWEEN %s AND %s OR %s IS NULL OR %s IS NULL)
                 ORDER BY
                    lr.applicant""",
                 (filters.get("company"), filters.get("applicant"), filters.get("applicant"),
                  filters.get("from_date"), filters.get("to_date"), filters.get("from_date"), filters.get("to_date")), as_dict =1)


	default_currency = frappe.get_cached_value("Company", filters.get("company"), "default_currency")

	for repayment in loan_repayments:
		row = {
			"posting_date": repayment.posting_date,
			"loan_repayment": repayment.name,
			"applicant": repayment.applicant,
			"against_loan": repayment.against_loan,
			"principal_amount": repayment.pending_principal_amount,
			"interest": repayment.interest_payable,
			"penalty": repayment.penalty_amount,
			"payable_amount": repayment.payable_amount,
			"paid_amount": repayment.amount_paid,
			"currency": default_currency,
			"applicant_name": repayment.applicant_name,
		}

		data.append(row)

	return data

