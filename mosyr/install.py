import frappe

def after_install():
    
    components = [
        {'component': 'Housing', 'abbr': 'H'},
        {},
        {}]
    
    {'Allowance Housing':'AH', 'Allowance Worknatural':'AW', 'Allowance Other':'AO',
                 'Allowance Phone':'AP', 'Allowance Trans':'AT', 'Allowance Living':'AL'}
                 
    for comp ,desc in components.items():
        salary_component = frappe.new_doc("Salary Component")
        salary_component.salary_component = comp
        salary_component.salary_component_abbr = desc
        salary_component.type = "Earning"
        salary_component.insert()
        frappe.db.commit()

    

