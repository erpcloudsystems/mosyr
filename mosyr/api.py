import frappe 


@frappe.whitelist()
def check_payment_mode(doc, method):
    if not doc.mode_of_payment or not doc.payment_account:
        payment_account = frappe.db.get_value("Account", {"company": doc.company, "account_type": "Cash"}, "name")
        payment_mode_list = frappe.get_list("Mode of Payment", filters={"type":"Cash"})
        if payment_mode_list:
            doc.mode_of_payment = payment_mode_list[0].name
            doc.payment_account = payment_account
        else:
            company_list = frappe.get_list("Company", fields=["name", "default_cash_account"])
            new_pay_mode = frappe.new_doc("Mode of Payment")
            new_pay_mode.mode_of_payment = "Cash"
            new_pay_mode.enabled = 1
            new_pay_mode.type = "Cash"
            if company_list:
                for company in company_list:
                    new_pay_mode.append("accounts", {
                        "company": company.get("name") or "",
                        "default_account": company.get("default_cash_account") or ""
                    })

            new_pay_mode.save()
            doc.mode_of_payment = new_pay_mode.name
            doc.payment_account = payment_account

@frappe.whitelist()
def set_accounts(doc, method):
    doc.accounts = []
    company_list = frappe.get_list("Company", fields=["name", "default_payroll_payable_account"])
    if company_list:
        for company in company_list:
            doc.append("accounts", {
                "company": company.get("name") or "",
                "account": company.get("default_payroll_payable_account") or ""
            })
            

    