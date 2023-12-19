from .attendance_policy import _AttendancePolicy
from ..constans import AppliedAttendancePolicy
from ..factory import Factory, DAO
import frappe


class _AbsentPolicy(_AttendancePolicy):
    def __init__(self, absent_policy_dict):
        super().__init__()
        for key, value in absent_policy_dict.items():
            setattr(self, key, value)

    def set_attributes(self):
        self.applied_policy = AppliedAttendancePolicy.ABSENT

    def apply(self, attendance) -> tuple[list[float], list[str], list[int]]:
        if not self._policies:
            frappe.throw(
                f"there is no {self.applied_policy} policy to apply. Please add some policies or disable it")

        amounts = self._get_amounts(attendance, 0)

        salary_components = self._get_salary_components(0, 1)

        policy_rows = self._get_policy_rows(0,1)

        minutes = [None] * len(amounts)

        return amounts, salary_components, policy_rows, minutes


class _AbsentPolicyDao(DAO):
    @staticmethod
    def create(shift_name: str):
        obj = {'_PREFIX_PENALTY_COLUMN_NAME': "no_of_absent", '_MAXIMUM_NUMBER_OF_POLICY_COLUMNS': 5,
               '_shift_name': shift_name}
        obj['_policies'] = frappe.db.sql(f"""
                                   SELECT  -1 AS `from`,
                                           1 AS `to`,
                                           /*
                                            this following expression will generate:
                                               no_of_absent_0,
                                               no_of_absent_1,
                                               no_of_absent_2,
                                               no_of_absent_3,
                                               no_of_absent_4,
                                            */
                                           {''.join(f"{obj['_PREFIX_PENALTY_COLUMN_NAME']}_{i}, "
                                                    for i in range(obj['_MAXIMUM_NUMBER_OF_POLICY_COLUMNS']))}
                                          salary_component,
                                          CAST((@row_number:=@row_number+1) AS UNSIGNED) AS policy_row
                                   FROM 
                                       `tabAbsent Table`
                                   WHERE 
                                       `tabAbsent Table`.parent = '{shift_name}'
                               """, as_dict=1)
        obj['_recorder'] = {}
        return _AbsentPolicy(obj)


class AbsentPolicyFactory(Factory):
    _store = {}

    @staticmethod
    def create(shift_name: str):
        if shift_name in AbsentPolicyFactory._store:
            return AbsentPolicyFactory._store[shift_name]
        else:
            AbsentPolicyFactory._store[shift_name] = _AbsentPolicyDao.create(shift_name)
            return AbsentPolicyFactory._store[shift_name]
