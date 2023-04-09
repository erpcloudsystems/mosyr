
import frappe

def execute():
    cash_custody_expense =  frappe.get_list("Cash Custody Expense", pluck="name")
    if len(cash_custody_expense) > 0:
        for cash in cash_custody_expense:
            cash_custody_expense = frappe.get_doc("Cash Custody Expense", cash)
            cash_custody_expense.db_set("remaining_value", (cash_custody_expense.estimated_value - cash_custody_expense.spent_value))
            cash_custody_expense.save()
        frappe.db.commit()