import frappe
from frappe.utils import getdate, today

def update_status_for_contracts():
    employee_contracts = frappe.get_all(
        "Employee Contract",
        filters={"status": "Approved", "contract_status": "Valid"},
        fields=["name", "status", "contract_end_date"],
    )
    for contract in employee_contracts:
        if getdate(contract.contract_end_date) > getdate(today()):
                continue
        ec = frappe.get_doc("Employee Contract", contract.get("name"))
        ec.db_set("status", "Ended")
        # ec.db_set("status", "Ended")