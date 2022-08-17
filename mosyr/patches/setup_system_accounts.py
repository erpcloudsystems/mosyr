from mosyr.install import prepare_mode_payments, prepare_system_accounts,hide_accounts_fields

def execute():
    prepare_mode_payments()
    prepare_system_accounts()
    hide_accounts_fields()