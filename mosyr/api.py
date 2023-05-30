
import json

import frappe 
from frappe.utils import nowdate, getdate, today, flt, cint, date_diff
from frappe import _
from hijri_converter import Hijri, Gregorian
from json import loads
from frappe.utils import get_datetime, get_url

def _get_employee_from_user(user):
    employee_docname = frappe.db.exists(
        {'doctype': 'Employee', 'user_id': user})

    if not employee_docname:
        frappe.throw(_('Employee NOT Found'))

    if employee_docname:
        return frappe.get_doc('Employee', employee_docname[0][0]).name
    return None

@frappe.whitelist()
def get_will_expire_docs():
    notify_settings = frappe.get_doc("HR Notification Settings")
    now = nowdate()

    # Get Employee Contracts that will be expired 
    expire_contracts = frappe.db.sql("""
        SELECT 
            name
        FROM
            `tabEmployee Contract`
        WHERE 
            docstatus = 1 AND contract_status = "Valid" AND DATEDIFF(contract_end_date, %(now)s) BETWEEN 0 AND %(diff_day)s
    """, {"now":now, "diff_day": notify_settings.for_contracts_notice_me_before}, as_dict=True)

    # Get Identities that will be expired 
    expire_identities = frappe.db.sql("""
        SELECT 
            name
        FROM
            `tabIdentity`
        WHERE 
            DATEDIFF(expire_date, %(now)s) BETWEEN 0 AND %(diff_day)s
    """, {"now":now, "diff_day": notify_settings.for_ids__notice_me_before}, as_dict=True)

    # Get Passports that will be expired 
    expire_passports = frappe.db.sql("""
        SELECT 
            name
        FROM
            `tabPassport`
        WHERE 
            DATEDIFF(passport_expire, %(now)s) BETWEEN 0 AND %(diff_day)s
    """, {"now":now, "diff_day": notify_settings.for_passports_notice_me_before}, as_dict=True)

    # Get Insurances that will be expired 
    expire_Insurances = frappe.db.sql("""
        SELECT 
            name, health_insurance_no
        FROM
            `tabEmployee`
        WHERE 
            DATEDIFF(insurance_card_expire, %(now)s) BETWEEN 0 AND %(diff_day)s
    """, {"now":now, "diff_day": notify_settings.for_insurance_notice_me_before}, as_dict=True)

    return {
            "expire_contracts":expire_contracts, 
            "expire_identities":expire_identities, 
            "expire_passports":expire_passports,
            "expire_Insurances": expire_Insurances
        }

@frappe.whitelist()
def show_expier_docs():
    notify_settings = frappe.get_doc("HR Notification Settings")
    if notify_settings.notify_after_login:
        result = get_will_expire_docs()
        expire_contracts = result.get("expire_contracts")
        expire_identities = result.get("expire_identities")
        expire_passports = result.get("expire_passports")
        expire_Insurances = result.get("expire_Insurances")
        
        msg = ""
        print_msg = False

        if len(expire_contracts): 
            msg += f"{len(expire_contracts)} Contracts Expire Within {notify_settings.for_contracts_notice_me_before} <br>"
            print_msg = True

        if len(expire_identities):
            msg += f" {len(expire_identities)} ID's Expire Within {notify_settings.for_ids__notice_me_before} <br> "
            print_msg = True

        if len(expire_passports):
            msg += f"{len(expire_passports)} Passport Expire Within {notify_settings.for_passports_notice_me_before} <br>"
            print_msg = True

        if len(expire_Insurances):
            msg += f"{len(expire_Insurances)} Insurances Expire Within {notify_settings.for_insurance_notice_me_before}"
            print_msg = True
        
        if print_msg:
            frappe.msgprint(_(msg), title= _('Employee Docs that will be expired'), indicator= 'orange')

@frappe.whitelist()
def set_employee_approvers(department):
    ''' Fetch Aprrovers From Department & Set it in Employee Page Depends on Department Field'''
    if department:
        leave_approver = expense_approver = shift_req_approver = ''
        department = frappe.get_doc('Department', department)
        
        if len(department.leave_approvers):
            leave_approver = department.leave_approvers[0].approver
            leave_approver = leave_approver
        if len(department.expense_approvers):
            expense_approver = department.expense_approvers[0].approver
            expense_approver = expense_approver

        if len(department.shift_request_approver):
            shift_req_approver = department.shift_request_approver[0].approver
            shift_req_approver = shift_req_approver

        return leave_approver, expense_approver, shift_req_approver

