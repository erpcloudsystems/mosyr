
def execute():
    import frappe
    for company in frappe.get_list("Company"):
        company = company.name
        account_currency = frappe.get_value("Company", company, "default_currency") or "USD"
        for account in frappe.get_list("Account", filters={"company": company, "account_currency": ["!=", account_currency]}):
            frappe.db.set_value("Account", account.name, "account_currency", account_currency)
    frappe.db.commit()