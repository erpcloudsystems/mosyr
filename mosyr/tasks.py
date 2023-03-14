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

def notify_expired_dates_task():
    notify_expired_dates(False)

def notify_expired_dates(skip_check_olds=True):
    # turn off all notifications
    if not skip_check_olds:
        frappe.db.sql("""UPDATE `tabEmployee` SET notify_id=0, notify_passport=0, notify_insurance_d=0, notify_insurance_e=0 WHERE 1=1""")
        frappe.db.commit()

    for employee in frappe.get_all(
        "Employee", 
        fields=["name"],
        filters={"status": "Active"},
        ):
        emp = frappe.get_doc("Employee", employee.get("name"))
        # Check Employee Insurance
        if getdate(emp.insurance_card_expire) < getdate(today()):
            emp.db_set("notify_insurance_e", 1, update_modified=False)

        # Check ID's
        need_update = False
        for eid in emp.identity:
            if getdate(eid.expire_date) < getdate(today()):
                need_update = True
        if need_update: emp.db_set("notify_id", 1, update_modified=False)

        # Check Passports
        need_update = False
        for epass in emp.passport:
            if getdate(epass.passport_expire) < getdate(today()):
                need_update = True
        if need_update: emp.db_set("notify_passport", 1, update_modified=False)

        # Check Dependent Insurance
        need_update = False
        for edep in emp.dependent:
            if getdate(edep.insurance_card_expire) < getdate(today()):
                need_update = True
        if need_update: emp.db_set("notify_insurance_d", 1, update_modified=False)

def process_auto_attendance_for_all_shifts():
    frappe.log_error("5min", "Error log every 5 minutes")
    shift_list = frappe.get_all("Shift Type", filters={"enable_auto_attendance": "1"}, pluck="name")
    for shift in shift_list:
        doc = frappe.get_cached_doc("Shift Type", shift)
        try:
            doc.process_auto_attendance_v2()
            doc.db_set("last_sync_of_checkin", frappe.utils.now_datetime(), update_modified=False)
        except Exception as e:
            frappe.log_error(e, "faild to process auto-attendance")
