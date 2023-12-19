class Employee:
    def __init__(self, emp_id):
        self._id = emp_id
        self._shifts = []

    # # assuming that employee could has more than one shift
    # # so return a list containing all his shifts
    # def get_shifts(self):
    #     if hasattr(self, '_shifts'):
    #         return self._shifts
    #     self._shifts = [Shift(name) for name in frappe.db.sql("SELECT ")]  # todo: pass parameter
    #     return self._shifts

    def get_id(self):
        return self._id
