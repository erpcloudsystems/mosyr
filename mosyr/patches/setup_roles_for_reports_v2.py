from mosyr.install import allow_read_for_reports
from erpnext.setup.install import create_custom_role

def execute():
    data = {"role": "SaaS Manager"}
    create_custom_role(data)
    allow_read_for_reports()