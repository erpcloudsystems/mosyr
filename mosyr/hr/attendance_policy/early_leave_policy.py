from .attendance_policy import _AttendancePolicy
from ..factory import Factory, DAO
from ..constans import AppliedAttendancePolicy
import frappe


class _EarlyLeavePolicy(_AttendancePolicy):
    def __init__(self, early_leave_policy_dict):
        super().__init__()
        for key, value in early_leave_policy_dict.items():
            setattr(self, key, value)

    def set_attributes(self):
        self.applied_policy = AppliedAttendancePolicy.EARLY

    def apply(self, attendance) -> tuple[list[float], list[str], list[int]]:
        if not self._policies:
            frappe.throw(
                f"there is no {self.applied_policy} policy to apply. Please add some policies or disable it")

        minutes_before_grace_period = attendance.get_shift().get_leave_minutes_before_grace_period(attendance)
        amounts = self._get_amounts(attendance, minutes_before_grace_period)

        salary_components = self._get_salary_components(minutes_before_grace_period)

        policy_rows = self._get_policy_rows(minutes_before_grace_period)

        minutes = [minutes_before_grace_period] * len(amounts)

        return amounts, salary_components, policy_rows, minutes


class _EarlyLeavePolicyDao(DAO):
    @staticmethod
    def create(shift_name):
        obj = {}
        obj['_PREFIX_PENALTY_COLUMN_NAME']: str = "no_of_early_leave"
        obj['_MAXIMUM_NUMBER_OF_POLICY_COLUMNS']: int = 5
        obj['_shift_name']: str = shift_name
        obj['_policies'] = frappe.db.sql(f"""
                           SELECT from_after_grace_period AS `from`,
                                   to_after_grace_period AS `to`,
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
                               `tabEarly Leave Table`, (SELECT @row_number:=-1) AS r
                           WHERE 
                               `tabEarly Leave Table`.parent = '{shift_name}'
                           ORDER BY
                               `from`, `to`
                       """, as_dict=1)
        obj['_recorder'] = {}
        return _EarlyLeavePolicy(obj)


class EarlyLeavePolicyFactory(Factory):
    _store = {}

    @staticmethod
    def create(shift_name: str):
        if shift_name in EarlyLeavePolicyFactory._store:
            return EarlyLeavePolicyFactory._store[shift_name]
        else:
            EarlyLeavePolicyFactory._store[shift_name] = _EarlyLeavePolicyDao.create(shift_name)
            return EarlyLeavePolicyFactory._store[shift_name]
