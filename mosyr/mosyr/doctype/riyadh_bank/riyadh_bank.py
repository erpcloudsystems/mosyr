# Copyright (c) 2022, AnvilERP and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from random import randint


class RiyadhBank(Document):
    def before_insert(self):
        list_riad = frappe.get_list("Riyadh Bank", pluck="name")
        random_num = str(randint(10000, 100000))

        while random_num in list_riad:
            random_num = str(randint(10000, 100000))
        self.random_number = random_num
        self.today = frappe.utils.today()
