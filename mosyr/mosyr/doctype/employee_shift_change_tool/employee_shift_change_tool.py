# Copyright (c) 2023, AnvilERP and contributors
# For license information, please see license.txt

import frappe
from frappe import _
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
                                            "name", "employee", "employee_name", "start_date", "end_date", "status", "shift_type"], filters={"employee": emp.get("name")})
                if len(shifts):
                    result.append({
                        "emp": emp.get("name"),
                        "emp_name": emp.get("employee_name"),
                        "emp_shift_count": len(shifts),
                        "emp_shifts": shifts
                    })

        return {"data": result}

    @frappe.whitelist()
    def update_employee_shift_and_recalculate_period(self, employee, new_shift, start_date, end_date, recalculate_period):
        if frappe.db.exists("Shift Type", new_shift):
            if frappe.db.exists("Shift Assignment", {"employee": employee, "shift_type": new_shift, "status": "Active"}):
                shift = frappe.get_doc("Shift Assignment", {
                                       "employee": employee, "shift_type": new_shift, "status": "Active"})
            else:
                try:
                    new_doc = frappe.new_doc("Shift Assignment")
                    new_doc.employee = employee
                    new_doc.shift_type = new_shift
                    new_doc.start_date = start_date
                    new_doc.end_date = end_date
                    new_doc.save()
                    new_doc.submit()
                    if recalculate_period:
                        # Get All missed Employee Checkin
                        sql = """
                            SELECT name
                            FROM `tabEmployee Checkin`
                            WHERE employee = '{0}' AND shift IS NULL AND DATE(time) > '{1}' AND DATE(time) < '{2}'
                        """.format(employee, start_date, end_date)
                        checkin_list = frappe.db.sql(sql, as_dict=1)
                        for row in checkin_list:
                            doc = frappe.get_doc(
                                "Employee Checkin", row.get("name"))
                            doc.save()
                        frappe.db.commit()

                        shift_doc = frappe.get_cached_doc(
                            "Shift Type", new_shift)
                        shift_doc.process_auto_attendance()
                except Exception as e:
                    frappe.log_error(title=_("Error while processing Auto Attendence "), message=e)
