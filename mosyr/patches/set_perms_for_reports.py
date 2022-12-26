
def execute():
    from mosyr.install import add_select_perm_for_all, allow_read_for_reports
    add_select_perm_for_all()
    allow_read_for_reports()
