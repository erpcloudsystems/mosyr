import frappe

from .attendance_policy import _AttendancePolicy
from ..constans import AppliedAttendancePolicy
from ..factory import Factory, DAO


class _LateArrivalPolicy(_AttendancePolicy):
    def __init__(self, late_arrival_policy_dict):
        super().__init__()
        for key, value in late_arrival_policy_dict.items():
            setattr(self, key, value)

    def set_attributes(self):
        self.applied_policy = AppliedAttendancePolicy.LATE

    def apply(self, attendance) -> tuple[list[float], list[str], list[int]]:
        if not self._policies:
            frappe.throw(
                f"there is no {self.applied_policy} policy to apply. Please add some policies or disable it")

        minutes_after_grace_period = attendance.get_shift().get_arrival_minutes_after_grace_period(attendance)
        amounts = self._get_amounts(attendance, minutes_after_grace_period)

        salary_components = self._get_salary_components(minutes_after_grace_period)

        policy_rows = self._get_policy_rows(minutes_after_grace_period)

        minutes = [minutes_after_grace_period] * len(amounts)

        return amounts, salary_components, policy_rows, minutes


class _LateArrivalPolicyDao(DAO):
    @staticmethod
    def create(shift_name):
        obj = {}
        obj["_PREFIX_PENALTY_COLUMN_NAME"]: str = "no_of_late_arrival"
        obj["_MAXIMUM_NUMBER_OF_POLICY_COLUMNS"]: int = 5
        obj["_shift_name"]: str = shift_name

        obj["_policies"] = frappe.db.sql(f"""
                    SELECT from_after_grace_period AS `from`,
                            to_after_grace_period AS `to`,
                            /*
                             this following expression will generate:
                                no_of_late_arrival_0,
                                no_of_late_arrival_1,
                                no_of_late_arrival_2,
                                no_of_late_arrival_3,
                                no_of_late_arrival_4,
                             */
                            {''.join(f"{obj['_PREFIX_PENALTY_COLUMN_NAME']}_{i}, "
                                     for i in range(obj['_MAXIMUM_NUMBER_OF_POLICY_COLUMNS']))}
                           salary_component,
                           CAST((@row_number:=@row_number+1) AS UNSIGNED) AS policy_row           
                    FROM 

                        `tabLate Table`, (SELECT @row_number:=-1) AS r
                    WHERE 
                        `tabLate Table`.parent = '{shift_name}'
                    ORDER BY
                        `from`, `to`
                """, as_dict=1)
        obj['_recorder'] = {}
        return _LateArrivalPolicy(obj)


class LateArrivalPolicyFactory(Factory):
    _store = {}

    @staticmethod
    def create(shift_name: str):
        if shift_name in LateArrivalPolicyFactory._store:
            return LateArrivalPolicyFactory._store[shift_name]
        else:
            LateArrivalPolicyFactory._store[shift_name] = _LateArrivalPolicyDao.create(shift_name)
            return LateArrivalPolicyFactory._store[shift_name]
