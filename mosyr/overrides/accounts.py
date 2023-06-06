import frappe
from erpnext.accounts.doctype.mode_of_payment.mode_of_payment import ModeofPayment

from mosyr import create_account


class CustomModeofPayment(ModeofPayment):
    def validate(self):
        self.set_missing_custome_values()
        super().validate()
    def set_missing_custome_values(self):
        self.accounts = []
        companies = frappe.get_list("Company", ["name", "abbr"])
        for company in companies:
            account_name = f"{self.mode_of_payment}"
            account = create_account(
                account_name,
                company.name,
                "Current Assets",
                "Asset",
                "Receivable",
                False,
            )
            self.append(
                "accounts", {"company": company.name, "default_account": account}
            )