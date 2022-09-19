from datetime import timedelta

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import cint, flt, formatdate, getdate

from erpnext.hr.utils import validate_active_employee
    
def share_doc_with_approver(doc, user):
    # if approver does not have permissions, share
    if not frappe.has_permission(doc=doc, ptype="submit", user=user):
        frappe.share.add(doc.doctype, doc.name, user, submit=1, flags={"ignore_share_permission": True})

        frappe.msgprint(
            _("Shared with the user {0} with {1} access").format(user, frappe.bold("submit"), alert=True)
        )

    # remove shared doc if approver changes
    doc_before_save = doc.get_doc_before_save()
    if doc_before_save:
        approvers = {
            "Leave Application": "leave_approver",
            "Expense Claim": "expense_approver",
            "Shift Request": "approver",
            "Lateness Permission": "approver",
        }

        approver = approvers.get(doc.doctype)
        if doc_before_save.get(approver) != doc.get(approver):
            frappe.share.remove(doc.doctype, doc.name, doc_before_save.get(approver))


class OverlapError(frappe.ValidationError):
    pass

class LatenessPermission(Document):
    def validate(self):
        validate_active_employee(self.employee)
        self.validate_dates()
        self.validate_overlap_dates()
        self.validate_approver()

    def on_update(self):
        share_doc_with_approver(self, self.approver)

    def on_submit(self):
        if self.status not in ["Approved", "Rejected"]:
            frappe.throw(_("Only Lateness Permission with status 'Approved' and 'Rejected' can be submitted"))
        
        if self.status == "Approved":
            assigned_shift = ""
            default_shift = frappe.db.get_value("Employee", self.employee, 'default_shift')
            
            shift_type = None
            
            if assigned_shift:  shift_type = assigned_shift
            elif default_shift: shift_type = default_shift
            if not shift_type: return

            shift_type = frappe.get_doc("Shift Type", shift_type)
            
            # TODO(1) Check attendance status if enable_auto_attendance=0
            if cint(shift_type.enable_auto_attendance) == 0: return

            new_shift_type = None

            new_shift_type = frappe.copy_doc(shift_type)
            seconds = cint(shift_type.start_time.seconds) + cint(self.lateness_hours * 60 * 60)
            new_shift_type.start_time = timedelta(seconds=seconds)
            new_shift_type.save()
            frappe.db.commit()

            assignment_doc = frappe.new_doc("Shift Assignment")
            assignment_doc.company = self.company
            assignment_doc.shift_type = new_shift_type.name
            assignment_doc.employee = self.employee
            assignment_doc.start_date = self.from_date
            if self.to_date:
                assignment_doc.end_date = self.to_date
            else:
                assignment_doc.end_date = self.from_date
            assignment_doc.lateness_permission = self.name
            assignment_doc.flags.ignore_permissions = 1
            assignment_doc.insert()
            assignment_doc.submit()

            frappe.msgprint(
                _("Shift Assignment: {0} created for Employee: {1}").format(
                    frappe.bold(assignment_doc.name), frappe.bold(self.employee)
                )
            )

    def on_cancel(self):
        shift_assignment_list = frappe.get_list(
            "Shift Assignment", {"employee": self.employee, "lateness_permission": self.name}
        )
        if shift_assignment_list:
            for shift in shift_assignment_list:
                shift_assignment_doc = frappe.get_doc("Shift Assignment", shift["name"])
                shift_assignment_doc.cancel()

    def validate_approver(self):
        department = frappe.get_value("Employee", self.employee, "department")
        shift_approver = frappe.get_value("Employee", self.employee, "shift_request_approver")
        approvers = frappe.db.sql(
            """select approver from `tabDepartment Approver` where parent= %s and parentfield = 'shift_request_approver'""",
            (department),
        )
        approvers = [approver[0] for approver in approvers]
        approvers.append(shift_approver)
        if self.approver not in approvers:
            frappe.throw(_("Only Approvers can Approve this Request."))

    def validate_dates(self):
        if self.from_date and self.to_date and (getdate(self.to_date) < getdate(self.from_date)):
            frappe.throw(_("To date cannot be before from date"))
        
        if flt(self.lateness_hours) <= 0:
            frappe.throw(_("Lateness hours cannot be zero"))

    def validate_overlap_dates(self):
        if not self.name:
            self.name = "New Lateness Permission"
        d = frappe.db.sql(
            """
                select
                    name, from_date, to_date
                from `tabLateness Permission`
                where employee = %(employee)s and docstatus < 2
                and ((%(from_date)s >= from_date
                    and %(from_date)s <= to_date) or
                    ( %(to_date)s >= from_date
                    and %(to_date)s <= to_date ))
                and name != %(name)s""",
            {
                "employee": self.employee,
                "from_date": self.from_date,
                "to_date": self.to_date,
                "name": self.name,
            },
            as_dict=1,
        )

        for date_overlap in d:
            if date_overlap["name"]:
                self.throw_overlap_error(date_overlap)

    def throw_overlap_error(self, d):
        msg = _("Employee {0} has already applied for Lateness between {1} and {2} : ").format(
            self.employee, formatdate(d["from_date"]), formatdate(d["to_date"])
        ) + """ <b><a href="/app/Form/Lateness Permission/{0}">{0}</a></b>""".format(d["name"])
        frappe.throw(msg, OverlapError)