@frappe.whitelist()
def convert_date(gregorian_date=None, hijri_date=None):
    if gregorian_date:
        gd, gm, gy = getdate(gregorian_date).day, getdate(gregorian_date).month, getdate(gregorian_date).year
        hijri = Gregorian(gy, gm, gd).to_hijri()
        return str(hijri)

    if hijri_date:
        hd, hm, hy = getdate(hijri_date).day, getdate(hijri_date).month, getdate(hijri_date).year
        gregorian = Hijri(hy, hm, hd ).to_gregorian()
        return str(gregorian)

def validate_social_insurance(doc, method):
    comapny_data = frappe.db.sql("""SELECT * FROM `tabCompany`""", as_dict=1)
    social_type = doc.social_insurance_type
    # if f"{doc.nationality}".lower() in ["saudi", "سعودي", "سعودى"] else "Non Saudi"
    if len(comapny_data) > 0:
        comapny_data = comapny_data[0]
        doc.social_insurance_type = social_type
        
        if social_type == "Saudi":
            doc.risk_on_employee = 0
            doc.risk_on_company = 0
            doc.pension_on_employee = flt(comapny_data.pension_percentage_on_employee)
            doc.pension_on_company = flt(comapny_data.pension_percentage_on_company)
        else:
            doc.risk_on_employee = flt(comapny_data.risk_percentage_on_employee)
            doc.risk_on_company = flt(comapny_data.risk_percentage_on_company)
            doc.pension_on_employee = 0
            doc.pension_on_company = 0
    else:
        doc.social_insurance_type = "Other"
        doc.risk_on_employee = 0
        doc.risk_on_company = 0
        doc.pension_on_employee = 0
        doc.pension_on_company = 0

def notify_expired_dates(doc, method):
    emp = doc
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

def check_other_annual_leaves(doc, method):
    if cint(doc.is_annual_leave) == 1 and cint(doc.allow_encashment) == 1:
        leaves = frappe.get_list("Leave Type", filters={"is_annual_leave": 1, "allow_encashment": 1})
        #frappe.db.sql("""SELECT name FROM `tabLeave Type` WHERE is_annual_leave=1 AND allow_encashment=1""")
        if len(leaves) >= 1:
            msg_str = ""
            for l in leaves:
                msg_str += "<li>{}</li>".format(_(l['name']))
            msg_str = "<ul>" + msg_str + "</ul>"
            frappe.throw(_("Only One Annual Leave allowed to be encashment check.")+msg_str)

def set_employee_gender(doc, method):
    gender_doc = frappe.db.exists("Gender", doc.e_gender)
    if gender_doc:
        doc.gender = gender_doc
    else:
        gender_doc = frappe.new_doc("Gender")
        gender_doc.gender = doc.e_gender
        gender_doc.save()
        frappe.db.commit()
        doc.gender = gender_doc.name

@frappe.whitelist(allow_guest=True)
def add_employee_log(*args, **kwargs):
    logs_data =frappe.request.data.decode()
    if isinstance(logs_data, str):
        logs_data = json.loads(logs_data)
    logs_data = logs_data.get("logs", [])
    errors = []
    success = []
    
    if isinstance(logs_data, list):
        for log in logs_data:
            log_id = log.get("log_id", False)
            
            if log_id:
                # Extract data from log
                employee_field_value = log.get("employee_field_value", False)
                device_id = log.get("device_id", "")
                timestamp = log.get("timestamp", False)
                log_type = log.get("log_type", '-')
                if not employee_field_value or not timestamp:
                    errors.append({
                        "log_id": log_id,
                        "result": "Employee Id or Chickin datetime"
                    })
                    continue
                employee = frappe.db.get_values(
                    "Employee",{"attendance_device_id": employee_field_value},
                    ["name", "employee_name", "attendance_device_id"], as_dict=True,)
                if employee:
                    employee = employee[0]
                else:
                    errors.append({
                        "log_id": log_id,
                        "result": "no employee found for {}".format(employee_field_value or "")
                    })
                    continue
                if not isinstance(log_type, str):
                    log_type = None
                else:
                    log_type = f'{log_type}'.upper()
                
                if log_type in ['0', 0, 'IN']:
                    log_type = "IN"
                elif log_type in ['1', 1, 'OUT']:
                    log_type = "OUT"
                else:
                    log_type = None

                frappe.logger("mosyr.biometric").debug({"resuest_data":" [!] logs_data"})
                doc = frappe.new_doc("Employee Checkin")
                doc.employee = f'{employee.name}'
                doc.employee_name = f'{employee.employee_name}'
                doc.time = get_datetime(timestamp)
                doc.device_id = f'{device_id}'
                doc.log_type = log_type
                try:
                    doc.insert(ignore_permissions=True)
                    success.append({
                        "log_id": log_id,
                        "result": "success"
                    })
                except Exception as e:
                    errors.append({
                        "log_id": log_id,
                        "result": e
                    })
    return {
        "errors": errors,
        "success": success,
    }

