import frappe

def after_install():
    create_salary_components()
    # create_salary_structure()
    frappe.db.commit()

def create_salary_components():
    print('[*] Add Salary Components')
    components = [
        {'component': 'Housing',               'abbr': 'H'},
        {'component': 'Allowance Housing',     'abbr':'AH'},
        {'component': 'Allowance Worknatural', 'abbr':'AW'},
        {'component': 'Allowance Other',       'abbr':'AO'},
        {'component': 'Allowance Phone',       'abbr':'AP'},
        {'component': 'Allowance Trans',       'abbr':'AT'},
        {'component': 'Allowance Living',      'abbr':'AL'}]
                 
    for component in components:
        salary_component = component['component']
        if not frappe.db.exists('Salary Component', salary_component):
            salary_component_abbr = component['abbr']
            component_type = "Earning"
            salary_component_doc = frappe.new_doc("Salary Component")
            salary_component_doc.update({
                'salary_component': salary_component,
                'salary_component_abbr': salary_component_abbr,
                'type': component_type})
            salary_component_doc.save()

def create_salary_structure():
    components = [
        {'component': 'Housing',               'abbr': 'H'},
        {'component': 'Allowance Housing',     'abbr':'AH'},
        {'component': 'Allowance Worknatural', 'abbr':'AW'},
        {'component': 'Allowance Other',       'abbr':'AO'},
        {'component': 'Allowance Phone',       'abbr':'AP'},
        {'component': 'Allowance Trans',       'abbr':'AT'},
        {'component': 'Allowance Living',      'abbr':'AL'}]
    salary_structure_doc = frappe.new_doc('Salary Structure')
    company = frappe.defaults.get_global_default('company')
    company = frappe.get_doc('Company', company)
    salary_structure_doc.update({
        '__newname': 'Base Salary Structure',
        'is_active': 'Yes',
        'payroll_frequency': 'Monthly',
        'company': company.name,
        'currency': company.default_currency
    })

    for component in components:
        salary_component_abbr = component['abbr']
        salary_component = component['component']
        salary_structure_doc.append('earnings', {
            'salary_component': salary_component,
            'abbr': salary_component_abbr
        })
    salary_structure_doc.save()
    salary_structure_doc.submit()
