
import frappe

def process_auto_attendance_for_all_shifts():

    shift_list = frappe.get_all("Shift Type", filters={"enable_auto_attendance": "1"}, pluck="name")
    for shift in shift_list:
        doc = frappe.get_doc("Shift Type", shift)
        try: doc.process_auto_attendance()
        except Exception as e: pass
    frappe.db.commit()