def translate_employee(doc,method):
    tr = False
    if doc.is_new():
        tr = frappe.new_doc("Translation")
    else:
        old_doc = doc.get_doc_before_save()
        if doc.full_name_en and doc.full_name_en != old_doc.full_name_en:
            tr = frappe.new_doc("Translation")
    if not tr: return

    tr.language = "en"
    tr.source_text = doc.first_name
    tr.translated_text = doc.full_name_en
    tr.flags.ignore_permissions = True
    tr.insert(ignore_permissions=True)

@frappe.whitelist()
def get_doctypes(doctype, txt, searchfield, start, page_len, filters):
    result = frappe.db.sql("""
        select doc_name,parent_name from `tabSideBar Item Table`
        where doc_name LIKE %(txt)s or parent_name LIKE %(txt)s""" ,{"txt": "%" + txt + "%"})
    return result

def set_user_type(doc,method):
    role = frappe.db.exists("Role", "Mosyr Forms")
    if role:
        doc.add_roles("Mosyr Forms")
        doc.save(ignore_permissions=True)
        frappe.db.commit()
    if doc.email != "Administrator":
        doc.db_set("user_type","Employee Self Service")
        frappe.db.commit()

def set_employee_number(doc,method):
    doc.employee_number = doc.number

def set_date_of_joining(doc,method):
    doc.date_of_joining = doc.custom_date_of_joining

@frappe.whitelist()
def get_roles(doctype, txt, searchfield, start, page_len, filters):
    result = frappe.db.sql("""
        select name from `tabRole`
        where is_custom = 1 and name LIKE %(txt)s  LIKE %(txt)s""" ,{"txt": "%" + txt + "%"})
    return result

def validate_remaining_loan(doc,method):
    loan_doc = frappe.get_doc("Loan", doc.against_loan)
    if loan_doc.total_payment - loan_doc.total_amount_paid == 0:
        frappe.throw(f"The Remaining in this loan equal zero")
    if loan_doc.total_amount_paid + doc.amount_paid >  loan_doc.total_payment:
        frappe.throw(f"Remaining in your loan is {loan_doc.total_amount_remaining}, Not {doc.amount_paid}, Please change the amount paid to {loan_doc.total_amount_remaining}")

@frappe.whitelist()
def get_repayment_schedule(doc_name):
    repayment_schedule = frappe.db.sql(f"""
        SELECT rs.idx, rs.name, rs.paid_amount, rs.total_payment, rs.payment_date, rs.payment_date as new_payment_date
        FROM `tabLoan` l 
        LEFT JOIN `tabRepayment Schedule` rs ON rs.parent=l.name 
        WHERE rs.parent='{doc_name}' AND rs.total_payment>rs.paid_amount AND l.docstatus=1
        ORDER BY rs.payment_date""", as_dict=1)

    return repayment_schedule

@frappe.whitelist()
def set_new_date_in_repayment(rows, doc_name):
    loan_doc = frappe.db.exists("Loan", doc_name)
    if not loan_doc:
        frappe.throw(_("Loan {} not found".format((doc_name))))
        return
    try:
        loan_doc = frappe.get_doc("Loan", doc_name)
        rows = loads(rows)
        errors = []
        for tidx, row in enumerate(rows, 1):
            new_payment_date = row.get("new_date", "")
            repayment = frappe.get_doc("Repayment Schedule", row.get("row_name", ""))
            if date_diff(repayment.payment_date, new_payment_date) > 0:
                errors.append({
                    "date": repayment.payment_date,
                    "idx": tidx
                })
        
        if len(errors) > 0:
            errors_str = ''
            for err in errors:
                errors_str += "Choose Date after {} in row {}".format(err.get("date", ""), err.get("idx", ""))+"<br>"
            frappe.msgprint(_(errors_str))
            return "err"
        
        for tidx, row in enumerate(rows, 1):
            new_payment_date = row.get("new_date", "")
            repayment = frappe.get_doc("Repayment Schedule", row.get("row_name", ""))
            repayment.db_set("payment_date", new_payment_date, update_modified=False)
        reorder_payments_by_dates(loan_doc.name)
        
    except Exception as e:
        frappe.throw(_("Incorrect format"))

