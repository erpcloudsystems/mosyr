
import frappe
from frappe.core.doctype.user_type.user_type import UserType
class CustomUserType(UserType):
    def add_role_permissions_for_user_doctypes(self):
        perms = ["read", "write", "create", "submit", "cancel", "amend", "delete"]
        for row in self.user_doctypes:
            docperm = add_custom_role_permissions(row.document_type, self.role)

            values = {perm: row.get(perm) or 0 for perm in perms}
            for perm in ["print", "email", "share"]:
                values[perm] = 1

            frappe.db.set_value("Custom DocPerm", docperm, values)

def add_custom_role_permissions(doctype, role):
    name = frappe.get_value("Custom DocPerm", dict(parent=doctype, role=role, permlevel=0))

    if not name:
        name = add_custom_permission(doctype, role, 0)

    return name

def add_custom_permission(doctype, role, permlevel=0, ptype=None):
    """Add a new permission rule to the given doctype
    for the given Role and Permission Level"""
    from frappe.core.doctype.doctype.doctype import validate_permissions_for_doctype
    from frappe.permissions import setup_custom_perms

    setup_custom_perms(doctype)

    if frappe.db.get_value(
        "Custom DocPerm", dict(parent=doctype, role=role, permlevel=permlevel, if_owner=0)
    ):
        return

    if not ptype:
        ptype = "read"

    custom_docperm = frappe.get_doc(
        {
            "doctype": "Custom DocPerm",
            "__islocal": 1,
            "parent": doctype,
            "parenttype": "DocType",
            "parentfield": "permissions",
            "role": role,
            "permlevel": permlevel,
            ptype: 1,
        }
    )

    custom_docperm.save(ignore_permissions=1)

    validate_permissions_for_doctype(doctype)
    return custom_docperm.name