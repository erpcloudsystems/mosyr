# Copyright (c) 2022, AnvilERP and contributors
# For license information, please see license.txt

import frappe
import requests
from frappe.model.document import Document
from datetime import datetime
from frappe import _
import os
import json
from frappe.utils import cint, getdate, flt, get_date_str

doctypes_with_abbr = ['Department']
doctypes_with_company_field = ['Department']

class MosyrDataImport(Document):

    def download_mosyr_file(self, doctype, docname, filed_name, source_path, filename):
        frappe.db.commit()
        source_path = f"{source_path}{filename}"
        try:
            r = requests.get(source_path, allow_redirects=True)
            r.raise_for_status()
            content = r.content
            _file = frappe.new_doc("File")
            _file.update({
                "file_name": filename,
                "attached_to_doctype": doctype,
                "attached_to_name": docname,
                "attached_to_field": filed_name,
                "folder": 'Home/Attachments',
                "is_private": 1,
                "content": content
            })
            _file.save(ignore_permissions=True)
            
            doc = frappe.get_doc(doctype, docname)
            if filed_name and doctype:
                doc.set(filed_name, _file.file_url)
                doc.flags.ignore_mandatory = True
                doc.save()
                frappe.db.commit()
            return True, _file.as_dict()
        except Exception as e:
            return False, {}

    def get_clean_data(self, data):
        clear_data = {}
        for k, v in data.items():
            if isinstance(v, list):
                if len(v) == 1:
                    if v[0] == '':
                        clear_data[f'{k}'] = ''
                    else:
                        clear_data[f'{k}'] = v
                elif len(v) == 0:
                    clear_data[f'{k}'] = ''

                else:
                    clear_data[f'{k}'] = v
            else:
                clear_data[f'{k}'] = v
        return clear_data

    def check_link_data(self, doctype, value, filed):
        new_value = f"{value}".strip()
        if doctype in doctypes_with_abbr:
            company = frappe.defaults.get_global_default('company')
            company = frappe.get_doc('Company', company)
            abbr = company.abbr
            new_value = f'{value} - {abbr}'

        exist = frappe.db.exists(doctype, new_value)
        is_new = False
        if not exist:
            args = {
                f'{filed}': value
            }
            # if dictype has company field
            if doctype in doctypes_with_company_field:
                args.update({
                    'company': company.name
                })
            new_doc = frappe.new_doc(doctype)
            new_doc.update(args)
            new_doc.save()
            frappe.db.commit()
            exist = new_value
            is_new = True
        return is_new, exist

    @frappe.whitelist()
    def psc(self):
        banks = [
            "Al Rajhi Bank",
            "Al Inma Bank",
            "Bank Al Bilad",
            "Bank Al Jazira",
            "The National Commercial Bank",
            "Arab National Bank",
            "Bank Saudi Fransi",
            "Saudi Investment Bank",
            "Saudi Hollandi Bank",
            "The Saudi British Bank",
            "Samba Financial Group",
        ]
        for bank in banks:
            self.check_link_data('Bank', bank, 'bank_name')
            
        frappe.db.commit()

    @frappe.whitelist()
    def get_company_id(self):
        return frappe.conf.company_id or False

    def call_api(self, path, company_id, doctype):
        data = []
        errors_count = 0

        if not company_id:
            company_id = self.get_company_id()

        if not company_id:
            msg = _(f"Set Company id please")
            frappe.throw(f"{msg}!")

        url = path.format(company_id)
        res = False
        try:
            res = requests.get(url)
            res.raise_for_status()

            if res.ok and res.status_code == 200:
                data = res.json()
        except Exception as e:
            status_code = ''
            if res:
                status_code = res.status_code
                status_code = f"error code {status_code}"
            err = frappe.log_error(
                f"{e}", f'Import {doctype}s Faield. {status_code}!')
            err_msg = _(f'An Error occurred while Import {doctype}s see')
            err_name_html = f' <a href="/app/error-log/{err.name}"><b>{err.name}</b></a>'
            frappe.throw(err_msg + err_name_html)
            data = []
        return data

    def show_import_status(self, doctype, total_data, success, existed, errors, headers, error_msgs, log_name):
        error_table_html = ''
        if len(error_msgs) > 0:
            headers_html = ''
            errors_html = ''

            for head in headers:
                headers_html += f'<th>{head}</th>'
            headers_html = f'<tr>{headers_html}</tr>'
            
            for errs in error_msgs:
                err_html = ''
                for err in errs:
                    err_html += f'<td>{err}</td>'
                errors_html += f'<tr>{err_html}</tr>'
            
            error_table_html = f'''<table id="table" class="table table-bordered">
							<thead>{headers_html}</thead>
							<tbody>{errors_html}</tbody>
							</table>
							'''
        msg = f"""<table class="table table-bordered">
		<tbody>
			<tr>
			    <th scope="row"><span class="indicator green"></span>{_("Success")}</th>
			    <td>{success}</td>
			</tr>
            <tr>
			    <th scope="row"><span class="indicator green"></span>{_("Existed")}</th>
			    <td>{existed}</td>
			</tr>
			<tr>
                <th scope="row"><span class="indicator red"></span>{_("Errors")}</th>
                <td>{errors}</td>
			</tr>
		</tbody>
		</table>
		{error_table_html}
		"""
        frappe.msgprint(msg, title=f'{total_data} {doctype} Imported',
                        indicator='Cs', primary_action={ 'label': _('Export Error Log 2'),
                            'client_action': 'mosyr.download_errors',
                            'args': {
                                'data': log_name
                            } })
    
    def create_import_log(self, doctype, total_data, success, existed, errors, headers, error_msgs):
        err_log = frappe.new_doc('Mosyr Data Import Log')
        err_log.title = f"Import {doctype}"
        err_log.successed = success
        err_log.existed = existed
        err_log.failed = errors
        err_log.import_date = frappe.utils.now_datetime()
        err_log.error_json = json.dumps({
            'headers': headers,
            'error_msgs': error_msgs
        })
        err_log.save()
        frappe.db.commit()
        return err_log.name
    
    @frappe.whitelist()
    def import_branches(self, company_id):
        path = 'https://www.mosyr.io/ar/api/branches_api.json?list=branches_{}'
        data = self.call_api(path, company_id, 'Branche')

        headers = [_('Branch Id'), _('Error')]
        error_msgs = []
        total_data = len(data)
        errors = 0
        success = 0
        existed = 0

        for d in data:
            d = self.get_clean_data(d)
            bn = d.get('branch_name', '')
            bid = d.get('branch_id', '')
            if bn != '':
                is_new, exist = self.check_link_data('Branch', bn, 'branch')
                if is_new:
                    success += 1
                else:
                    existed += 1
            else:
                errors += 1
                error_msgs.append([bid, _('Missing Branch Name')])
        log_name = self.create_import_log('Branch', total_data, success, existed, errors, headers, error_msgs)
        self.show_import_status('Branch', total_data, success, existed, errors, headers, error_msgs, log_name)
    
    @frappe.whitelist()
    def import_grades(self, company_id):
        path = 'https://www.mosyr.io/en/api/migration-classes.json?company_id={}'
        data = self.call_api(path, company_id, 'Employee Grade')
        headers = [_('Employee Class Id'), _('Error')]
        error_msgs = []
        total_data = len(data)
        errors = 0
        success = 0
        existed = 0

        for d in data:
            d = self.get_clean_data(d)
            dn = d.get('name', '')
            did = d.get('key', '')
            if dn != '':
                is_new, exist = self.check_link_data('Employee Grade', dn, '__newname')
                if is_new:
                    success += 1
                else:
                    existed += 1
            else:
                errors += 1
                error_msgs.append([did, _('Missing Class Value')])
        log_name = self.create_import_log('Employee Grade', total_data, success, existed, errors, headers, error_msgs)
        self.show_import_status('Employee Grade', total_data, success, existed, errors, headers, error_msgs, log_name)

    @frappe.whitelist()
    def import_departments(self, company_id):
        path = 'https://www.mosyr.io/en/api/migration-departments.json?company_id={}'
                
        data = self.call_api(path, company_id, 'Department')
        headers = [_('Employee Class Id'), _('Error')]
        error_msgs = []
        total_data = len(data)
        errors = 0
        success = 0
        existed = 0

        for d in data:
            d = self.get_clean_data(d)
            dn = d.get('name', '')
            did = d.get('key', '')
            if dn != '':
                is_new, exist = self.check_link_data('Department', dn, 'department_name')
                if is_new:
                    success += 1
                else:
                    existed += 1
            else:
                errors += 1
                error_msgs.append([did, _('Missing Class Value')])
        log_name = self.create_import_log('Department', total_data, success, existed, errors, headers, error_msgs)
        self.show_import_status('Department', total_data, success, existed, errors, headers, error_msgs, log_name)

    @frappe.whitelist()
    def import_employees(self, company_id):
        path = 'https://www.mosyr.io/en/api/migration-employees.json?company_id={}'
        data = self.call_api(path, company_id, 'Employee')
        company_id_for_insurances = frappe.db.exists("Company Id", company_id)
        company_insurances = {
            "risk_on_employee": 0,
            "risk_on_company": 0,
            "pension_on_employee": 0,
            "pension_on_company": 0,
            "company": None
        }
        if company_id_for_insurances:
            company_id_for_insurances = frappe.get_doc("Company Id", company_id)
            comapny_data = frappe.get_list("Company", filters={'name': company_id_for_insurances.company}, fields=['*'])
            if len(comapny_data) > 0:
                comapny_data = comapny_data[0]
                company_insurances.update({
                    "risk_on_employee": comapny_data.risk_percentage_on_employee,
                    "risk_on_company": comapny_data.risk_percentage_on_company,
                    "pension_on_employee": comapny_data.pension_percentage_on_employee,
                    "pension_on_company": comapny_data.pension_percentage_on_company,
                    'company': comapny_data.company
                })

        headers = [_('Employee Id'), _('Employee Name'), _('Error')]
        error_msgs = []
        total_data = len(data)
        errors = 0
        success = 0
        existed = 0
        attachment_field_as_dict = ['employee_photo']
        attachment_field_as_list = []
        ignored_fields = ['branches']
        mapped_fields = {
            'fullname_ar': 'first_name',
            'employee_status': 'api_employee_status',
            'branch_name': 'branch',
            'job_title': 'designation',
            'birth_date_g': 'date_of_birth',
            'employee_class': 'department',
            'iban': 'bank_ac_no',
            'payroll_card_no': 'payroll_card_number',
            'mobile':'cell_number',
            'employee_email':'personal_email',
            'employee_address': 'permanent_address',
            'insurance_card_number':'health_insurance_no',
            'insurance_card_company': 'health_insurance_provider',
            'employee_no': 'employee_number',
            'fullname_en': 'full_name_en',
            'bank': 'bank_name',
            'Bank': 'bank_name',
            'birth_date_h': 'hijri_date_of_birth'
        }
        date_fields = ['date_of_birth', 'birth_date_g', 'insurance_card_expire']
        link_fields = []
        args = {
            'status': 'Inactive',
            'from_api': 1,
            'valid_data': 0,
        }
        for d in data:
            d = self.get_clean_data(d)
            key = d.get('key', '')
            fullname_ar = d.get('fullname_ar', False)
            if not fullname_ar:
                errors += 1
                error_msgs.append([key, fullname_ar, _('Missing Arabic Full Name')])
                continue
            
            gender = d.get('gender', False)
            if not gender:
                errors += 1
                error_msgs.append([key, fullname_ar, _('Missing Employee Gender')])
                continue
            
            birth_date_g = d.get('birth_date_g', False)
            if not birth_date_g or birth_date_g=="":
                birth_date_g = get_date_str(getdate("01-01-2000"))
                # d.update({ "birth_date_g": birth_date_g })
                # errors += 1
                # error_msgs.append([key, fullname_ar, _('Missing Date Of Birth')])
                # continue

            new_employee = frappe.new_doc("Employee")
            employees_with_same_key = frappe.get_list('Employee', filters={'key': key})
            if len(employees_with_same_key) > 0:
                existed += 1
                new_employee = frappe.get_doc('Employee', employees_with_same_key[0])
            
            fiels_to_attach = []
            for k, v in d.items():
                k = f'{k}'.lower()
                k = mapped_fields.get(k, k)
                
                if k in ignored_fields: continue
                if k in attachment_field_as_dict:
                    if v != "":
                        filename = v.get('filename', False)
                        if filename:
                            fiels_to_attach.append({
                                "path": "https://www.mosyr.io/sites/default/files/",
                                "name": filename
                            })
                if k in date_fields and v != '':
                    v = get_date_str(getdate(v))
                if k == 'date_of_birth':
                    v = birth_date_g
                if k == 'designation' and v != '':
                    is_new, v = self.check_link_data('Designation', v, 'designation_name')
                if k == 'department' and v != '':
                    is_new, v = self.check_link_data('Department', v, 'department_name')
                if k == 'religion' and v != '':
                    is_new, v = self.check_link_data('Religion', v, 'religion')
                if k == 'nationality' and v != '':
                    is_new, v = self.check_link_data('Nationality', v, 'nationality')
                if k == 'health_insurance_provider' and v != '':
                    is_new, v = self.check_link_data('Employee Health Insurance', v, 'health_insurance_name')
                if k == 'branch' and v != '':
                    is_new, v = self.check_link_data('Branch', v, 'branch')
                if k == 'gender' and v != '':
                    is_new, v = self.check_link_data('Gender', v, 'gender')
                    k = "e_gender"
                if k == 'self_service':
                    v = cint(v)
                if k == 'hijri_date_of_birth' and v != '':
                    temp_v = f'{v}'.split('-')
                    if len(temp_v) == 3:
                        if cint(temp_v[0]) > cint(temp_v[-1]):
                            temp_v.reverse()
                            v = '-'.join(temp_v)
                args.update({f'{k}': v})
                if k == 'bank':
                    args.update({
                        'salary_mode': 'Bank'
                    })
                
            new_employee.update(args)
            company = company_insurances.get("company", False)
            if company:
                new_employee.update({
                    "company": company
                })
            new_employee.flags.ignore_mandatory = True
            new_employee.save()
            frappe.db.commit()
            for fta in fiels_to_attach:
                self.download_mosyr_file('Employee', new_employee.name, 'image', fta['path'], fta['name'])
            success += 1

        log_name = self.create_import_log('Employee', total_data, success, existed, errors, headers, error_msgs)
        self.show_import_status('Employee', total_data, success, existed, errors, headers, error_msgs, log_name)
       
    @frappe.whitelist()
    def import_identity(self, company_id):
        path = 'https://www.mosyr.io/en/api/migration-ids.json?company_id={}'
        data = self.call_api(path, company_id, 'Employee Identity')
        headers = [_('Employee Id'), _('Identity Key'), _('Error')]
        error_msgs = []
        total_data = len(data)
        errors = 0
        success = 0
        existed = 0

        attachment_field = ['id_photo']
        ignored_fields = []
        date_fields = ['border_entry_date', 'expire_date', 'issue_date']
        mapped_fields = {
            'name': 'identity_name',
        }
        link_fields = []
        lookup_value = {
            'nationalid': 'National ID',
            'displacedtribalscard': 'Displaced tribals card',
            'gccstatesidentity': 'GCC States Identity',
            'bordersentrynumber': 'Borders Entry Number',
            'number': 'Number',
            'drivinglicense': 'Driving License',
            'iqama': 'Iqama'
        }

        for d in data:
            d = self.get_clean_data(d)
            key = d.get('key', '')
            nid = d.get('nid', False)
            if not nid:
                errors += 1
                error_msgs.append(['Unknown', key, _('Missing Employee nid')])
                continue
            
            id_type = d.get('id_type', False)
            if not id_type:
                errors += 1
                error_msgs.append([nid, key, _('Missing Id Type')])
                continue
            
            employees_with_nid = frappe.get_list('Employee', filters={'key': nid})
            if len(employees_with_nid) == 0:
                errors += 1
                error_msgs.append([nid, '', _('Employee not found')])
                continue
            
            employee = frappe.get_doc('Employee', employees_with_nid[0].name)
            args = {}
            attachments_data = []
            for k, v in d.items():
                k = f'{k}'.lower()
                k = mapped_fields.get(k, k)
                if k in ignored_fields: continue
                if k in attachment_field and isinstance(v, list):
                    if len(v) > 0:
                        attachments_data.append(v[0])
                    continue

                if k == 'border_entry_port' and v != '':
                    is_new, v = self.check_link_data('Border', v, 'border')

                if k == 'id_type':
                    v = lookup_value.get(v, 'Iqama')
                
                if k in date_fields and v != '':
                    v = getdate(v)
                
                if k in ['issue_date_h', 'expire_date_h', 'border_entry_date_h'] and v != '':
                    temp_v = f'{v}'.split('-')
                    if len(temp_v) == 3:
                        if cint(temp_v[0]) > cint(temp_v[-1]):
                            temp_v.reverse()
                            v = '-'.join(temp_v)
                args.update({f'{k}': v})
            
            is_new = True
            new_idx = -1
            for idx, eid in enumerate(employee.identity):
                if eid.key == key:
                    identity = employee.identity[idx]
                    identity.update(args)
                    is_new = False
                    new_idx = idx
            
            if is_new:
                new_idx = len(employee.identity)
                employee.append('identity', args)
            
            employee.flags.ignore_mandatory = True
            employee.save()
            frappe.db.commit()
            
            for att in attachments_data:
                att = att.get("filename", False)
                if att:
                    source_path = "https://www.mosyr.io/sites/default/files/"
                    is_downloaded, _file = self.download_mosyr_file("Employee", employee.name, 'id_photo', source_path, att)
                    if is_downloaded and new_idx != -1:
                        employee = frappe.get_doc('Employee', employee.name)
                        id_row = employee.identity[new_idx]
                        id_row.id_photo = _file['file_url']
                        employee.flags.ignore_mandatory = True
                        employee.save()
                        frappe.db.commit()
            success += 1
        frappe.db.commit()

        log_name = self.create_import_log('Employee Identity', total_data, success, existed, errors, headers, error_msgs)
        self.show_import_status('Employee Identity', total_data, success, existed, errors, headers, error_msgs, log_name)
    
    @frappe.whitelist()
    def import_dependents(self, company_id):
        path = 'https://www.mosyr.io/en/api/migration-employee-dependents.json?company_id={}'
        data = self.call_api(path, company_id, 'Employee Dependent')
        headers = [_('Employee Id'), _('Dependent Key'), _('Error')]
        error_msgs = []
        total_data = len(data)
        errors = 0
        success = 0
        existed = 0

        attachment_field = ['attachement']
        ignored_fields = ['name']
        date_fields = ['birth_date_g', 'insurance_card_expire']
        mapped_fields = {
            'fullname_ar': 'full_name_ar',
            'fullname_en': 'full_name_en',
        }
        link_fields = []

        for d in data:
            d = self.get_clean_data(d)
            key = d.get('key', '')
            nid = d.get('nid', False)
            if not nid:
                errors += 1
                error_msgs.append(['Unknown', key, _('Missing Employee nid')])
                continue

            employees_with_nid = frappe.get_list('Employee', filters={'key': nid})
            if len(employees_with_nid) == 0:
                errors += 1
                error_msgs.append([nid, '', _('Employee not found')])
                continue
            
            employee = frappe.get_doc('Employee', employees_with_nid[0].name)
            args = {}

            for k, v in d.items():
                k = f'{k}'.lower()
                k = mapped_fields.get(k, k)
                if k in attachment_field: continue
                if k in ignored_fields: continue

                if k == 'insurance_card_company' and v != '':
                    is_new, v = self.check_link_data('Employee Health Insurance', v, 'health_insurance_name')
                if k == "relationship" and v == "0":
                    v = ""
                if k in date_fields and v != '':
                    v = getdate(v)
                if k == 'birth_date_h' and v != '':
                    temp_v = f'{v}'.split('-')
                    if len(temp_v) == 3:
                        if cint(temp_v[0]) > cint(temp_v[-1]):
                            temp_v.reverse()
                            v = '-'.join(temp_v)
                args.update({f'{k}': v})
            
            if len(employee.dependent) > 0:
                for idx, eid in enumerate(employee.dependent):
                    if eid.key == key:
                        dependent = employee.dependent[idx]
                        dependent.update(args)
            else:
                employee.append('dependent', args)
            employee.flags.ignore_mandatory = True
            employee.save()
            success += 1
            
        log_name = self.create_import_log('Employee Dependent', total_data, success, existed, errors, headers, error_msgs)
        self.show_import_status('Employee Dependent', total_data, success, existed, errors, headers, error_msgs, log_name)

    @frappe.whitelist()
    def import_employee_status(self, company_id):
        path = 'https://www.mosyr.io/en/api/migration-employee-status.json?company_id={}'
        data = self.call_api(path, company_id, 'Employee Status')
        headers = [_('Employee Id'), _('Status Key'), _('Error')]
        error_msgs = []
        total_data = len(data)
        errors = 0
        success = 0
        existed = 0

        attachment_field = ['attachement']
        ignored_fields = ['name']
        date_fields = ['status_date']
        mapped_fields = {
            'attachement': 'attachment'
        }
        link_fields = []
        
        status_lookup_value = {
            "active": "Active",
            "leave": "On Leave",
            "escaped": "Escaped",
            "finalexit": "Final Exit",
            "sponsorshiptrans": "Need Sponsorship Transmission",
            "dead": "Dead",
            "termination": "Termination",
            "exitandreturnnoshow": "Exit and return with no show",
            "sponsoredonly": "Sponsored only (Kafala)",
            "onsponsorshiptrans": "On Sponsorship Transmission",
            "stopworking": "Stop Working",
            "inactive": "Not active",
            "assignment": "Assignment",
            "onajob": "On a job",
            "intraining": "In Training",
            "resigned": "Resigned",
            "contractexpired": "Contract Expired",
        }
        for d in data:
            d = self.get_clean_data(d)
            key = d.get('key', '')
            nid = d.get('nid', False)
            status = d.get('status', False)
            if not nid:
                errors += 1
                error_msgs.append(['Unknown', key, _('Missing Employee nid')])
                continue
            if not status:
                errors += 1
                error_msgs.append([nid, key, _('Missing Status')])
                continue

            employees_with_nid = frappe.get_list('Employee', filters={'key': nid})
            if len(employees_with_nid) == 0:
                errors += 1
                error_msgs.append([nid, '', _('Employee not found')])
                continue
            
            employee = frappe.get_doc('Employee', employees_with_nid[0].name)
            args = {}

            for k, v in d.items():
                k = f'{k}'.lower()
                k = mapped_fields.get(k, k)
                if k in attachment_field: continue
                if k in ignored_fields: continue

                if k == "status" and v != '':
                    v = status_lookup_value.get('status', 'Not active')
                if k in date_fields and v != '':
                    v = getdate(v)
                if k == 'status_date_h' and v != '':
                    temp_v = f'{v}'.split('-')
                    if len(temp_v) == 3:
                        if cint(temp_v[0]) > cint(temp_v[-1]):
                            temp_v.reverse()
                            v = '-'.join(temp_v)
                args.update({f'{k}': v})
            
            if len(employee.mosyr_employee_status) > 0:
                for idx, eid in enumerate(employee.mosyr_employee_status):
                    if eid.key == key:
                        mosyr_employee_status = employee.mosyr_employee_status[idx]
                        mosyr_employee_status.update(args)
            else:
                employee.append('mosyr_employee_status', args)
            employee.flags.ignore_mandatory = True
            employee.save()
            success += 1
            
        log_name = self.create_import_log('Employee Status', total_data, success, existed, errors, headers, error_msgs)
        self.show_import_status('Employee Status', total_data, success, existed, errors, headers, error_msgs, log_name)

    @frappe.whitelist()
    def import_experiences(self, company_id):
        path = 'https://www.mosyr.io/en/api/migration-employee-experiences.json?company_id={}'
        data = self.call_api(path, company_id, 'Employee Experience')
        headers = [_('Employee Id'), _('Experience Key'), _('Error')]
        error_msgs = []
        total_data = len(data)
        errors = 0
        success = 0
        existed = 0

        attachment_field = ['attachement']
        ignored_fields = ['name']
        date_fields = ['star_date', 'end_date']
        mapped_fields = {
            'certificate_experience_file': 'certificate_experience',
            'company': 'company_name',
        }
        link_fields = []

        for d in data:
            d = self.get_clean_data(d)
            key = d.get('key', '')
            nid = d.get('nid', False)
            if not nid:
                errors += 1
                error_msgs.append(['Unknown', key, _('Missing Employee nid')])
                continue

            employees_with_nid = frappe.get_list('Employee', filters={'key': nid})
            if len(employees_with_nid) == 0:
                errors += 1
                error_msgs.append([nid, '', _('Employee not found')])
                continue
            
            employee = frappe.get_doc('Employee', employees_with_nid[0].name)
            args = {}

            for k, v in d.items():
                k = f'{k}'.lower()
                k = mapped_fields.get(k, k)
                if k in attachment_field: continue
                if k in ignored_fields: continue

                if k in date_fields and v != '':
                    v = getdate(v)
                args.update({f'{k}': v})
            
            if len(employee.external_work_history) > 0:
                for idx, eid in enumerate(employee.external_work_history):
                    if eid.key == key:
                        external_work_history = employee.external_work_history[idx]
                        external_work_history.update(args)
            else:
                employee.append('external_work_history', args)
            employee.flags.ignore_mandatory = True
            employee.save()
            success += 1
            
        log_name = self.create_import_log('Employee Experience', total_data, success, existed, errors, headers, error_msgs)
        self.show_import_status('Employee Experience', total_data, success, existed, errors, headers, error_msgs, log_name)
    
    @frappe.whitelist()
    def import_passport(self, company_id):
        path = 'https://www.mosyr.io/en/api/migration-passports.json?company_id={}'
        data = self.call_api(path, company_id, 'Employee Passport')
        headers = [_('Employee Id'), _('Passport Key'), _('Error')]
        error_msgs = []
        total_data = len(data)
        errors = 0
        success = 0
        existed = 0

        attachment_field = ['passport_photo']
        ignored_fields = ['name']
        date_fields = ['passport_expire', 'passport_issue_date']
        mapped_fields = {}
        link_fields = []

        for d in data:
            d = self.get_clean_data(d)
            key = d.get('key', '')
            nid = d.get('nid', False)
            passport_number = d.get('nid', False)
            if not nid:
                errors += 1
                error_msgs.append(['Unknown', key, _('Missing Employee nid')])
                continue
            
            if not passport_number:
                errors += 1
                error_msgs.append([nid, key, _('Missing Passport Number')])
                continue

            employees_with_nid = frappe.get_list('Employee', filters={'key': nid})
            if len(employees_with_nid) == 0:
                errors += 1
                error_msgs.append([nid, '', _('Employee not found')])
                continue
            
            employee = frappe.get_doc('Employee', employees_with_nid[0].name)
            args = {}
            attachments_data = []
            for k, v in d.items():
                k = f'{k}'.lower()
                k = mapped_fields.get(k, k)
                if k in ignored_fields: continue
                if k in attachment_field and isinstance(v, dict):
                    attachments_data.append(v)
                    continue

                if k in date_fields and v != '':
                    v = getdate(v)
                if k in ['passport_expire_h', 'passport_issue_date_h'] and v != '':
                    temp_v = f'{v}'.split('-')
                    if len(temp_v) == 3:
                        if cint(temp_v[0]) > cint(temp_v[-1]):
                            temp_v.reverse()
                            v = '-'.join(temp_v)
                args.update({f'{k}': v})
            
            is_new = True
            new_idx = -1
            
            for idx, eid in enumerate(employee.passport):
                if eid.key == key:
                    passport = employee.passport[idx]
                    passport.update(args)
                    is_new = False
                    new_idx = idx
            if is_new:
                new_idx = len(employee.passport)
                employee.append('passport', args)
            
            employee.flags.ignore_mandatory = True
            employee.save()
            frappe.db.commit()
            
            for att in attachments_data:
                att = att.get("filename", False)
                if att:
                    source_path = "https://www.mosyr.io/sites/default/files/"
                    is_downloaded, _file = self.download_mosyr_file("Employee", employee.name, 'passport_photo', source_path, att)
                    if is_downloaded and new_idx != -1:
                        employee = frappe.get_doc('Employee', employee.name)
                        passport = employee.passport[new_idx]
                        passport.passport_photo = _file['file_url']
                        employee.flags.ignore_mandatory = True
                        employee.save()
                        frappe.db.commit()
            success += 1
        frappe.db.commit()
        log_name = self.create_import_log('Employee Passport', total_data, success, existed, errors, headers, error_msgs)
        self.show_import_status('Employee Passport', total_data, success, existed, errors, headers, error_msgs, log_name)
    
    @frappe.whitelist()
    def import_employee_qualifications(self, company_id):
        path = 'https://www.mosyr.io/en/api/migration-employee-qualifications.json?company_id={}'
        data = self.call_api(path, company_id, 'Employee Qualification')
        headers = [_('Employee Id'), _('Qualification Key'), _('Error')]
        error_msgs = []
        total_data = len(data)
        errors = 0
        success = 0
        existed = 0

        attachment_field = ['attachment']
        ignored_fields = ['name']
        date_fields = ['attendance_date', 'issue_date']
        mapped_fields = {
            'specialization': 'qualification',
            'qualification_mark': 'class_per',
            'attachement': 'attachment',
            'degree': 'qualification_degree'
        }
        degree_lookup_value = {
            "_none": "None",
            "primary": "Primary school",
            "secondary": "Secondary school",
            "hight": "hight school",
            "diploma": "Diploma",
            "academic": "Academic",
            "training": "Training Certificate",
        }
        link_fields = []
        
        for d in data:
            d = self.get_clean_data(d)
            key = d.get('key', '')
            nid = d.get('nid', False)
            passport_number = d.get('nid', False)
            if not nid:
                errors += 1
                error_msgs.append(['Unknown', key, _('Missing Employee nid')])
                continue

            employees_with_nid = frappe.get_list('Employee', filters={'key': nid})
            if len(employees_with_nid) == 0:
                errors += 1
                error_msgs.append([nid, '', _('Employee not found')])
                continue
            
            employee = frappe.get_doc('Employee', employees_with_nid[0].name)
            args = {}

            attachments_data = []
            for k, v in d.items():
                k = f'{k}'.lower()
                k = mapped_fields.get(k, k)
                if k in ignored_fields: continue
                if k in attachment_field and isinstance(v, dict):
                    attachments_data.append(v)
                    continue
                if k == 'qualification_degree':
                    v = degree_lookup_value.get(v, 'None')
                if k in date_fields and v != '':
                    v = getdate(v)
                args.update({f'{k}': v})
            
            is_new = True
            new_idx = -1
            
            for idx, eid in enumerate(employee.education):
                if eid.key == key:
                    education = employee.education[idx]
                    education.update(args)
                    is_new = False
                    new_idx = idx
            if is_new:
                new_idx = len(employee.education)
                employee.append('education', args)
            
            employee.flags.ignore_mandatory = True
            employee.save()
            frappe.db.commit()
            
            for att in attachments_data:
                att = att.get("filename", False)
                if att:
                    source_path = "https://www.mosyr.io/sites/default/files/"
                    is_downloaded, _file = self.download_mosyr_file("Employee", employee.name, 'attachment', source_path, att)
                    if is_downloaded and new_idx != -1:
                        employee = frappe.get_doc('Employee', employee.name)
                        qual = employee.education[new_idx]
                        qual.attachment = _file['file_url']
                        employee.flags.ignore_mandatory = True
                        employee.save()
                        frappe.db.commit()

            success += 1
            
        log_name = self.create_import_log('Employee Qualification', total_data, success, existed, errors, headers, error_msgs)
        self.show_import_status('Employee Qualification', total_data, success, existed, errors, headers, error_msgs, log_name)

    @frappe.whitelist()
    def import_contracts(self, company_id):
        path = 'https://www.mosyr.io/en/api/migration-contracts.json?company_id={}'
        data = self.call_api(path, company_id, 'Employee Contract')
        headers = [_('Contract Key'), _('Error')]
        error_msgs = []
        total_data = len(data)
        errors = 0
        success = 0
        existed = 0

        attachment_field = ['attached_documents', 'job_description_file', 'hiring_letter']
        ignored_fields = ['nid', 'name']
        date_fields = [
            'contract_start_date', 'contract_end_date', 'hiring_start_date', 'allowance_living_end_date',
            'allowance_living_start_date', 'allowance_housing_end_date', 'allowance_housing_start_date',
            'allowance_worknatural_end_date', 'allowance_worknatural_start_date', 'allowance_other_end_date',
            'allowance_other_start_date', 'allowance_phone_end_date', 'allowance_phone_start_date',
            'allowance_trans_end_date', 'allowance_trans_start_date'
        ]
        mapped_fields = {}

        finan_values_lookup = {
            'none': 'None',
            'covered': 'Covered',
            'cash': 'Cash'
        }
        finan_fields = [
            'allowance_phone', 'allowance_living', 'allowance_trans', 
            'allowance_worknatural', 'allowance_housing', 'allowance_other']

        yes_no_lookup = {
            'no': 'No',
            'yes': 'Yes',
            'travelticketsself': 'Employee Only',
            'selfspouse': 'Employee & Spouse',
            'selfspouse1dep': 'Family with 1 Dependant',
            'selfspouse2dep': 'Family with 2 Dependant',
            'selfspouse3dep': 'Family with 3 Dependant',
            'selfspouse4dep': 'Family with 4 Dependant',
            'family': 'All Family'
        }
        yes_no_fields = ['commision', 'commision_at_end_of_contract', 'vacation_travel_tickets', 'over_time_included']

        ctype_lookup = {
            'married': 'Married',
            'notmarried': 'Not Married',
            'temporary': 'Temporary',
            'lump': 'Lump',
            'theindefinite': 'The Indefinite',
            'fixed term': 'Fixed Term',
        }
        cstatus_lookup = {
            'valid': 'Valid',
            'not-valid': 'Not Valid',
        }
        values_lookup = {
            'fixed': 'Fixed',
            'percentage': 'Percentage',
            'monthly': 'Monthly',
            'onetime': 'One Time',
            'twotimes': 'Two Times',
        }

        link_fields = []
        for d in data:
            d = self.get_clean_data(d)
            key = d.get('key', '')
            nid = d.get('nid', False)
            if not nid:
                errors += 1
                error_msgs.append([key, _('Missing Employee nid')])
                continue

            employees_with_nid = frappe.get_list('Employee', filters={'key': nid})
            if len(employees_with_nid) == 0:
                errors += 1
                error_msgs.append([key, _(f'Employee <b>{nid}</b> not found')])
                continue
            
            contract_type = d.get('contract_type', False)
            if not contract_type:
                errors += 1
                error_msgs.append([key, _('Missing Contract Type')])
                continue

            contract_status = d.get('contract_status', False)
            if not contract_status:
                errors += 1
                error_msgs.append([key, _('Missing Contract Status')])
                continue
            
            nid = employees_with_nid[0].name
            args = {
                'employee': nid
            }

            new_cont = frappe.new_doc("Employee Contract")
            con_with_same_key = frappe.get_list('Employee Contract', filters={'key': key})
            if len(con_with_same_key) > 0:
                existed += 1
                new_cont = frappe.get_doc('Employee Contract', con_with_same_key[0].name)
                if new_cont.docstatus == 1:
                    errors += 1
                    error_msgs.append([key, _('Employee Deduction is Submited')])
                    continue
            
            attachments_data = []
            for k, v in d.items():
                k = f'{k}'.lower()
                k = mapped_fields.get(k, k)
                if k == 'attached_documents' and v != '':
                    if isinstance(v, list): attachments_data = attachments_data  + v
                    else: attachments_data.append(v)
                    continue
                
                if k in attachment_field: continue
                if k in ignored_fields: continue
                
                v = values_lookup.get(f'{v}', v)
                if k in finan_fields:
                    v = finan_values_lookup.get(v, 'None')
                
                if k in yes_no_fields:
                    v = yes_no_lookup.get(v, 'No')
                
                if k in date_fields and (v != '' or isinstance(v, list)):
                    v = getdate(v)
                
                if k == 'contract_type':
                    v = ctype_lookup.get(v, 'Temporary')
                
                if k == 'contract_status':
                    v = cstatus_lookup.get(v, 'Not Valid')
                
                
                if k in ['basic_salary', 'leaves_consumed_balance']:
                    v = flt(v)
                
                if k == 'vacation_period':
                    v = cint(v)
                if k == 'commision_precentage':
                    v = f'{v}'.replace('%', '')
                    v = flt(v)

                args.update({f'{k}': v})
            
            new_cont.update(args)
            new_cont.save()
            success += 1
            frappe.db.commit()
            
            
            new_cont = frappe.get_doc('Employee Contract', new_cont.name)
            hiring_letter = d.get('hiring_letter', '')
            if len(hiring_letter) > 0:
                file_name = hiring_letter.split('/')[-1]
                source_path = '/'.join(hiring_letter.split('/')[:-1])
                source_path = f'{source_path}/'
                is_downloaded, _file  = self.download_mosyr_file('Employee Contract', new_cont.name, 'hiring_letter', source_path, file_name)
                if is_downloaded:
                    new_cont = frappe.get_doc('Employee Contract', new_cont.name)
                    new_cont.hiring_letter = _file['file_url']
                    new_cont.save()
                    frappe.db.commit()
            
            job_description_file = d.get('job_description_file', '')
            if len(job_description_file) > 0:
                file_name = job_description_file.split('/')[-1]
                source_path = '/'.join(job_description_file.split('/')[:-1])
                source_path = f'{source_path}/'
                is_downloaded, _file  = self.download_mosyr_file('Employee Contract', new_cont.name, 'job_description_file', source_path, file_name)
                if is_downloaded:
                    new_cont = frappe.get_doc('Employee Contract', new_cont.name)
                    new_cont.job_description_file = _file['file_url']
                    new_cont.save()
                    frappe.db.commit()
            attached_documents = d.get('attached_documents', [])
            if isinstance(attached_documents, list):
                for ad in attached_documents:
                    file_name = ad.split('/')[-1]
                    source_path = '/'.join(ad.split('/')[:-1])
                    source_path = f'{source_path}/'
                    is_downloaded, _file  = self.download_mosyr_file('Employee Contract', new_cont.name, 'attachment', source_path, file_name)
                    if is_downloaded:
                        new_cont = frappe.get_doc('Employee Contract', new_cont.name)
                        new_cont.append('attachments', {
                            'attachment': _file['file_url']
                        })
                        new_cont.save()
                        frappe.db.commit()
            frappe.db.commit()

            
        log_name = self.create_import_log('Employee Contract', total_data, success, existed, errors, headers, error_msgs)
        self.show_import_status('Employee Contract', total_data, success, existed, errors, headers, error_msgs, log_name)
    
    @frappe.whitelist()
    def import_letters(self, company_id):
        path = 'https://www.mosyr.io/en/api/migration-letters.json?company_id={}'
        data = self.call_api(path, company_id, 'Letter')
        headers = [_('Letter Id'), _('Error')]
        error_msgs = []
        total_data = len(data)
        errors = 0
        success = 0
        existed = 0
        lookup_value = {
            'yes': 'Yes',
            'no': 'No',
            'definition': 'Definition',
            'letter of disclaimer': 'Letter of Disclaimer',
            'letter final clearance': 'Letter final Clearance',
            'experience certificate': 'Experience Certificate',
            'alert 1': 'Alert 1',
            'alert 2': 'Alert 2',
            'alert 3': 'Alert 3',
            'bo': 'Both',
            'both': 'Both'
        }
        attachment_field = ['attachement']
        ignored_fields = ['nid']
        date_fields = ['letter_date']
        mapped_fields = {
            'name': 'purpose',
            'letter date g': 'letter_date',
            'letter_head': 'letterhead'
        }
        link_fields = []
        
        for d in data:
            d = self.get_clean_data(d)
            key = d.get('key', '')
            name = d.get('name', False)
            if not name:
                errors += 1
                error_msgs.append([key, _('Missing Letter Purpose')])
                continue
            
            nid = d.get('nid', False)
            if not nid:
                errors += 1
                error_msgs.append([key, _('Missing Employee nid')])
                continue
            
            letter_type = d.get('letter_type', False)
            if not letter_type:
                errors += 1
                error_msgs.append([key, _('Missing Letter Type')])
                continue

            include_details_salary = d.get('include_details_salary', False)
            if not include_details_salary:
                errors += 1
                error_msgs.append([key, _('Missing Include Detailes Salary Value')])
                continue
            
            language_type = d.get('language_type', False)
            if not language_type:
                errors += 1
                error_msgs.append([key, _('Missing Language Type')])
                continue

            letter_head = d.get('letter_head', False)
            if not letter_head:
                errors += 1
                error_msgs.append([key, _('Missing Letter Head')])
                continue
            
            include_salary = d.get('include_salary', False)
            if not letter_head:
                errors += 1
                error_msgs.append([key, _('Missing Include Salary Value')])
                continue
            
            employees_with_nid = frappe.get_list('Employee', filters={'key': nid})
            if len(employees_with_nid) == 0:
                errors += 1
                error_msgs.append([key, _('Employee Not Found')])
                continue
            nid = employees_with_nid[0].name

            new_letter = frappe.new_doc("Letter")
            letters_with_same_key = frappe.get_list('Letter', filters={'key': key})
            if len(letters_with_same_key) > 0:
                existed += 1
                new_letter = frappe.get_doc('Letter', letters_with_same_key[0].name)
            
            attachments_data = []
            args = {'employee': nid}
            for k, v in d.items():
                k = f'{k}'.lower()
                k = mapped_fields.get(k, k)
                
                if k in ignored_fields: continue
                if k in attachment_field and isinstance(v, dict):
                    attachments_data.append(v)
                    continue
                if k in date_fields and v != '':
                    v = getdate(v)
                v = lookup_value.get(v, v)
                args.update({f'{k}': v})
                
            new_letter.update(args)
            new_letter.save()
            frappe.db.commit()
            for att in attachments_data:
                att = att.get("filename", False)
                if att:
                    source_path = "https://www.mosyr.io/sites/default/files/"
                    is_downloaded, _file  = self.download_mosyr_file('Letter', new_letter.name, 'attachment', source_path, att)
                    if is_downloaded:
                        new_letter = frappe.get_doc('Letter', new_letter.name)
                        new_letter.attachment = _file['file_url']
                        new_letter.save()
                        frappe.db.commit()
            success += 1
        frappe.db.commit()
        log_name = self.create_import_log('Letter', total_data, success, existed, errors, headers, error_msgs)
        self.show_import_status('Letter', total_data, success, existed, errors, headers, error_msgs, log_name)
    
    @frappe.whitelist()
    def import_deductions(self, company_id):
        path = 'https://www.mosyr.io/en/api/migration-deductions.json?company_id={}'
        data = self.call_api(path, company_id, 'Employee Deduction')
        headers = [_('Deduction Id'), _('Error')]
        error_msgs = []
        total_data = len(data)
        errors = 0
        success = 0
        existed = 0
        lookup_value = {}
        attachment_field = []
        ignored_fields = ['nid', 'name']
        date_fields = ['created_at']
        mapped_fields = {
            'created': 'created_at'
        }
        
        link_fields = []
        for d in data:
            d = self.get_clean_data(d)
            key = d.get('key', '')
            
            nid = d.get('nid', False)
            if not nid:
                errors += 1
                error_msgs.append([key, _('Missing Employee nid')])
                continue
            
            amount = flt(d.get('amount', False))
            if not amount or amount == 0:
                errors += 1
                error_msgs.append([key, _('Missing Amount Value')])
                continue

            employees_with_nid = frappe.get_list('Employee', filters={'key': nid})
            if len(employees_with_nid) == 0:
                errors += 1
                error_msgs.append([key, _('Employee Not Found')])
                continue
            
            nid = employees_with_nid[0].name

            new_ed = frappe.new_doc("Employee Deduction")
            ed_with_same_key = frappe.get_list('Employee Deduction', filters={'key': key})
            if len(ed_with_same_key) > 0:
                existed += 1
                new_ed = frappe.get_doc('Employee Deduction', ed_with_same_key[0].name)
                if new_ed.docstatus == 1:
                    errors += 1
                    error_msgs.append([key, _('Employee Deduction is Submited')])
                    continue
            
            attachments_data = []
            args = {'employee': nid}
            for k, v in d.items():
                k = f'{k}'.lower()
                k = mapped_fields.get(k, k)
                
                if k in ignored_fields: continue
                if k in attachment_field: continue
                if k in date_fields and v != '':
                    v = getdate(v)
                args.update({f'{k}': v})
            
            new_ed.update(args)
            new_ed.save()
            frappe.db.commit()
            # new_ed.submit()
            success += 1
            
        log_name = self.create_import_log('Employee Deduction', total_data, success, existed, errors, headers, error_msgs)
        self.show_import_status('Employee Deduction', total_data, success, existed, errors, headers, error_msgs, log_name)

    @frappe.whitelist()
    def import_benefits(self, company_id):
        path = 'https://www.mosyr.io/en/api/migration-benefits.json?company_id={}'
        data = self.call_api(path, company_id, 'Employee Benefit')
        headers = [_('Benefit Id'), _('Error')]
        error_msgs = []
        total_data = len(data)
        errors = 0
        success = 0
        existed = 0
        
        lookup_value = {
            "_none": "None",
            "backpay": "Back Pay",
            "bonus": "Bonus",
            "overtime": "Overtime",
            "business_trip": "Business Trip",
            "commission": "Commission"
        }
        attachment_field = []
        ignored_fields = ['nid', 'name']
        date_fields = ['created_at']
        mapped_fields = {
            'created': 'created_at'
        }
        
        link_fields = []
        for d in data:
            d = self.get_clean_data(d)
            key = d.get('key', '')
            
            nid = d.get('nid', False)
            if not nid:
                errors += 1
                error_msgs.append([key, _('Missing Employee nid')])
                continue
            
            amount = flt(d.get('amount', False))
            if not amount or amount == 0:
                errors += 1
                error_msgs.append([key, _('Missing Amount Value')])
                continue

            payroll_month = d.get('payroll_month', False)
            if not payroll_month:
                errors += 1
                error_msgs.append([key, _('Missing Payroll Month Value')])
                continue

            employees_with_nid = frappe.get_list('Employee', filters={'key': nid})
            if len(employees_with_nid) == 0:
                errors += 1
                error_msgs.append([key, _('Employee Not Found')])
                continue
            
            nid = employees_with_nid[0].name

            new_eb = frappe.new_doc("Employee Benefit")
            ed_with_same_key = frappe.get_list('Employee Benefit', filters={'key': key})
            if len(ed_with_same_key) > 0:
                existed += 1
                new_eb = frappe.get_doc('Employee Benefit', ed_with_same_key[0].name)
                if new_eb.docstatus == 1:
                    errors += 1
                    error_msgs.append([key, _('Employee Benefit is Submited')])
                    continue
            
            attachments_data = []
            args = {'employee': nid}
            for k, v in d.items():
                k = f'{k}'.lower()
                k = mapped_fields.get(k, k)
                
                if k in ignored_fields: continue
                if k in attachment_field: continue
                if k in date_fields and v != '':
                    v = getdate(v)
                if k == "addition_type":
                    to_check = f'{v}'.lower()
                    v = lookup_value.get(to_check, "None")
                args.update({f'{k}': v})
            
            new_eb.update(args)
            new_eb.save()
            # new_eb.submit()
            frappe.db.commit()
            success += 1
            
        log_name = self.create_import_log('Employee Benefit', total_data, success, existed, errors, headers, error_msgs)
        self.show_import_status('Employee Benefit', total_data, success, existed, errors, headers, error_msgs, log_name)

    @frappe.whitelist()
    def import_overtime(self, company_id):
        path = 'https://www.mosyr.io/en/api/migration-overtime.json?company_id={}'
        data = self.call_api(path, company_id, 'Employee Overtime')
        headers = [_('Overtime Id'), _('Error')]
        error_msgs = []
        total_data = len(data)
        errors = 0
        success = 0
        existed = 0
        

        attachment_field = []
        ignored_fields = ['nid', 'name']
        date_fields = ['created_at']
        mapped_fields = {
            'overtime_hours_by_1.5': 'overtime_hours_by_1_5'
        }
        
        link_fields = []
        for d in data:
            d = self.get_clean_data(d)
            key = d.get('key', '')
            
            nid = d.get('nid', False)
            if isinstance(nid, dict):
                nid = nid.get('target_id', False)
            else:
                nid = False
            
            if not nid:
                errors += 1
                error_msgs.append([key, _('Missing Employee nid')])
                continue
            
            amount = flt(d.get('amount', 0))
            if not amount or amount == 0:
                errors += 1
                error_msgs.append([key, _('Missing Amount Value')])
                continue

            payroll_month = d.get('payroll_month', False)
            if not payroll_month:
                errors += 1
                error_msgs.append([key, _('Missing Payroll Month Value')])
                continue

            employees_with_nid = frappe.get_list('Employee', filters={'key': nid})
            if len(employees_with_nid) == 0:
                errors += 1
                error_msgs.append([key, _('Employee Not Found')])
                continue

            new_eb = frappe.new_doc("Employee Overtime")
            ed_with_same_key = frappe.get_list('Employee Overtime', filters={'key': key})
            if len(ed_with_same_key) > 0:
                existed += 1
                new_eb = frappe.get_doc('Employee Overtime', ed_with_same_key[0].name)
                if new_eb.docstatus == 1:
                    errors += 1
                    error_msgs.append([key, _('Employee Overtime is Submited')])
                    continue
            
            by_2 = flt(d.get('overtime_hours_by_2', 0))
            by_1_5 = flt(d.get('overtime_hours_by_1.5', 0))
            hour_rate = 0
            args = {'employee': employees_with_nid[0].name}
            if (by_2+by_1_5) == 0:
                # errors += 1
                # error_msgs.append([key, _('Overtime Hours are 0')])
                # continue
                args.update({
                    'overtime_hours_by_2': 0,
                    'overtime_hours_by_1.5': 0,
                    'from_biometric': 1,
                    'hour_rate': 0
                })
            else:
                hour_rate = flt(amount) / (by_2*2+by_1_5*1.5)
                args.update({
                    'hour_rate': hour_rate
                })

            nid = employees_with_nid[0].name
            attachments_data = []
            
            
            for k, v in d.items():
                k = f'{k}'.lower()
                k = mapped_fields.get(k, k)
                
                if k in ignored_fields: continue
                if k in attachment_field: continue
                if k in date_fields and v != '':
                    v = getdate(v)
                if k in ['overtime_hours_by_1_5', 'overtime_hours_by_2', 'amount']:
                    v = flt(v)
                
                args.update({f'{k}': v})
            
            new_eb.update(args)
            new_eb.save()
            frappe.db.commit()
            # new_eb.submit()
            success += 1
            
        log_name = self.create_import_log('Employee Overtime', total_data, success, existed, errors, headers, error_msgs)
        self.show_import_status('Employee Overtime', total_data, success, existed, errors, headers, error_msgs, log_name)

    @frappe.whitelist()
    def import_main_settings(self, company_id):
        path = 'https://www.mosyr.io/api/company_status.json?field_account_target_id={}'
        data = self.call_api(path, company_id, 'Main Settings')
        headers = [_('Error')]
        error_msgs = []
        total_data = len(data)
        company_id_doc = frappe.db.exists('Company Id', company_id)
        if not company_id_doc:
            error_msgs.append(_('Company Id not found in the system'))
            log_name = self.create_import_log('Main Settings', 0, 0, 0, 1, headers, error_msgs)
            self.show_import_status('Main Settings', 0, 0, 0, 1, headers, error_msgs, log_name)
            return
        company_id_doc = frappe.get_doc('Company Id', company_id)
        company_doc = frappe.db.exists('Company', company_id_doc.company)
        if not company_doc:
            error_msgs.append(_('Company not found in the system'))
            log_name = self.create_import_log('Main Settings', 0, 0, 0, 1, headers, error_msgs)
            self.show_import_status('Main Settings', 0, 0, 0, 1, headers, error_msgs, log_name)
            return

        company_doc = frappe.get_doc('Company', company_id_doc.company)
        main_settings = frappe.get_doc('Company', company_doc.name)

        if isinstance(data, list):
            if len(data) == 1:
                main_data = data[0]
                main_data = self.get_clean_data(main_data)
                
                mail_sender_address = main_data.get('mail_sender_address', '')
                mail_sender_name = main_data.get('mail_sender_name', '')
                cid = main_data.get('cid', '')

                mobile = main_data.get('mobile', '')
                bank_name = main_data.get('bank_name', '')
                bank_code = main_data.get('bank_code', '')
                bank_account_number = main_data.get('bank_account_number', '')
                sender_name_sms = main_data.get('sender_name_sms', '')
                organization_english = main_data.get('organization_english', '')
                english_name_in_bank = main_data.get('english_name_in_bank', '')
                
                overtime_hours = main_data.get('overtime_hours', '')
                attendance_service = main_data.get('attendance_service', '')
                pension_percentage_on_company = main_data.get('pension_percentage_on_company', '')
                pension_percentage_on_company = pension_percentage_on_company.replace('%', '')
                pension_percentage_on_employee = main_data.get('pension_percentage_on_employee', '')
                pension_percentage_on_employee = pension_percentage_on_employee.replace('%', '')
                risk_percentage_on_company = main_data.get('risk_percentage_on_company', '')
                risk_percentage_on_company = risk_percentage_on_company.replace('%', '')
                risk_percentage_on_employee = main_data.get('risk_percentage_on_employee', '')
                risk_percentage_on_employee = risk_percentage_on_employee.replace('%', '')
                
                first_absence_value = main_data.get('first_absence_value', '')
                other_absences_value = main_data.get('other_absences_value', '')
                first_delay_value = main_data.get('first_delay_value', '')
                other_delays_value = main_data.get('other_delays_value', '')

                payroll_type = main_data.get('payroll_type', 'payroll')
                month_days = main_data.get('month_days', '22')
                
                main_settings.mail_sender_address = f"{mail_sender_address}"
                main_settings.mail_sender_name = f"{mail_sender_name}"
                main_settings.company_id = f"{company_id_doc.company_id}"
                main_settings.sender_name_sms = f"{sender_name_sms}"
                main_settings.organization_english = f"{organization_english}"
                main_settings.english_name_in_bank = f"{english_name_in_bank}"
                
                main_settings.mobile = f"{mobile}"
                if bank_name:
                    if len(bank_name) > 0:
                        is_new, v = self.check_link_data('Bank', bank_name, 'bank_name')
                        bank_doc = frappe.get_doc('Bank', v)
                        bank_doc.bank_name = bank_name
                        if len(bank_code) > 0:
                            bank_doc.swift_number = bank_code
                            main_settings.bank_code = bank_code
                        
                        bank_doc.save()
                        frappe.db.commit()
                        main_settings.bank = bank_doc.name
                        main_settings.bank_name = bank_name
                
                if len(bank_account_number) > 0:
                    main_settings.bank_account_number = bank_account_number
                
                if overtime_hours in ["1.5", "2", 1.5, 2]:
                    hl = {
                        "1.5": "Hour And Half",
                        "2": "Two Hours",
                    }

                    overtime_hours = hl.get(f"{overtime_hours}", "")
                    main_settings.overtime_hours = overtime_hours
                
                if f"{attendance_service}".lower() in ["active", "suspended", "terminated"]:
                    main_settings.attendance_service = f"{attendance_service}".capitalize()
                
                main_settings.pension_percentage_on_company = flt(pension_percentage_on_company)
                main_settings.pension_percentage_on_employee = flt(pension_percentage_on_employee)
                main_settings.risk_percentage_on_company = flt(risk_percentage_on_company)
                main_settings.risk_percentage_on_employee = flt(risk_percentage_on_employee)
                
                if first_absence_value in ['1', '1.5', '2', 1, 1.5, 2]:
                    main_settings.first_absence_value = f"{first_absence_value}"
                if other_absences_value in ['1', '1.5', '2', 1, 1.5, 2]:
                    main_settings.other_absences_value = f"{other_absences_value}"
                if first_delay_value in ['1', '1.5', '2', 1, 1.5, 2]:
                    main_settings.first_delay_value = f"{first_delay_value}"
                if other_delays_value in ['1', '1.5', '2', 1, 1.5, 2]:
                    main_settings.other_delays_value = f"{other_delays_value}"
                
                if f"{payroll_type}".lower() in ['payroll', 'wps', 'payrollcards']:
                    ptl = {
                        'payroll': 'Payroll',
                        'wps': 'WPS',
                        'payrollcards': 'Payroll Cards'
                    }
                    payroll_type = ptl.get(payroll_type, 'Payroll')
                    main_settings.disbursement_type = f"{payroll_type}".capitalize()

                if month_days in ['22', 22, '28', 28, '29', 29, '30', 30, 'calendar']:
                    if month_days == 'calendar':
                        month_days = 'Calendar'
                    main_settings.month_days = month_days
                else:
                    main_settings.month_days = '30'
                
                
                main_settings.overtime_hours = f"{overtime_hours}"
                comp_lookup = {
                    'basic_salary': 'Basic',
                    'housing': 'Allowance Housing',
                    'transportations': 'Allowance Trans',
                    'phone': 'Allowance Phone',
                    'feeding': 'Allowance Living',
                    'natureow': 'Allowance Worknatural',
                    'cash': 'Allowance Other'
                }
                employee_day_working = main_data.get('employee_day_working', [])
                if isinstance(employee_day_working, list):
                    main_settings.employee_day_working = []
                    for edw in employee_day_working:
                        edw = comp_lookup.get(edw, False)
                        if edw:
                            main_settings.append('employee_day_working', {
                                'component': edw
                            })
                
                employee_day_annual_vacation = main_data.get('employee_day_annual_vacation', [])
                if isinstance(employee_day_annual_vacation, list):
                    for edw in employee_day_annual_vacation:
                        edw = comp_lookup.get(edw, False)
                        main_settings.employee_day_annual_vacation = []
                        if edw:
                            main_settings.append('employee_day_annual_vacation', {
                                'component': edw
                            })
                
                employee_day_childbirth_vacation = main_data.get('employee_day_childbirth_vacation', [])
                if isinstance(employee_day_childbirth_vacation, list):
                    for edw in employee_day_childbirth_vacation:
                        edw = comp_lookup.get(edw, False)
                        main_settings.employee_day_childbirth_vacation = []
                        if edw:
                            main_settings.append('employee_day_childbirth_vacation', {
                                'component': edw
                            })
                
                employee_day_hajj_leave = main_data.get('employee_day_hajj_leave', [])
                if isinstance(employee_day_hajj_leave, list):
                    for edw in employee_day_hajj_leave:
                        edw = comp_lookup.get(edw, False)
                        main_settings.employee_day_hajj_leave = []
                        if edw:
                            main_settings.append('employee_day_hajj_leave', {
                                'component': edw
                            })
                
                emp_day_urgent_leave = main_data.get('emp_day_urgent_leave', [])
                if isinstance(emp_day_urgent_leave, list):
                    for edw in emp_day_urgent_leave:
                        edw = comp_lookup.get(edw, False)
                        main_settings.employee_day_urgent_leave = []
                        if edw:
                            main_settings.append('employee_day_urgent_leave', {
                                'component': edw
                            })
                
                employee_day_sick_leave = main_data.get('employee_day_sick_leave', [])
                if isinstance(employee_day_sick_leave, list):
                    for edw in employee_day_sick_leave:
                        edw = comp_lookup.get(edw, False)
                        main_settings.employee_day_sick_leave = []
                        if edw:
                            main_settings.append('employee_day_sick_leave', {
                                'component': edw
                            })
                
                employee_day_benefits_withoutpay_leave = main_data.get('employee_day_benefits_withoutpay_leave', [])
                if isinstance(employee_day_benefits_withoutpay_leave, list):
                    for edw in employee_day_benefits_withoutpay_leave:
                        edw = comp_lookup.get(edw, False)
                        main_settings.employee_day_benefits_with_out_pay_leave = []
                        if edw:
                            main_settings.append('employee_day_benefits_with_out_pay_leave', {
                                'component': edw
                            })
                
                emp_day_death_leave = main_data.get('emp_day_death_leave', [])
                if isinstance(emp_day_death_leave, list):
                    for edw in emp_day_death_leave:
                        edw = comp_lookup.get(edw, False)
                        main_settings.employee_day_death_leave = []
                        if edw:
                            main_settings.append('employee_day_death_leave', {
                                'component': edw
                            })
                
                end_of_services = main_data.get('end_of_services', [])
                if isinstance(end_of_services, list):
                    for edw in end_of_services:
                        edw = comp_lookup.get(edw, False)
                        main_settings.end_of_services = []
                        if edw:
                            main_settings.append('end_of_services', {
                                'component': edw
                            })
                
                emp_day_wedding_leave = main_data.get('emp_day_wedding_leave', [])
                if isinstance(emp_day_wedding_leave, list):
                    for edw in emp_day_wedding_leave:
                        edw = comp_lookup.get(edw, False)
                        main_settings.employee_day_wedding_leave = []
                        if edw:
                            main_settings.append('employee_day_wedding_leave', {
                                'component': edw
                            })
                
                unaccounted_deductions = main_data.get('unaccounted_deductions', [])
                if isinstance(unaccounted_deductions, list):
                    for edw in unaccounted_deductions:
                        edw = comp_lookup.get(edw, False)
                        main_settings.unaccounted_deductions = []
                        if edw:
                            main_settings.append('unaccounted_deductions', {
                                'component': edw
                            })
                
                banks_type_payroll = main_data.get('banks_type_payroll', [])
                if isinstance(banks_type_payroll, list):
                    for edw in banks_type_payroll:
                        main_settings.banks_type_payroll = []
                        if edw:
                            is_new, va = self.check_link_data('Bank', edw, 'bank_name')
                            main_settings.append('banks_type_payroll', {
                                'bank': edw
                            })
                
                working_in_weekend = main_data.get('working_in_weekend', [])
                if isinstance(working_in_weekend, list):
                    if 'Friday' in working_in_weekend or 'friday' in working_in_weekend:
                        main_settings.friday = 1
                    if 'Saturday' in working_in_weekend or 'saturday' in working_in_weekend:
                        main_settings.saterday = 1
                
                main_settings.save()
                frappe.db.commit()
                source_path = "https://www.mosyr.io/sites/default/files/"
                logo = main_data.get('logo', {})
                baladiya_license = main_data.get('baladiya_license', {})
                cr_document = main_data.get('cr_document', {})
                stamp = main_data.get('stamp', {})
                if isinstance(baladiya_license, dict):
                    filename = baladiya_license.get('filename', False)
                    if filename:
                        main_settings = frappe.get_doc('Company', main_settings.name)
                        is_downloaded, _file  = self.download_mosyr_file('Company', main_settings.name, 'baladiya_license', source_path, filename)
                        if is_downloaded:
                            main_settings = frappe.get_doc('Company', main_settings.name)
                            main_settings.db_set('baladiya_license', _file['file_url'])
                            # main_settings.save()
                            frappe.db.commit()
                if isinstance(stamp, dict):
                    filename = stamp.get('filename', False)
                    if filename:
                        main_settings = frappe.get_doc('Company', main_settings.name)
                        is_downloaded, _file  = self.download_mosyr_file('Company', main_settings.name, 'stamp', source_path, filename)
                        if is_downloaded:
                            main_settings = frappe.get_doc('Company', main_settings.name)
                            main_settings.db_set('stamp', _file['file_url'])
                            # main_settings.save()
                            frappe.db.commit()
                if isinstance(cr_document, dict):
                    filename = cr_document.get('filename', False)
                    if filename:
                        main_settings = frappe.get_doc('Company', main_settings.name)
                        is_downloaded, _file  = self.download_mosyr_file('Company', main_settings.name, 'cr_document', source_path, filename)
                        if is_downloaded:
                            main_settings = frappe.get_doc('Company', main_settings.name)
                            main_settings.db_set('cr_document', _file['file_url'])
                            # main_settings.save()
                            frappe.db.commit()
                if isinstance(logo, dict):
                    filename = logo.get('filename', False)
                    if filename:
                        main_settings = frappe.get_doc('Company', main_settings.name)
                        is_downloaded, _file  = self.download_mosyr_file('Company', main_settings.name, 'logo', source_path, filename)
                        if is_downloaded:
                            main_settings = frappe.get_doc('Company', main_settings.name)
                            main_settings.db_set('logo', _file['file_url'])

                        is_downloaded, _file  = self.download_mosyr_file('Company', company_doc.name, 'company_logo', source_path, filename)
                        if is_downloaded:
                            company_doc = frappe.get_doc('Company', company_doc.name)
                            company_doc.db_set('company_logo', _file['file_url'])
                            # main_settings.save()
                frappe.db.commit()
                
            else:
                error_msgs.append(_('Data Error, expected list with one record'))
                log_name = self.create_import_log('Main Settings', 0, 0, 0, 1, headers, error_msgs)
                self.show_import_status('Main Settings', 0, 0, 0, 1, headers, error_msgs, log_name)
        else:
            error_msgs.append(_('Data Error, expected list with one record'))
            log_name = self.create_import_log('Main Settings', '', '', '', 1, headers, error_msgs)
            self.show_import_status('Main Settings', '', '', '', 1, headers, error_msgs, log_name)

    @frappe.whitelist()
    def import_leave(self, company_id):
        path = 'https://www.mosyr.io/en/api/migration-leaves.json?company_id={}'
        data = self.call_api(path, company_id, 'Leave Type')        
        headers = [_('Leave Type'), _('Error')]
        error_msgs = []
        total_data = len(data)
        errors = 0
        success = 0
        existed = 0
        mapped_fields = {
            'leave_type': 'leave_type_name'
        }
        for d in data:
            d = self.get_clean_data(d)
            ltname = d.get('leave_type', '')
            if ltname != '':
                is_new, exist = self.check_link_data('Leave Type', ltname, 'leave_type_name')
                if is_new:
                    success += 1
                else:
                    existed += 1
            else:
                errors += 1
                error_msgs.append([ltname, _('Missing Leave Type Name')])
        log_name = self.create_import_log('Leave Type', total_data, success, existed, errors, headers, error_msgs)
        self.show_import_status('Leave Type', total_data, success, existed, errors, headers, error_msgs, log_name)
    
    @frappe.whitelist()
    def import_leave_application(self, company_id):
        errors = 0
        sucess = 0
        exists = 0
        error_msgs = ''
        path = 'https://www.mosyr.io/en/api/migration-leaves.json?company_id={}'
        data = self.call_api(path, company_id, 'Leave Application')
        mapped_fields = {
        }

        for d in data:
            d = self.get_clean_data(d)
            key = d.get('key')
            nid = d.get('nid')
            leave_attachments = ''
            from_date = d.get('leave_start_date', '')
            to_date = d.get('leave_end_date', '')
            leave_type = d.get('leave_type', '')
            employee_name_from_mosyr = d.get('name')
            if d.get('leave_attachments') not in (None, '', []):
                x = d.get('leave_attachments')
                splitted = x.split()
                str_match = [s for s in splitted if "href=" in s][0]
                split1 = str_match.split('"', -1)[1]
                leave_attachments = split1
            if nid:
                employees = frappe.get_list("Employee", filters={'key': nid})
                if len(employees) > 0:
                    employees = employees[0]
                    emp = frappe.get_doc("Employee", employees.name)
                    if emp.status in ("Active"):
                        name, employee_name = frappe.db.get_value(
                            'Employee', {'key': nid}, ['name', 'employee_name'])
                        if frappe.db.exists('Leave Application', {'key': key}):
                            exists += 1
                            continue
                        else:
                            leave = frappe.new_doc("Leave Application")
                            leave.leave_type_name = leave_type
                            leave.employee = name
                            leave.employee_name = employee_name
                            leave.from_date = from_date
                            leave.to_date = to_date
                            leave.key = key
                            leave.status = "Approved"
                            leave.leave_attachments = leave_attachments
                            file_output_name = f'{name}-leave application'
                            leave.save()
                            leave_name = frappe.get_value(
                                "Leave Application", {'key', key}, ['name'])
                            self.upload_file(
                                "Leave Application", leave_name, 'leave_attachments', file_output_name, leave_attachments)
                            leave.save()
                            frappe.db.commit()
                            sucess += 1
                    else:
                        msg = "Employee is not Active in System"
                        error_msgs += f'<tr><th>{nid}</th><td>{employee_name_from_mosyr}</td><td>{msg}</td></tr>'
                        errors += 1
                        continue

                else:
                    msg = "Employee is not exist in system"
                    error_msgs += f'<tr><th>{nid}</th><td>{employee_name_from_mosyr}</td><td>{msg}</td></tr>'
                    errors += 1
                    continue
        frappe.db.commit()
        self.handle_error(error_msgs, sucess, errors, data, exists)

    @frappe.whitelist()
    def handle_error(self, error_msgs, sucess, errors, data, exists):
        if exists:
            exists = f'<tr><th scope="row"><span class="indicator orange"></span>Exists</th><td>{exists}</td></tr>'
        else:
            exists = ''
        if len(error_msgs) > 0:
            error_msgs = f'''<table id = "table" class="table table-bordered">
							<thead>
							<tr>
							<th>Employee No.</th>
							<th>Name</th>
							<th>Error</th>
							</tr></thead>
							<tbody>{error_msgs}</tbody>
							</table>
							'''
        msg = f"""
		<table class="table table-bordered">
		<tbody>
			<tr>
			<th scope="row"><span class="indicator green"></span>Sucess</th>
			<td>{sucess}</td>
			</tr>
			{exists}
			<tr>
			<th scope="row"><span class="indicator red"></span>Errors</th>
			<td>{errors}</td>
			</tr>
		</tbody>
		</table>
		{'' if error_msgs is None else error_msgs}
		"""
        frappe.msgprint(msg, title=f'{len(data)} Employess Imported', indicator='Cs',
                        primary_action={
                            'label': _('Export Error Log 2'),
                            'client_action': 'mosyr.utils.download_errors',
                            'args': {
                                'data': 'e42237ba5e'
                            }
                        }
                        )

    def get_error_as_json(self, err):
        if not frappe.db.exists('Mosyr Data Import Log', err): return {}
        mdi = frappe.get_doc('Mosyr Data Import Log', err)
        return json.loads(mdi.error_json)