def reorder_payments_by_dates(row_parent):
    repayment_schedule = frappe.db.sql(f"""
           SELECT name 
           FROM `tabRepayment Schedule` 
           WHERE parent='{row_parent}' ORDER BY payment_date""", as_dict=1)
    for new_idx, row in enumerate(repayment_schedule, 1):
        doc = frappe.get_doc("Repayment Schedule" ,row.name)
        doc.db_set("idx", new_idx, update_modified=False)


@frappe.whitelist()
def get_users(doctype, txt, searchfield, start, page_len, filters):
    result = frappe.db.sql("""
        select name, full_name from `tabUser`
        where name LIKE %(txt)s and user_type <> 'SaaS Manager' and user_type <> 'System User' and name not in ('Guest', 'Administrator', 'support@mosyr.io') """ ,{"txt": "%" + txt + "%"})
    return result

def update_user_type_limits(doc,method):
    from frappe.installer import update_site_config
    types = frappe.get_list("User Type", filters={'is_standard': 0})
    user_type_limit = {}
    for utype in types:
        user_type_limit.setdefault(frappe.scrub(utype.name), 10000)
    update_site_config("user_type_doctype_limit", user_type_limit)

@frappe.whitelist(allow_guest=True)
def download_pdf(doctype, name, format=None, doc=None, no_letterhead=0):
    from frappe.www.printview import validate_print_permission
    from frappe.utils.pdf import get_pdf
    doc = doc or frappe.get_doc(doctype, name)
    try:
        validate_print_permission(doc)
    except frappe.exceptions.LinkExpired:
        frappe.local.response.http_status_code = 410
        frappe.local.response.message = _("Link Expired")
        return
    except frappe.exceptions.InvalidKeyError:
        frappe.local.response.http_status_code = 401
        frappe.local.response.message = _("Invalid Key")
        return
    html = frappe.get_print(doctype, name, format, doc=doc, no_letterhead=no_letterhead)
    if doctype == "Payroll Entry" and format == "Standard Printing for Payroll":
        from frappe.utils.print_format import report_to_pdf
        report_to_pdf(html, orientation="Landscape")
        frappe.local.response.filename = "{name}.pdf".format(
            name=name.replace(" ", "-").replace("/", "-")
        )
        return
    html = frappe.get_print(doctype, name, format, doc=doc, no_letterhead=no_letterhead)
    frappe.local.response.filename = "{name}.pdf".format(
        name=name.replace(" ", "-").replace("/", "-")
    )
    frappe.local.response.filecontent = get_pdf(html)
    frappe.local.response.type = "pdf"

@frappe.whitelist()
def get_salary_per_day(employee):
    base = 0
    months_days = 22

    lst = frappe.get_list(
        "Salary Structure Assignment",
        filters={"employee": employee, "docstatus": 1},
        fields=["from_date", "base", "company"],
        order_by="from_date desc",
    )
    if len(lst) > 0:
        base = flt(lst[0].base)
        company = lst[0].company
        mdays = frappe.get_list(
            "Company",
            filters={"name": company},
            fields=["month_days"]
        )
        if len(mdays) > 0:
            months_days = cint(mdays[0].month_days)
            if months_days not in [22, 28, 29, 30]:
                months_days = 22
        base = base / months_days
    return base

