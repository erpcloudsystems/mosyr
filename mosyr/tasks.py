import frappe
from frappe import _
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
    shift_list = frappe.get_all("Shift Type", filters={"enable_auto_attendance": "1"}, pluck="name")
    for shift in shift_list:
        doc = frappe.get_cached_doc("Shift Type", shift)
        try:
            doc.process_auto_attendance_v2()
            doc.db_set("last_sync_of_checkin", frappe.utils.now_datetime(), update_modified=False)
        except Exception as e:
            frappe.log_error(e, "faild to process auto-attendance")

def employee_end_contract():
    # change employee status based on contract end date to inactive status
    employees = frappe.db.sql("""
        SELECT name FROM tabEmployee
        WHERE contract_end_date <> '' AND DATE(contract_end_date) < NOW()
        AND status = 'Active'
    """, as_dict=True)

    if any(employees):
        for employee in employees:
            frappe.db.set_value("Employee", employee.name, "status", "Inactive")
            frappe.db.commit()


def check_expired_dates():
    expired_dates = get_expired_dates()
    hr_manager_msgs = {}
    if expired_dates:
        for row in expired_dates:
            hr_manager_list = frappe.get_list("Employee", fields=["name", "user_id"], filters={"department":row.get("department"), "designation":"HR Manager"})
            if hr_manager_list:
                hr_manager = hr_manager_list[0]
                if hr_manager_msgs.get(hr_manager.user_id):
                    hr_manager_msgs[hr_manager.user_id].append(row)
                else:
                    hr_manager_msgs.update({hr_manager.user_id:[row]})

            send_expired_dates_notifications_for_user(row)
            send_expired_dates_email_for_user(row)
        
        send_expired_dates_notifications_for_hr_manager(hr_manager_msgs)
        send_expired_dates_email_for_hr_manager(hr_manager_msgs)


def get_expired_dates():
    expired_dates = []
    dates_labels = [
        {
            "filedname":"contract_end_date",
            "label": "Contract End Date",
            "msg": "Contract Date Will Expire Soon"
        },
        {
            "filedname":"expire_date",
            "label": "ID Expire Date",
            "msg": "ID Date Will Expire Soon"
        },
        {
            "filedname":"passport_expire",
            "label": "Passport Expire Date",
            "msg": "Passport Date Will Expire Soon"
        },
        {
            "filedname":"insurance_card_expire",
            "label": "Insurance Card Expire",
            "msg": "Insurance Date Will Expire Soon"
        }
    ]
    
    emps = frappe.db.get_list("Employee", filters={"status":"Active"})
    for emp in emps:
        emp_doc = frappe.get_doc("Employee", emp.name)
        for d in dates_labels:
            date = d.get("filedname")
            label = d.get("label")
            if date in ["expire_date", "passport_expire"]:
                table = "identity" if date == "expire_date" else "passport"
                data = emp_doc.get(table)
                if data:
                    for row in data:
                        if row.get(date):
                            diff_days =  row.get(date) - frappe.utils.getdate(today())
                            if diff_days.days == 30:
                                expired_dates.append({
                                    "emp_name": emp_doc.name,
                                    "user": emp_doc.user_id,
                                    "department": emp_doc.department or "",
                                    "subject": label,
                                    "msg": d.get("msg") + ", on " + row.get(date).strftime("%Y-%m-%d"),
                                    "expire_date": row.get(date)
                                })
                            
            else:
                if emp_doc.get(date):
                    diff_days =  emp_doc.get(date) - frappe.utils.getdate(today())
                    if diff_days.days == 30:
                        expired_dates.append({
                            "emp_name": emp_doc.name,
                            "user": emp_doc.user_id,
                            "department": emp_doc.department or "",
                            "subject": label,
                            "msg": d.get("msg") + ", on " + emp_doc.get(date).strftime("%Y-%m-%d"),
                            "expire_date": emp_doc.get(date)
                        })
                    
    return expired_dates

def send_expired_dates_notifications_for_user(data):
    new_doc = frappe.new_doc("Notification Log")
    new_doc.subject = data.get("subject")
    new_doc.for_user = data.get("user")
    new_doc.type = "Alert"
    new_doc.email_content = data.get("msg")
    new_doc.insert()


def send_expired_dates_email_for_user(data):
    hr_settings = frappe.get_doc("HR Notification Settings")
    sender = frappe.get_value("Email Account", hr_settings.notification_default_email, "email_id")

    frappe.sendmail(
        recipients=data.get("user"),
        sender=sender,
        subject=data.get("subject"),
        message=data.get("msg"),
        retry=3,
    )


def send_expired_dates_notifications_for_hr_manager(data):
    for row in data:
        for_user = row
        msg = ""
        for d in data.get(row):
            msg += d.get('msg') + " For User " + d.get('user') + "<br>"
            
        new_doc = frappe.new_doc("Notification Log")
        new_doc.subject = "Employees Document Will be Expired Soon"
        new_doc.for_user = row
        new_doc.type = "Alert"
        new_doc.email_content = msg
        new_doc.insert()

def send_expired_dates_email_for_hr_manager(hr_manager_msgs):
    hr_settings = frappe.get_doc("HR Notification Settings")
    sender = frappe.get_value("Email Account", hr_settings.notification_default_email, "email_id")
    
    for row in hr_manager_msgs:
        for_user = row
        msg = ""
        for d in hr_manager_msgs.get(row):
            msg += d.get('msg') + " For User " + d.get('user') + "<br>"
            
        frappe.sendmail(
            recipients=for_user,
            sender=sender,
            subject=_("Employees Document Will be Expired Soon"),
            message=msg,
            retry=3,
        )
