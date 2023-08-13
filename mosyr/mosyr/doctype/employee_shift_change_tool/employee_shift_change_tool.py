# Copyright (c) 2023, AnvilERP and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class EmployeeShiftChangeTool(Document):
    def validate(self):
        pass

    @frappe.whitelist()
    def fetch_employees_shift(self, company):
        result = []
        emp_list = frappe.db.get_list(
            "Employee", fields=["name", "employee_name"], filters={"company": company})
        if emp_list:
            for emp in emp_list:
                shifts = frappe.db.get_list("Shift Assignment", fields=[
                                            "name", "employee_name", "start_date", "end_date", "status", "shift_type"], filters={"employee": emp.get("name")})
                if len(shifts):
                    result.append({
                        "emp": emp.get("name"),
                        "emp_name": emp.get("employee_name"),
                        "emp_shift_count": len(shifts),
                        "emp_shifts": shifts
                    })

        return {"data": result}
