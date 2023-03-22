# Copyright (c) 2022, AnvilERP and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.installer import update_site_config

from six import iteritems
from frappe.utils.user import add_role

from erpnext.setup.install import create_custom_role, update_select_perm_after_install

class UsersPermissionManager(Document):
    doctypes = [
        {"system_management" : ["System Controller", "Company Controller", "Translation"]},
        {"user_management": ["User", "Users Permission Manager"]},
        {"hr_management": [ "Department", "Branch", "Employee Group", "Designation", "Employee Grade", "Employment Type", "Shift Type", "Shift Builder", "Staffing Plan", "Holiday List", "Leave Type", "Leave Period", "Leave Policy", "Leave Policy Assignment", "Leave Allocation", "Leave Encashment", "Employee Health Insurance", "Leave Block List"]},
        {"employees_list": ["Employee", "End Of Service"]},
        {"self_service": [ "Leave Application","Shift Request","Contact Details","Educational Qualification","Emergency Contact","Health Insurance","Lateness Permission","Personal Details","Salary Details", "Exit Permission"]},
        {"e_form": ["Mosyr Form"]},
        {"timesheet_attendees_management": ["Attendance","Employee Attendance Tool","Attendance Request","Upload Attendance","Employee Checkin"]},
        {"payroll": ["Payroll Settings","Salary Component","Salary Structure","Salary Structure Assignment","Employee Benefit","Employee Deduction","Payroll Entry","Salary Slip","Retention Bonus","Employee Incentive"]},
        {"employees_performance": ["Appraisal", "Appraisal Template"]},
        {"leave": ["Leave Application", "Compensatory Leave Request", "Travel Request", "Leave Encashment"]},
        {"loans" : ["Loan Type", "Loan", "Loan Application"]},
        {"vehicle_management": ["Vehicle", "Vehicle Log", "Vehicle Service"]},
        {"documents_management" : ["Document Manager", "Document Type"]},
        {"custody_management" : ["Custody", "Cash Custody", "Cash Custody Expense"]}
    ]
    
    def validate(self):
        self.flags.ignore_mandatory = 1
        self.user = ''
        self.page_or_report = []
    
    @frappe.whitelist()
    def get_permissions(self, user):
        if user == frappe.session.user: return { 'docs': [] }
        if not frappe.db.exists("User", user): return { 'docs': [] }
        user = frappe.get_doc("User", user)
        if user.name in ['Administrator', 'Guest', 'support@mosyr.io']: return { 'docs': [] }
        if user.user_type == 'SaaS Manager': return { 'docs': [] }
        user_type = frappe.get_doc("User Type", user.user_type)
        if user_type.is_standard: return []


        controller = frappe.get_doc("System Controller")
        permission = {'system_management':[],
                       "user_management":[],
                      "hr_management":[],
                      "employees_list":[],
                      "self_service":[],
                      "e_form":[],
                      "timesheet_attendees_management":[],
                      "payroll":[],
                      "employees_performance":[],
                      "leave":[],
                      "loans":[],
                      "vehicle_management":[],
                      "documents_management":[],
                      "custody_management":[]}
        
        for item in controller.sidebar_item:
            for perm in user_type.user_doctypes:
                if perm.document_type != item.doc_name: continue
                parent = item.parent_name
                if ' ' in item.parent_name:
                    parent = (item.parent_name).replace(" ", "_")
                if '-' in item.parent_name:
                    parent = (item.parent_name).replace("-", "_")
                permission[(parent).casefold()].append(
                    {   "document_type": perm.document_type,
                        "is_custom": perm.is_custom,
                        "read": perm.read,
                        "write": perm.write,
                        "create": perm.create,
                        "submit": perm.submit,
                        "cancel": perm.cancel,
                        "amend": perm.amend,
                        "delete": perm.delete,
                        })
        return {"doctypes":self.doctypes, 
                "permission":[permission],
                'repage': frappe.db.sql(f"SELECT cr.page, cr.report, hr.role FROM `tabCustom Role` cr LEFT JOIN `tabHas Role` hr ON hr.parent=cr.name WHERE hr.role='{user.user_type}'", as_dict=True)
                }

    @frappe.whitelist()
    def apply_permissions(self, user, perms, rps):
        saas = frappe.db.exists("User", {"name": frappe.conf.email_address})
        if saas:
            saas_manager  = frappe.get_doc("User", saas)
            saas_manager.db_set("user_type", "System User")
            frappe.db.commit()
            add_role(saas, "System Manager")
            frappe.db.commit()
        if not frappe.db.exists("User", user): return ""

        # if user == frappe.session.user: return ""
        apply_user = frappe.get_doc("User", user)
        if apply_user.name in ['Administrator', 'Guest', 'support@mosyr.io']: return ""
        if apply_user.user_type == 'SaaS Manager': return ""
        frappe.flags.ignore_permissions = 1
        user_types = self.get_user_types_data(user, perms)
        user_type_limit = {}
        for user_type, data in iteritems(user_types):
            user_type_limit.setdefault(frappe.scrub(user_type), 10000)

        update_site_config("user_type_doctype_limit", user_type_limit)

        new_type = None
        for user_type, data in iteritems(user_types):
            create_custom_role(data)
            new_type = self.create_user_type(user_type, data)
        

        if new_type:
            user = frappe.get_doc("User", user)
            user.db_set("user_type", new_type)
            frappe.db.commit()
            self.delete_old_roles(user.name)
            for rpr in rps:
                args = { 'doctype': 'Custom Role', 'roles': [{'role': user.name, 'parenttype': 'Custom Role'}]}
                if rpr.get('set_role_for', "") == "Report":
                    report_name = rpr.get("page_or_report")
                    args.update({
                        'report': report_name,
                        "ref_doctype": frappe.db.get_value("Report", report_name, "ref_doctype")
                    })
                    self.update_custom_roles({'report': report_name}, args)
                elif rpr.get('set_role_for', "")  == "Page":
                    args.update({
                        'page': rpr.get("page_or_report")
                    })
                    self.update_custom_roles({'page': rpr.get("page_or_report")}, args)

        saas = frappe.db.exists("User", {"name": frappe.conf.email_address})
        if saas:
            saas_manager  = frappe.get_doc("User", saas)
            saas_manager.remove_roles("System User")
            saas_manager.save()
            frappe.db.commit()
            saas_manager.db_set("user_type", "SaaS Manager")
            frappe.db.commit()

        return 'success'
    
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
            for new_role in args.get('roles', []):
                rol = new_role.get('role', False)
                if not rol: continue
                custom_role.append("roles", {
                    'role': rol
                })
            custom_role.flags.ignore_permissions=True
            custom_role.save(ignore_permissions=True)
        else:
            frappe.get_doc(args).insert(ignore_permissions=1)
            

    def get_user_types_data(self, user, perms):
        doctypes_permissions = {
            "Company": ['read'],
        }
        allowed_perms = ['read','write', 'create', 'delete', 'submit', 'cancel', 'amend']
        for doctype in perms:
            document_type = doctype.get("document_type", "")
            if document_type:
                prems = []
                for k, v in doctype.items():
                    if k not in allowed_perms: continue
                    if v == 1:
                        prems.append(k)
                doctypes_permissions.update({
                    f"{document_type}": prems
                })

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