def create_componants_in_salary_straucture(doc, method):
    components = []
    for d in doc.deductions:
        components.append(d.salary_component)

    cc = frappe.db.exists("Company", {"name": doc.company})
    if cc:
        company = frappe.get_doc("Company", cc)
        risk_percentage_on_company  = company.risk_percentage_on_company
        risk_percentage_on_employee = company.risk_percentage_on_employee
        pension_percentage_on_company = company.pension_percentage_on_company
        pension_percentage_on_employee = company.pension_percentage_on_employee

        if "Risk On Company" not in components:
            row = doc.append("deductions", {})
            row.salary_component = "Risk On Company"
            row.amount_based_on_formula = 1
            row.do_not_include_in_total = 1
            row.formula = f"""(BS*{risk_percentage_on_company}/100) if(social_insurance_type=="Non Saudi") else 0"""

        if "Risk On Employee" not in components:
            row = doc.append("deductions", {})
            row.salary_component = "Risk On Employee"
            row.amount_based_on_formula = 1
            row.formula = f"""(BS*{risk_percentage_on_employee}/100) if(social_insurance_type=="Non Saudi") else 0"""
        if "Company Pension Insurance" not in components:
            row = doc.append("deductions", {})
            row.salary_component = "Company Pension Insurance"
            row.amount_based_on_formula = 1
            row.do_not_include_in_total = 1
            row.formula = f"""(BS*{pension_percentage_on_company}/100) if(social_insurance_type=="Saudi") else 0"""

        if "Employee Pension Insurance" not in components:
            row = doc.append("deductions", {})
            row.salary_component = "Employee Pension Insurance"
            row.amount_based_on_formula = 1
            row.formula = f"""(BS*{pension_percentage_on_employee}/100) if(social_insurance_type=="Saudi") else 0"""

def sum_net_pay_payroll_entry(doc, method):
    salary_slips = frappe.get_all("Salary Slip",{"payroll_entry": doc.name}, pluck="net_pay")
    if len(salary_slips) > 0:
        total_net_pay = sum(salary_slips)
        doc.db_set("total_netpay", total_net_pay)
        frappe.db.commit()

def update_employee_data(self, method):
        frappe.db.sql("""
              UPDATE `tabEmployee`
              SET pension_on_employee={}, pension_on_company={},
                  risk_on_employee=0, risk_on_company=0
              WHERE social_insurance_type='Saudi'""".format(flt(self.pension_percentage_on_employee), flt(self.pension_percentage_on_company)))
        
        frappe.db.sql("""
              UPDATE `tabEmployee`
              SET pension_on_employee=0, pension_on_company=0,
                  risk_on_employee={}, risk_on_company={}
              WHERE social_insurance_type='Non Saudi'""".format(flt(self.risk_percentage_on_employee), flt(self.risk_percentage_on_company)))
        
def create_letter_head(self, method):
        
        has_new_letter_head = False
        company_name = self.organization_english if self.organization_english else frappe.db.get_value("Company Id", self.company_id, "company")
        html_header_content = ''
        html_footer_content = ''
        if self.logo:
            has_new_letter_head = True
            html_header_content = '''<div class="container-fluid">
                                        <div class="row">
                                            <div class="col-sm-4 text-left">
                                                <h3>{}</h3>
                                            </div>
                                            <div class="col-sm-4 text-center">
                                                <img src="{}" style="max-width: 100px; max-height: 100px;">
                                                <h3>{}</h3>
                                            </div>
                                            <div class="col-sm-4 text-right" >
                                                <h3>{}</h3>
                                            </div>
                                        </div>
                                    </div>'''.format(self.left_header,self.logo, company_name,self.right_header)
        
        if len(self.signatures) > 0:
            has_new_letter_head = True
            for signature in self.signatures:
                job_title = signature.job_title or ""
                employee_name = frappe.db.get_value("Employee", signature.name1, "employee_name")
                html_footer_content += '''<div class="col-sm-4 text-right">
                                                <p class="text-center" style="font-weight: bold">{}</p>
                                                <p class="text-center" style="font-weight: bold">{}</p>
                                              </div>'''.format(job_title, employee_name)
            
            
            html_footer_content = '<div class="container-fluid"><div class="row">' + html_footer_content + '</div></div>'
        if has_new_letter_head:
            lh = frappe.db.exists("Letter Head", self.name)
            
            if lh:
                lh = frappe.get_doc("Letter Head", self.name)
            else: 
                lh = frappe.new_doc("Letter Head")
                lh.letter_head_name = self.name
            lh.source = "HTML"
            lh.footer_source = "HTML"
            lh.is_default = 0
            # lh.image = image
            lh.content = html_header_content
            lh.footer = html_footer_content
            lh.save()
            frappe.db.commit()
            lh.db_set('source', "HTML")
            lh.db_set('footer', html_footer_content)

