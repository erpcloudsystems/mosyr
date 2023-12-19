from .attendance_policy import _AttendancePolicy
from ..factory import Factory, DAO
from ..constans import AppliedAttendancePolicy
import frappe


class _MissingFingerprintPolicy(_AttendancePolicy):
    def __init__(self, missing_fingerprint_policy_dict):
        super().__init__()
        for key, value in missing_fingerprint_policy_dict.items():
            setattr(self, key, value)

    def set_attributes(self):
        self.applied_policy = AppliedAttendancePolicy.MISSING_FINGERPRINT

    def apply(self, attendance) -> tuple[list[float], list[str], list[int]]:
        if not self._policies:
            frappe.throw(
                f"there is no {self.applied_policy} policy to apply. Please add some policies or disable it")

        amounts = self._get_amounts(attendance, 0)

        salary_components = self._get_salary_components(0)

        policy_rows = self._get_policy_rows(0)

        minutes = [None] * len(amounts)

        return amounts, salary_components, policy_rows, minutes


class _MissingFingerprintPolicyDao(DAO):
    @staticmethod
    def create(shift_name):
        obj = {}
        obj['_PREFIX_PENALTY_COLUMN_NAME']: str = "no_of_missing_fingerprint"
        obj['_MAXIMUM_NUMBER_OF_POLICY_COLUMNS']: int = 5
        obj['_shift_name']: str = shift_name

        obj['_policies'] = frappe.db.sql(f"""
                            SELECT -1 AS `from`,
                                   1 AS `to`,
                                   /*
                                    this following expression will generate:
                                       no_of_early_leave_0,
                                       no_of_early_leave_1,
                                       no_of_early_leave_2,
                                       no_of_early_leave_3,
                                       no_of_early_leave_4,
                                    */
                                   {''.join(f"{obj['_PREFIX_PENALTY_COLUMN_NAME']}_{i}, "
                                            for i in range(obj['_MAXIMUM_NUMBER_OF_POLICY_COLUMNS']))}
                                  salary_component,
                                  CAST((@row_number:=@row_number+1) AS UNSIGNED) AS policy_row           
                           FROM 
                               `tabMissing Fingerprint Policy`, (SELECT @row_number:=-1) AS r
                           WHERE 
                               `tabMissing Fingerprint Policy`.parent = '{shift_name}'
                           ORDER BY
                               `from`, `to`
                """, as_dict=1)
        obj['_recorder'] = {}
        return _MissingFingerprintPolicy(obj)


class MissingFingerprintPolicyFactory(Factory):
    _store = {}

    @staticmethod
    def create(shift_name: str):
        if shift_name in MissingFingerprintPolicyFactory._store:
            return MissingFingerprintPolicyFactory._store[shift_name]
        else:
            MissingFingerprintPolicyFactory._store[shift_name] = _MissingFingerprintPolicyDao.create(shift_name)
            return MissingFingerprintPolicyFactory._store[shift_name]
