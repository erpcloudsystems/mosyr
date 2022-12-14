# Copyright (c) 2022, AnvilERP and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import getdate


class EndOfService(Document):
    pass


@frappe.whitelist()
def get_diff_year_month_day(contract_end_date, date_of_joining):
    contract_end_date = getdate(contract_end_date)
    date_of_joining = getdate(date_of_joining)
    from dateutil.relativedelta import relativedelta
    diff = relativedelta(contract_end_date, date_of_joining)
    date = {'years': str(diff.years), 'months': str(
        diff.months), 'days': str(diff.days)}
    return date


@frappe.whitelist()
def calculate_end_awards(salary, number_of_years, number_of_months, number_of_days, type_of_contract, reason_of_end_contract):
    if reason_of_end_contract == '3':
        return {"value": 0}
    if reason_of_end_contract == '7':
        return {"value": 0}

    if int(number_of_years) >= 5:
        value = (.5 * float(salary) * 5) + (float(salary) * (int(number_of_years) - 5))\
            + (float(salary) / 12) * int(number_of_months) + \
            (float(salary) / 365) * int(number_of_days)
    if float(number_of_years) < 5:
        value = (.5 * float(salary) * int(number_of_years)) \
            + (.5 * float(salary) / 12) * int(number_of_months) + \
            (.5 * float(salary) / 365) * int(number_of_days)

    if reason_of_end_contract == '8':
        if int(number_of_years) < 2:
            return {"value": 0}

        if int(number_of_years) >= 2 and int(number_of_years) < 5:
            return {"value": (value/3)}

        if int(number_of_years) >= 5 and int(number_of_years) < 10:
            return {"value": (value * 2/3)}

        if int(number_of_years) >= 10:
            return {"value": value}

    return {"value": value}


@frappe.whitelist()
def get_salary(employee):
    earning = []
    salary = frappe.db.sql("""select net_pay, gross_pay, name,  start_date
            from  `tabSalary Slip` where
               employee = %(employee)s and docstatus = 1 and  total_working_days = payment_days order by start_date DESC  """, {'employee': employee}, as_dict=1)
    if salary:
        net_pay = salary[0].gross_pay
    else:
        net_pay = 0
    if salary:
        earning = frappe.db.sql("""select  salary_component, amount from `tabSalary Detail`
    							where parentfield='earnings' and parent= '{0}' """.format(str(salary[0].name)), as_dict=1)
    if not earning:
        earning = []
    return {"salary": net_pay, "earning": earning}
