# Copyright (c) 2022, AnvilERP and contributors
# For license information, please see license.txt
import json

import frappe
from frappe import _

from frappe.model.document import Document
from frappe.model.naming import make_autoname
from frappe.utils import cint

module = "Mosyr Forms"
allow_rename = 0
custom = 1
allowed_fields = (
    "Data",
    "Text Editor",
    "Text",
    "Select",
    "Date",
    "Datetime",
    "Duration",
    "Int",
    "Float",
    "Rating",
    "Attach",
    "Attach Image",
    "Check",
    "Color",
    "Table MultiSelect",
    "Column Break",
    "Section Break",
)


class InvalidOptionsError(frappe.ValidationError):
    pass


class MosyrForm(Document):
    def validate(self):
        self.check_fields(from_validate=True)
        self.check_roles(from_validate=True)

    def autoname(self):
        self.name = make_autoname("MOSYRFRM.YY.MM.DD.#####")

    def check_fields(self, from_validate=False):
        for field in self.fields:
            fieldtype = field.get("fieldtype")
            fieldidx = field.get("idx")
            fieldoptions = field.get("options")

            if fieldtype not in allowed_fields:
                frappe.throw(_("Not Allowed Field Type at row {}".format(fieldidx)))
            # Check Options
            if fieldtype in ["Select", "Table MultiSelect"]:
                clean_opts_checker = ""
                clean_opts = []
                if fieldoptions is not None:
                    clean_opts_checker = f"{fieldoptions}".strip().replace("\n", "")
                if clean_opts_checker == "":
                    frappe.throw(
                        _("Options is Required for {} field.".format(fieldtype))
                    )
                else:
                    if from_validate:
                        for opt in f"{fieldoptions}".split("\n"):
                            opt = f"{opt}".strip()
                            if opt != "":
                                clean_opts.append(opt)
                        field.options = "\n".join(clean_opts)
            else:
                field.options = ""

    def check_roles(self, from_validate=False):
        if cint(self.is_submittable) == 1:
            return
        for perm in self.permissions:
            if from_validate:
                perm.submit = 0
                perm.cancel = 0
                perm.amend = 0
            else:
                if perm.submit == 1 or perm.amend == 1 or perm.cancel == 1:
                    frappe.throw(
                        _("Submit, Cancel, Amend. Allowed for Submittable Form Only.")
                    )

    def on_submit(self):
        self.check_fields()
        self.check_roles()

        clean_fields, title_field = self.prepare_fields()
        self.build_system_doc(clean_fields, title_field)
    
    title_field = ""
    def prepare_fields(self):
        numeric_fields_prop = (
            "length",
            "precision_",
        )
        bool_fields_prop = (
            "non_negative",
            "hide_days",
            "hide_seconds",
            "reqd",
            "in_list_view",
            "bold",
            "collapsible",
            "set_only_once",
            "no_copy",
            "search_index",
        )
        str_fields_props = (
            "label",
            "fieldtype",
            "collapsible_depends_on",
            "options",
            "default",
            "description",
            "depends_on",
            "mandatory_depends_on",
            "non_negative",
            "read_only_depends_on",
        )
        clean_fields = []
        for field in self.fields:
            clean_field = {}
            fieldtype = field.get("fieldtype")
            curfieldname = field.get("name")
            fieldname = f"frmfield_{curfieldname}"
            fieldoptions = field.get("options")

            for prop in numeric_fields_prop:
                val = cint(field.get(f"{prop}", ""))
                prop = prop.replace("_", "")
                clean_field.update({f"{prop}": val})

            for prop in bool_fields_prop:
                val = cint(field.get(f"{prop}", ""))
                # prop = prop.replace("_", "")
                clean_field.update({f"{prop}": val})

            for prop in str_fields_props:
                val = field.get(f"{prop}", "")
                # prop = prop.replace("_", "")
                clean_field.update({f"{prop}": val})
            clean_field.update({"fieldname": fieldname, "options": ""})

            if fieldtype in ["Select", "Table MultiSelect"]:
                clean_opts = ""
                if fieldoptions is not None:
                    clean_opts = f"{fieldoptions}".strip().replace("\n", "")
                if clean_opts == "":
                    frappe.throw(
                        _("Options is Required for {} field.".format(fieldtype))
                    )
                    return
                multiselect_options = []
                for opt in f"{fieldoptions}".split("\n"):
                    opt = f"{opt}".strip()
                    if opt != "":
                        multiselect_options.append(opt)
                if len(multiselect_options) == 0:
                    frappe.throw(
                        _("Options is Required for {} field.".format(fieldtype))
                    )
                    return
                child_name = self.prepare_for_multiselect(multiselect_options)
                clean_field.update({"options": child_name})
            
            # if fieldtype in ["Attach", "Attach Image"]:
            #     clean_field.update({"in_list_view": 0})
            
            if cint(field.get("use_for_title", 0)) == 1 and fieldtype == "Data":
                title_field = fieldname
            clean_fields.append(clean_field)

        return clean_fields, title_field

    def prepare_for_multiselect(self, options):
        doc_name = make_autoname("FRMOPT.YY.MM.DD.#####")
        options_doc = {
            "__newname": doc_name,
            "module": "Mosyr Forms",
            "allow_rename": 1,
            "custom": 1,
            "autoname": "field:title",
            # "permissions": [],
        }
        new_opt_doc = frappe.new_doc("DocType")
        new_opt_doc.update(options_doc)
        new_opt_doc.append(
            "fields",
            {
                "label": "Title",
                "fieldtype": "Data",
                "fieldname": "title",
            },
        )
        new_opt_doc.append("permissions", {"role": "System Manager", "permlevel": "0"})
        new_opt_doc.append(
            "permissions",
            {
                "role": "All",
                "read": 1,
                "select": 1,
                "write": 0,
                "create": 0,
                "delete": 0,
                "export": 1,
                "report": 1,
                "permlevel": "0",
            },
        )
        try:
            new_opt_doc.save(ignore_permissions=True)
            options = set(options)
            for opt in options:
                new_opt = frappe.new_doc(doc_name)
                new_opt.title = f"{opt}"
                new_opt.save()
        except Exception as e:
            frappe.throw(
                _("Error While Prepare Options for MultiSelect field.\n{}".format(e))
            )
            frappe.db.rollback()
            return

        # TODO(3) Make Childtable Withlink
        child_doc_name = make_autoname("FRMCHLD.YY.MM.DD.#####")
        child_doc = {
            "__newname": child_doc_name,
            "module": "Mosyr Forms",
            "allow_rename": allow_rename,
            "custom": custom,
            "istable": 1,
            "editable_grid": 1,
        }
        new_child_doc = frappe.new_doc("DocType")
        new_child_doc.update(child_doc)
        new_child_doc.append(
            "fields",
            {
                "label": "Option",
                "fieldtype": "Link",
                "fieldname": "option",
                "options": new_opt_doc.name,
                "in_list_view": 1,
            },
        )
        try:
            new_child_doc.save(ignore_permissions=True)
        except Exception as e:
            frappe.throw(
                _("Error While Prepare Options for MultiSelect field.\n{}".format(e))
            )
            frappe.db.rollback()
            return
        # else:
        #     frappe.db.commit()

        return child_doc_name

    def build_system_doc(self, clean_fields, title_field):
        erp_doc = {
            "__newname": self.name,
            "module": "Mosyr Forms",
            "allow_rename": 0,
            "custom": 1,
            "is_submittable": self.is_submittable,
            "title_field": title_field,
            "show_name_in_global_search": 1,
        }
        new_erp_doc = frappe.new_doc("DocType")
        new_erp_doc.update(erp_doc)
        for field in clean_fields:
            new_erp_doc.append("fields", field)
        # new_erp_doc.append("permissions", {"role": "System Manager", "permlevel": "0"})
        for perm in self.permissions:
            new_erp_doc.append(
                "permissions",
                {
                    "role": perm.role,
                    "if_owner": perm.if_owner,
                    "permlevel": 0,
                    "select": perm.select,
                    "read": perm.read,
                    "write": perm.write,
                    "create": perm.create,
                    "delete": perm.delete,
                    "submit": perm.submit,
                    "cancel": perm.cancel,
                    "amend": perm.amend,
                    "report": perm.report,
                    "export": perm.export,
                    "import": perm.get("import", 0),
                    "set_user_permissions": perm.set_user_permissions,
                    "share": perm.share,
                    "print": perm.print,
                    "email": perm.email,
                },
            )

        try:
            attatched_req = []
            for idx, field in enumerate(new_erp_doc.fields):
                if field.fieldtype in ["Attach", "Attach Image"] and cint(field.reqd) == 1:
                    field.in_list_view = 0
                    field.reqd = 0
                    attatched_req.append(idx)
            new_erp_doc.save(ignore_permissions=True)
            for att_req in attatched_req:
                new_erp_doc.fields[att_req].reqd = 1
            new_erp_doc.save(ignore_permissions=True)
            self.prepare_trans_for_docname(self.name, self.form_title)
            frappe.db.commit()
        except Exception as e:
            frappe.throw(
                _("Error While Prepare Options for MultiSelect field.\n{}".format(e))
            )
            frappe.db.rollback()
            return

    def use_name_as_fieldname_in_childtable(self, doc):
        fields = []
        for field in doc.fields:
            field.update({"fieldname": field.name})
            fields.append(field)
        return fields

    def prepare_trans_for_docname(self, text, transtext):
        trans_to_lang = ["en", "ar"]
        sys_lang = l = frappe.get_value(
            "System Settings", "System Settings", "language"
        )
        if sys_lang not in trans_to_lang:
            trans_to_lang.append(sys_lang)

        for lang in trans_to_lang:
            trans_doc = frappe.new_doc("Translation")
            trans_doc.language = lang
            trans_doc.source_text = f"{text}"
            trans_doc.translated_text = f"{transtext}"
            trans_doc.flags.ignore_mandatory = True
            trans_doc.flags.ignore_validate = True
            # trans_doc.flags.ignore_permissions = True
            trans_doc.save(ignore_permissions=True)
        frappe.db.commit()
    
    def on_cancel(self):
        # Delete only Created Docs from the form ( Custom DocType)
        # Child Table ==> start with FRMCHLD
        # Base Docs   ==> start with FRMOPT
        system_doc = frappe.db.exists("DocType", self.name)
        if system_doc:
            system_doc = frappe.get_doc("DocType", system_doc)
            if system_doc.custom == 0: return
            for field in system_doc.fields:
                if field.fieldtype != "Table MultiSelect": continue
                self.clear_child_doc(field.options)
            system_doc.delete()
            frappe.db.commit()
                
    
    def clear_child_doc(self, options):
        child_doc = frappe.db.exists("DocType", options)
        if child_doc and f"{options}".startswith("FRMCHLD"):
            child_doc = frappe.get_doc("DocType", child_doc)
            if child_doc.custom == 0: return
            for field in child_doc.fields:
                if field.fieldtype != "Link": continue
                linked_doc = frappe.db.exists("DocType", field.options)
                if linked_doc and f"{field.options}".startswith("FRMOPT"):
                    linked_doc = frappe.get_doc("DocType", field.options)
                    if linked_doc.custom == 0: continue
                    linked_doc.delete()
            child_doc.delete()