def create_user_permission_on_company_in_validate(doc, method):
    if not doc.is_new():
        companies_before_save = frappe.db.get_list("Company Table", {"parent":doc.name}, pluck="company")
        companies_after_save = [d.company for d in doc.companies]
        diff_lists = list(set(companies_before_save) ^ set(companies_after_save))
        if len(diff_lists):
            user_permissions = frappe.get_list("User Permission", {"user": doc.name, "allow": "Company"})
            if len(user_permissions):
                for user_permission in user_permissions:
                    frappe.delete_doc("User Permission", user_permission.name)
                frappe.db.commit()
            if len(doc.companies):
                for row in doc.companies:
                    perm = frappe.new_doc("User Permission")
                    perm.user = doc.name
                    perm.allow = "Company"
                    perm.for_value = row.company
                    perm.save()
                frappe.db.commit()

def create_user_permission_on_company_in_create_user(doc, method):
        if len(doc.companies):
            for row in doc.companies:
                perm = frappe.new_doc("User Permission")
                perm.user = doc.name
                perm.allow = "Company"
                perm.for_value = row.company
                perm.save()
            frappe.db.commit()
            

@frappe.whitelist()
def get_emps_based_on_option(option, value):
    emps_list = frappe.db.get_list("Employee",fields=['name', 'first_name'], filters={"status":"Active", option:value})
    return {"emps_list":emps_list}


def custom_get_letter_heads():
    letter_heads = {}
    user = frappe.get_doc("User", frappe.session.user)
    if user.name == "Administrator" or user.user_type == "SaaS Manager":
        for letter_head in frappe.get_all("Letter Head", fields=["name", "content", "footer"]):
            letter_heads.setdefault(
                letter_head.name, {"header": letter_head.content, "footer": letter_head.footer}
            )
    else:
        if user.companies:
            lh = []
            for c in user.companies:
                lh.append(c.company)

            for letter_head in frappe.get_all("Letter Head", fields=["name", "content", "footer"], filters={'name': ["IN", lh]}):
                letter_heads.setdefault(
                    letter_head.name, {"header": letter_head.content, "footer": letter_head.footer}
                )
    return letter_heads

def employee_end_contract(doc, method):
    # change employee status based on contract end date to inactive status
    if doc.status != "Active":
        return
    prev_contract_date = frappe.get_value("Employee", doc.name, "contract_end_date")
    if not prev_contract_date:
        return

    if getdate(prev_contract_date) != getdate(doc.contract_end_date):
        if get_datetime(doc.contract_end_date) < get_datetime():
            doc.status = "Inactive"

@frappe.whitelist()
def handle_formula(docname, amount, operation, abbr):
    """set formula from custom formula form to formula text field"""
    amount = flt(amount)
    if amount == 0:
        return False

    sal_component = frappe.get_doc("Salary Component", docname)
    sal_component.formula = f"{abbr} {operation} {amount}"
    sal_component.save()
    return True


def create_department_workflows(doc, method):
    workflow_docs = [
        {
            "name": "Leave Application",
            "state_name": "Leave",
            "table_name": "leave_approvers",   
        },{
            "name": "Shift Request",
            "state_name": "Shift Request",
            "table_name": "shift_request_approver"
        },{
            "name": "Contact Details",
            "state_name": "Contact Details",
            "table_name": "contact_details_approver"

        },{
            "name": "Educational Qualification",
            "state_name": "Qualification",
            "table_name": "educational_qualification_approver"

        },{
            "name": "Emergency Contac",
            "state_name": "Emergency",
            "table_name": "emergency_contact_approver"

        },{
            "name": "Health Insurance",
            "state_name": "Insurance",
            "table_name": "health_insurance_approver"

        },{
            "name": "Personal Details",
            "state_name": "Personal Details",
            "table_name": "personal_details_approver"

        },{
            "name": "Salary Details",
            "state_name": "Salary Details",
            "table_name": "salary_details_approver"

        },{
            "name": "Exit Permission",
            "state_name": "Exit Permission",
            "table_name": "exit_permission_approver"

        },{
            "name": "Attendance Request",
            "state_name": "Attendance Request",
            "table_name": "attendance_request_approver"

        },{
            "name": "Compensatory Leave Request",
            "state_name": "Compensatory Leave Request",
            "table_name": "compensatory_leave_request_approver"

        },{
            "name": "Travel Request",
            "state_name": "Travel Request",
            "table_name": "travel_request_approver"

        }
    ]
    for row in workflow_docs:
        create_workflow(doc, row)
    
