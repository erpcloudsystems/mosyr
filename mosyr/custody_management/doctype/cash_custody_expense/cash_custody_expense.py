# Copyright (c) 2022, AnvilERP and contributors
# For license information, please see license.txt

import frappe
from frappe import _, throw
from frappe.model.document import Document

class CashCustodyExpense(Document):
    def validate(self):
        self.check_valid_spent_value()
        self.remaining_value = self.estimated_value - self.spent_value

    def on_submit(self):
        self.add_custody_expense()

    def check_valid_spent_value(self):
        if self.estimated_value == 0:
            throw(_("The cash custody <b>{}</b> value has been paid in full".format(self.cash_custody)))

        if self.spent_value > self.estimated_value:
            frappe.throw(_("<b>Spent value {}</b> must be smaller than or equal <b>estimated value {}</b>".format(self.spent_value, self.estimated_value)))

    def add_custody_expense(self):
        doc = frappe.get_doc('Cash Custody', self.cash_custody)
        doc.estimated_value -= self.spent_value
        doc.append('cash_custody_expense',{
            'cash_custody': self.name,
            'spent_value': self.spent_value
        })
        doc.save()
        frappe.db.commit()