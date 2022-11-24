
import frappe
from frappe.model.naming import make_autoname

def process_auto_attendance_for_all_shifts():
    shift_list = frappe.get_all("Shift Type", filters={"enable_auto_attendance": "1"}, pluck="name")
    for shift in shift_list:
        doc = frappe.get_cached_doc("Shift Type", shift)
        doc.process_auto_attendance()
    note = frappe.new_doc("Note")
    note.title = make_autoname("NJ.###.###") # "Note Job!"
    note.save()