def create_workflow(doc, row):
    approver_table = row.get("table_name")
    approver_list = doc.get(approver_table)
    if approver_list:
        state_list = create_doc_workflow_status(doc.name, approver_list, row.get("state_name"))
        actions_list = create_doc_workflow_actions(doc.name, state_list)
        
        is_workflow_exist = frappe.db.exists("Workflow", {"document_type":row.get("name"), "is_active": 1})
        if not is_workflow_exist:
            # Update States List With Standerd States
            state_list = add_standerd_states(state_list)
            
            # Create New Workflow For Doc 
            new_workflow = frappe.get_doc({
                "doctype": "Workflow",
                "workflow_name": row.get("name"),
                "document_type": row.get("name"),
                "is_active": 1,
                "is_standard": 0,
                "send_email_alert": 0,
                "states": state_list,
                "transitions": actions_list
            })
            new_workflow.insert()
        else:
            # Update Workflow Status & Actions
            workflow_doc = frappe.get_doc("Workflow", {"document_type":row.get("name"), "is_active": 1})
            clear_states_actions_related_to_department(doc.name, workflow_doc.name)
            workflow_doc = frappe.get_doc("Workflow",workflow_doc.name)
            
            # Check Stnaderd Statue ["Pending", "Cancelled"]
            exist_states = []
            for d in workflow_doc.states:
                exist_states.append(d.state)
            
            is_pending_exist = 1 if "Pending" in exist_states else 0
            is_cancelled_exist = 1 if "Cancelled" in exist_states else 0
            
            # Add Not Exists Standerd Status
            if not is_pending_exist:
                state_list.insert(0, {
                    "state": "Pending",
                    "doc_status": "0",
                    "update_field": "workflow_state",
                    "update_value": "Pending",
                    "allow_edit": "All"
                })
            
            if not is_cancelled_exist:
                state_list.append({
                    "state": "Cancelled",
                    "doc_status": "2",
                    "update_field": "workflow_state",
                    "update_value": "Cancelled",
                    "allow_edit": "All"
                })
            
            if state_list:
                for state in state_list:
                    workflow_doc.append("states", state)
            
            if actions_list:
                for action in actions_list:
                    workflow_doc.append("transitions", action)
            
            workflow_doc.save()


def create_doc_workflow_status(department, approvers, state_name):
    state_list = []
    if approvers:
        prev_state = "Pending"
        for idx, row in enumerate(approvers):
            approve_state_name = "Approved " + state_name + " By "+ row.approver
            is_exists = frappe.db.exists("Workflow State", approve_state_name)
            if not is_exists:
                # Create Status for every Approver
                doc = frappe.new_doc("Workflow State")
                doc.workflow_state_name = approve_state_name
                doc.style = "Success"
                doc.save()

            state_list.append({
                "state":approve_state_name,
                "doc_status": "1" if idx == len(approvers)-1 else "0",
                "update_field": "workflow_state",
                "update_value": approve_state_name,
                "allow_edit": "All",
                "state_type": "Approve",
                "prev_state": prev_state,
                "related_to": department,
                "approver": row.approver
            })

            reject_state_name = "Rejected " + state_name + " By "+ row.approver
            is_exists = frappe.db.exists("Workflow State", reject_state_name)
            if not is_exists:
                # Create Status for every Approver
                doc = frappe.new_doc("Workflow State")
                doc.workflow_state_name = reject_state_name
                doc.style = "Warning"
                doc.save()

            state_list.append({
                "state":reject_state_name,
                "doc_status": "1",
                "update_field": "workflow_state",
                "update_value": reject_state_name,
                "allow_edit": "All",
                "state_type": "Reject",
                "prev_state": prev_state,
                "related_to": department,
                "approver": row.approver
            })
            
            prev_state = approve_state_name

    return state_list

def create_doc_workflow_actions(department, state_list):
    print(state_list)
    actions_list = []
    if state_list:
        for row in state_list:
            actions_list.append({
                "state": row.get("prev_state"),
                "action": row.get("state_type"),
                "next_state": row.get("state"),
                "allowed": row.get("allow_edit"),
                "condition": f'doc.department == "{department}"',
                "related_to": department
            })
    # Create Cancelled action
    if state_list:
        for x in state_list:
            if x.get("state_type") == "Reject":
                actions_list.append({
                    "state": x.get("state"),
                    "action": "Cancel",
                    "next_state": "Cancelled",
                    "allowed": x.get("allow_edit"),
                    "condition": f'doc.department == "{department}"',
                    "related_to": department
                })
    return actions_list

