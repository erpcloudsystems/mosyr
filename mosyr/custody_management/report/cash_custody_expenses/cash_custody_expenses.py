# Copyright (c) 2022, AnvilERP and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def execute(filters=None):
    columns, data = get_columns(), get_data(filters)
    return columns, data


def get_columns():
    columns = [
        {
            "label": _("Custody Cash"),
            "fieldname": "name",
            "fieldtype": "Link",
            "options": "Cash Custody",
        },
        {
            "label": _("Responsible Employee"),
            "fieldname": "responsible_employee",
            "fieldtype": "Link",
            "options": "Employee",
        },
        {
            "label": _("Responsible Name"),
            "fieldname": "responsible_name",
            "fieldtype": "Data",
        },
        {
            "label": _("Branch"),
            "fieldname": "branch",
            "fieldtype": "Link",
            "options": "Branch",
        },
        {
            "label": _("Recipient Employee"),
            "fieldname": "recipient_employee",
            "fieldtype": "Link",
            "options": "Employee",
        },
        {
            "label": _("Recipient Name"),
            "fieldname": "recipient_name",
            "fieldtype": "Data",
        },
        {"label": _("Date(G)"), "fieldname": "date_receipt_g", "fieldtype": "Date"},
        {
            "label": _("Custody Value"),
            "fieldname": "custody_value",
            "fieldtype": "Currency",
        },
        {
            "label": _("Estimated Value"),
            "fieldname": "estimated_value",
            "fieldtype": "Currency",
        },
    ]
    return columns


def get_data(filters):
    COND = ""
    if filters.get("custody"):
        COND += "AND name='{}' ".format(filters.get("custody"))
    if filters.get("res_employee"):
        COND += "AND responsible_employee='{}' ".format(filters.get("res_employee"))
    if filters.get("branch"):
        COND += "AND branch='{}' ".format(filters.get("branch"))
    if filters.get("rec_employee"):
        COND += "AND recipient_employee='{}' ".format(filters.get("rec_employee"))
    if filters.get("from") and filters.get("to"):
        COND += "AND DATEDIFF(date_receipt_g, '{}')>=0 AND DATEDIFF(date_receipt_g, '{}')<=0 ".format(
            filters.get("from"), filters.get("to")
        )

    if filters.get("status"):
        status = filters.get("status")
        if status == "Fully Spent":
            COND += "AND estimated_value=0 "
        if status == "Partially Spent":
            COND += "AND estimated_value>0 AND estimated_value<custody_value "
        if status == "UnSpent":
            COND += "AND estimated_value=custody_value "

    sql = frappe.db.sql(
        """ SELECT name, responsible_employee, responsible_name, branch,
							recipient_employee, recipient_name, date_receipt_g, custody_value, estimated_value
						FROM `tabCash Custody` 
						WHERE docstatus=1 {} """.format(
            COND
        )
    )
    return sql
