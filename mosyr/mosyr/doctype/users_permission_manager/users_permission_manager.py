# Copyright (c) 2022, AnvilERP and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.installer import update_site_config

from six import iteritems
from frappe.utils.user import add_role

from erpnext.setup.install import create_custom_role, update_select_perm_after_install
from frappe.permissions import add_permission, update_permission_property
from frappe.utils import cint
from frappe.utils import unique
class UsersPermissionManager(Document):
    doctypes = {
        "system_management": [{"document_type": "Company"}],
        "user_management": [
            {"document_type": "User"},
            {"document_type": "Users Permission Manager"},
        ],
        "hr_management": [
            {"document_type": "Department"},
            {"document_type": "Branch"},
            {"document_type": "Employee Group"},
            {"document_type": "Designation"},
            {"document_type": "Employee Grade"},
            {"document_type": "Employment Type"},
            {"document_type": "Shift Type"},
            {"document_type": "Shift Builder"},
            {"document_type": "Staffing Plan"},
            {"document_type": "Holiday List"},
            {"document_type": "Leave Type"},
            {"document_type": "Leave Period"},
            {"document_type": "Leave Policy"},
            {"document_type": "Leave Policy Assignment"},
            {"document_type": "Leave Allocation"},
            {"document_type": "Leave Encashment"},
            {"document_type": "Employee Health Insurance"},
            {"document_type": "Leave Block List"},
        ],
        "employees_list": [
            {"document_type": "Employee"},
            {"document_type": "End Of Service"},
        ],
        "self_service": [
            {"document_type": "Leave Application"},
            {"document_type": "Shift Request"},
            {"document_type": "Contact Details"},
            {"document_type": "Educational Qualification"},
            {"document_type": "Emergency Contact"},
            {"document_type": "Health Insurance"},
            {"document_type": "Lateness Permission"},
            {"document_type": "Personal Details"},
            {"document_type": "Salary Details"},
            {"document_type": "Exit Permission"},
        ],
        "e_form": [{"document_type": "Mosyr Form"}],
        "timesheet_attendees_management": [
            {"document_type": "Attendance"},
            {"document_type": "Employee Attendance Tool"},
            {"document_type": "Attendance Request"},
            {"document_type": "Upload Attendance"},
            {"document_type": "Employee Checkin"},
        ],
        "payroll": [
            {"document_type": "Payroll Settings"},
            {"document_type": "Salary Component"},
            {"document_type": "Salary Structure"},
            {"document_type": "Salary Structure Assignment"},
            {"document_type": "Employee Benefit"},
            {"document_type": "Employee Deduction"},
            {"document_type": "Payroll Entry"},
            {"document_type": "Salary Slip"},
            {"document_type": "Retention Bonus"},
            {"document_type": "Employee Incentive"},
        ],
        "employees_performance": [
            {"document_type": "Appraisal"},
            {"document_type": "Appraisal Template"},
        ],
        "leave": [
            {"document_type": "Leave Application"},
            {"document_type": "Compensatory Leave Request"},
            {"document_type": "Travel Request"},
            {"document_type": "Leave Encashment"},
        ],
        "loans": [
            {"document_type": "Loan Type"},
            {"document_type": "Loan"},
            {"document_type": "Loan Application"},
        ],
        "vehicle_management": [
            {"document_type": "Vehicle"},
            {"document_type": "Vehicle Log"},
            {"document_type": "Vehicle Service"},
        ],
        "documents_management": [
            {"document_type": "Document Manager"},
            {"document_type": "Document Type"},
        ],
        "custody_management": [
            {"document_type": "Custody"},
            {"document_type": "Cash Custody"},
            {"document_type": "Cash Custody Expense"},
        ],
    }

    def onload(self):
        for key, docs in self.doctypes.items():
            for doc in docs:
                self.append(f"{key}", doc)

    def validate(self):
        self.flags.ignore_mandatory = 1
        self.user = ""
        self.page_or_report = []
        for k in self.doctypes.keys():
            self.set(k, [])

    @frappe.whitelist()
    def get_permissions(self, user):
        for k in self.doctypes.keys():
            self.set(k, [])
        
        if user == frappe.session.user:
            return {"doctypes": [], "repage": [], "permission": []}
        if not frappe.db.exists("User", user):
            return {"doctypes": [], "repage": [], "permission": []}
        user = frappe.get_doc("User", user)

        if user.name in ["Administrator", "Guest", "support@mosyr.io"]:
            return {"doctypes": [], "repage": [], "permission": []}

        user_roles = []
        user_roles.append(f"'{user.name}'")
        if len(user_roles) > 0:
            user_roles = ", ".join(user_roles)
        else:
            user_roles = ""

        docs = []
        for docss in self.doctypes.values():
            for doc in docss:
                doc = doc.get("document_type")
                if not doc:
                    continue
                docs.append(f"'{doc}'")
        if len(docs) > 0:
            docs = ", ".join(docs)
        else:
            docs = ""

        roles = frappe.db.sql(
            f"SELECT * FROM `tabDocPerm` WHERE role in ({user_roles}) and parent in ({docs})",
            as_dict=True,
        )
        croles = frappe.db.sql(
            f"SELECT * FROM `tabCustom DocPerm` WHERE role in ({user_roles}) and parent in ({docs})",
            as_dict=True,
        )
        roles += croles
        for r in croles:
            doctype = r.parent
            for k, v in self.doctypes.items():
                for idx, d in enumerate(v):
                    if doctype == d.get("document_type"):
                        if doctype == "Company":
                            continue
                        c = {
                            "document_type": doctype,
                            "is_custom": r.is_custom or 0,
                            "read": r.read,
                            "write": r.write,
                            "create": r.create,
                            "submit": r.submit,
                            "cancel": r.cancel,
                            "amend": r.amend,
                            "delete": r.delete,
                            "only_me": r.if_owner,
                        }
                        v[idx] = c
        
        for key, docs in self.doctypes.items():
            for doc in docs:
                self.append(f"{key}", doc)
                
        return "done"
    @frappe.whitelist()
    def add_role_for_user(self, user):
        user = frappe.get_doc("User", self.user)
        if not frappe.db.exists("Role", user.name):
            new_role = frappe.new_doc("Role")
            new_role.role_name = user.name
            new_role.insert()
            new_role.save()
            user = frappe.get_doc("User", self.user)
            user.add_roles(user.name)
    @frappe.whitelist()
    def apply_permissions(self, user, perms, rps):
        # if not self.user:
        #     return
        # if not frappe.db.exists("User", self.user):
        #     return
        
        # profile_doc = frappe.get_doc("Role Profile", profile)
        # roles = [ d.role for d in profile_doc.roles ]
        # if user.name in ["Administrator", "Guest", "support@mosyr.io"] or user.role_profile_name == "SaaS Manager":
        #     return
        # Check user profile
        # if frappe.db.exists("Role Profile", self.user):
        #     profile = frappe.get_doc("Role Profile", self.user)
        # else:
        #     profile = frappe.new_doc("Role Profile")
        #     profile.role_profile = self.user
            
        
        # if frappe.db.exists("Role", self.user):
        #     role = frappe.get_doc("Role", self.user)
        # else:
        #     role = frappe.new_doc("Role")
        #     role.role_name = self.user
        #     role.save()
        #     frappe.db.commit()
        self.add_role_for_user(self.user)
        user = frappe.get_doc("User", self.user)
        role_profile_name = user.role_profile_name

        for key in self.doctypes.keys():
            for doc in self.get(key, []):
                frappe.db.sql(f"DELETE FROM `tabCustom DocPerm` WHERE role='{user.name}' and parent='{doc.document_type}'")
                frappe.db.commit()
                if (cint(doc.read) > 0 or cint(doc.write) > 0 or cint(doc.create) > 0 
                    or cint(doc.submit) > 0 or cint(doc.cancel) > 0 or cint(doc.amend) > 0 
                    or cint(doc.delete) > 0):
                    frappe.db.sql(f"DELETE FROM `tabCustom DocPerm` WHERE role='{role_profile_name}' and parent='{doc.document_type}'")
                    frappe.db.sql(f"DELETE FROM `tabCustom DocPerm` WHERE role='Employee Self Service' and parent='{doc.document_type}'")
                    frappe.db.commit()
                    
                    frappe.get_doc(
                        {
                            "doctype": "Custom DocPerm",
                            "role": user.name,
                            "read": doc.read,
                            "write": doc.write,
                            "create": doc.create,
                            "delete": doc.delete,
                            "submit": doc.submit,
                            "cancel": doc.cancel,
                            "amend": doc.amend,
                            "parent": doc.document_type,
                            "if_owner": doc.only_me
                        }
                    ).insert(ignore_permissions=True)
                    frappe.get_doc(
                        {
                            "doctype": "Custom DocPerm",
                            "role": role_profile_name,
                            "read": doc.read,
                            "write": doc.write,
                            "create": doc.create,
                            "delete": doc.delete,
                            "submit": doc.submit,
                            "cancel": doc.cancel,
                            "amend": doc.amend,
                            "parent": doc.document_type,
                            "if_owner":1
                        }
                    ).insert(ignore_permissions=True)
                    frappe.get_doc(
                        {
                            "doctype": "Custom DocPerm",
                            "role": 'Employee Self Service',
                            "read": doc.read,
                            "write": doc.write,
                            "create": doc.create,
                            "delete": doc.delete,
                            "submit": doc.submit,
                            "cancel": doc.cancel,
                            "amend": doc.amend,
                            "parent": doc.document_type,
                            "if_owner": 1
                        }
                    ).insert(ignore_permissions=True)


        # profile.roles = []
        # profile.append("roles", {
        #     "role": role.name
        # })
        # profile.append("roles", {
        #     "role": "HR Notification"
        # })
        # profile.append("roles", {
        #     "role": "Mosyr Forms"
        # })
        # profile.save()
        # frappe.db.commit()
    
        # user.role_profile_name = profile.name
        # user.reload()
        # user.save()
        # frappe.flags.ignore_permissions = 1
        # user_types = self.get_user_types_data(user, perms)
        # user_type_limit = {}
        # for user_type, data in iteritems(user_types):
        #     user_type_limit.setdefault(frappe.scrub(user_type), 10000)

        # update_site_config("user_type_doctype_limit", user_type_limit)

        # new_type = None
        # for user_type, data in iteritems(user_types):
        #     create_custom_role(data)
        #     new_type = self.create_user_type(user_type, data)

        # if new_type:
        #     user = frappe.get_doc("User", user)
        #     user.db_set("user_type", new_type)
        #     frappe.db.commit()
        #     self.delete_old_roles(user.name)
        #     for rpr in rps:
        #         args = {
        #             "doctype": "Custom Role",
        #             "roles": [{"role": user.name, "parenttype": "Custom Role"}],
        #         }
        #         if rpr.get("set_role_for", "") == "Report":
        #             report_name = rpr.get("page_or_report")
        #             ref_doctype = frappe.db.get_value(
        #                 "Report", report_name, "ref_doctype"
        #             )
        #             args.update({"report": report_name, "ref_doctype": ref_doctype})
        #             self.update_custom_roles({"report": report_name}, args)
        #             add_permission(ref_doctype, user.name, permlevel=0)
        #             update_permission_property(
        #                 ref_doctype, user.name, permlevel=0, ptype="report", value=1
        #             )
        #         elif rpr.get("set_role_for", "") == "Page":
        #             args.update({"page": rpr.get("page_or_report")})
        #             self.update_custom_roles({"page": rpr.get("page_or_report")}, args)

        # saas = frappe.db.exists("User", {"name": frappe.conf.email_address})
        # if saas:
        #     saas_manager = frappe.get_doc("User", saas)
        #     saas_manager.remove_roles("System User")
        #     saas_manager.save(ignore_permissions=True)
        #     frappe.db.commit()
        #     saas_manager.db_set("user_type", "SaaS Manager")
        #     frappe.db.commit()

        return "success"

    def delete_old_roles(self, user_role):
        for custom_role in frappe.get_all("Custom Role"):
            custom_role = frappe.get_doc("Custom Role", custom_role.name)
            custom_role.flags.ignore_permissions = 1
            for role in custom_role.roles:
                if role.role == user_role:
                    doc = frappe.get_doc("Has Role", role.name)
                    doc.flags.ignore_permissions = 1
                    doc.delete()
        frappe.db.commit()

    def update_custom_roles(self, role_args, args):
        name = frappe.db.get_value("Custom Role", role_args, "name")
        if name:
            custom_role = frappe.get_doc("Custom Role", name)
            for new_role in args.get("roles", []):
                rol = new_role.get("role", False)
                if not rol:
                    continue
                custom_role.append("roles", {"role": rol})
            custom_role.flags.ignore_permissions = True
            custom_role.save(ignore_permissions=True)
        else:
            frappe.get_doc(args).insert(ignore_permissions=1)

    def get_user_types_data(self, user, perms):
        doctypes_permissions = {
            "Company": ["read"],
        }
        allowed_perms = [
            "read",
            "write",
            "create",
            "delete",
            "submit",
            "cancel",
            "amend",
        ]
        for doctype in perms:
            document_type = doctype.get("document_type", "")
            if document_type:
                prems = []
                for k, v in doctype.items():
                    if k not in allowed_perms:
                        continue
                    if v == 1:
                        prems.append(k)
                doctypes_permissions.update({f"{document_type}": prems})

        return {
            f"{user}": {
                "role": f"{user}",
                "apply_user_permission_on": "Employee",
                "user_id_field": "user_id",
                "doctypes": doctypes_permissions,
            }
        }

    def create_user_type(self, user_type, data):
        if frappe.db.exists("User Type", user_type):
            doc = frappe.get_cached_doc("User Type", user_type)
            doc.user_doctypes = []
        else:
            doc = frappe.new_doc("User Type")
            doc.update(
                {
                    "name": user_type,
                    "role": data.get("role"),
                    "user_id_field": data.get("user_id_field"),
                    "apply_user_permission_on": data.get("apply_user_permission_on"),
                }
            )
        self.flags.ignore_permissions = 1
        create_role_permissions_for_doctype(doc, data)

        update_select_perm_after_install()

        return doc.name


def create_role_permissions_for_doctype(doc, data):
    for doctype, perms in iteritems(data.get("doctypes")):
        args = {"document_type": doctype}
        if len(perms) > 0:
            for perm in perms:
                args[perm] = 1
            doc.append("user_doctypes", args)
    doc.save(ignore_permissions=True)
    frappe.db.commit()



def check_user_role(user, role):
    user_roles = frappe.get_roles(user)
    for role in user_roles:
        frappe.msgprint(f"{role}")
    return role in user_roles