def clear_states_actions_related_to_department(department, doc_name):
    doc = frappe.get_doc("Workflow",doc_name)

    for row in doc.states:
        if row.related_to == department:
            frappe.delete_doc("Workflow Document State", row.name)
            
    for row in doc.transitions:
        if row.related_to == department:
            frappe.delete_doc("Workflow Transition", row.name)

    doc.save()
    frappe.db.commit()
    
def add_standerd_states(state_list):
    states = ["Pending", "Cancelled"]
    for row in states:
        is_exists = frappe.db.exists("Workflow State", row)
        if not is_exists:
            # Create Status for every Approver
            doc = frappe.new_doc("Workflow State")
            doc.workflow_state_name = row
            doc.save()
        
    state_list.insert(0, {
        "state": "Pending",
        "doc_status": "0",
        "update_field": "workflow_state",
        "update_value": "Pending",
        "allow_edit": "All"
    })
    state_list.append({
        "state": "Cancelled",
        "doc_status": "2",
        "update_field": "workflow_state",
        "update_value": "Cancelled",
        "allow_edit": "All"
    })
    
    return state_list


def validate_approver(doc, method):
    is_workflow_exist = frappe.db.exists("Workflow", {"document_type":doc.doctype, "is_active": 1})
    if is_workflow_exist:
        workflow_doc = frappe.get_doc("Workflow", {"document_type":doc.doctype, "is_active": 1})
        for row in workflow_doc.states:
            if row.state == doc.workflow_state:
                if row.approver != frappe.session.user and doc.workflow_state != "Pending" :
                    approver_name = frappe.get_value("User", row.approver, "full_name")
                    frappe.throw(_(f"Can't Approved this Application, Just <b>{approver_name}</b> Can Approved this Application"))
    else:
        return
    

def send_notification_and_email(doc, method=None):
    if doc.get("workflow_state"):
        if doc.workflow_state != "Pending":
            doc_before_save = doc.get_doc_before_save()
            old_status = doc_before_save.workflow_state

            args = {
                "new_status": doc.workflow_state,
                "old_status": old_status,
                "for_user": frappe.get_value("Employee", doc.employee, "user_id"),
                "service_name":"Leave Application",
                "service_url": "leave-application",
                "name": doc.name,
                "by": frappe.session.user,
                "new_st_color": "yellow",
                "old_st_color": "yellow"
            }
            if "Approved" in doc.workflow_state:
                args.update({"new_st_color":"green"})
            elif "Rejected" in doc.workflow_state:
                args.update({"new_st_color":"red"})


            if "Approved" in old_status:
                args.update({"old_st_color":"green"})
            elif "Rejected" in old_status:
                args.update({"old_st_color":"red"})

            send_notification(args)
            send_email(args)


def send_notification(args):
    doc_url = get_url() + "/app/" + args.get("service_url") + "/"
    new_doc = frappe.new_doc("Notification Log")
    new_doc.subject = f"""{args.get("service_name")} Updated"""
    new_doc.for_user = args.get("for_user")
    new_doc.type = "Alert"
    new_doc.email_content = f"""Your {args.get("service_name")}: <a href="{doc_url}{args.get("name")}" style="cursor: pointer;"><b> {args.get("name")} </b></a>Status Changed </br> From <span class="text-{args.get("old_st_color")}"> {args.get("old_status")} </span> to <span class="text-{args.get("new_st_color")}"> {args.get("new_status")} </span> by <b>{args.get("by")}</b>"""
    new_doc.insert(ignore_permissions=True)


def send_email(args):
    doc_url = get_url() + "/app/" + args.get("service_url") + "/"
    msg = f"""Your {args.get("service_name")}: <a href="{doc_url}{args.get("name")}" style="cursor: pointer;"><b> {args.get("name")} </b></a>Status Changed </br> From <span class="text-{args.get("old_st_color")}"> {args.get("old_status")} </span> to <span class="text-{args.get("new_st_color")}"> {args.get("new_status")} </span> by <b>{args.get("by")}</b>"""
    
    frappe.sendmail(
        recipients=['mismail@anvilerp.com'],
        sender=args.get("by"),
        subject=f"""{args.get("service_name")} Updated""",
        message=msg,
        retry=3,
    )