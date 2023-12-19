from abc import ABC, abstractmethod
from ..constans import AttendanceStatus
import frappe


# class _AttendancePolicy(ABC):
#     @abstractmethod
#     def apply(self, attendance):
#         pass  # todo
#
#     @abstractmethod
#     def _get_amounts(self, attendance) -> float:
#         pass  # todo
#
#     @abstractmethod
#     def _get_salary_components(self, attendance) -> str:
#         pass  # todo
#
#     @abstractmethod
#     def _get_policy_rows(self, attendance):
#         pass  # todo
#

class _AttendancePolicy(ABC):

    def __init__(self):
        self.set_attributes()

    @abstractmethod
    def set_attributes(self):
        pass

    def get_name(self):
        return self.applied_policy

    @abstractmethod
    def apply(self, attendance) -> tuple[list[float], list[str], list[int]]:
        pass  # todo

    def _get_amounts(self, attendance, minutes_after_grace_period: float = 0) -> list[float]:
        result = []
        for policy in self._policies:
            if policy['from'] < minutes_after_grace_period <= policy['to'] :
                policy_row = policy.policy_row
                if attendance.get_status() == AttendanceStatus.ABSENT:
                    policy_row = policy_row - 1 
                times_being_late = self._get_times_of_violating_policy(attendance, policy_row)

                result.append(self._policies[policy_row][
                                  f"{self._PREFIX_PENALTY_COLUMN_NAME}_{min(times_being_late, self._MAXIMUM_NUMBER_OF_POLICY_COLUMNS - 1)}"])

                self._recorder[
                    (attendance.get_employee().get_id(), attendance.get_payroll_start_date(), policy_row)] += 1

        if result:
            return result

        policy_row = self._policies[-1].policy_row
        times_being_late = self._get_times_of_violating_policy(attendance, policy_row)
        result.append(self._policies[policy_row][
                          f"{self._PREFIX_PENALTY_COLUMN_NAME}_{min(times_being_late, self._MAXIMUM_NUMBER_OF_POLICY_COLUMNS - 1)}"])

        self._recorder[
            (attendance.get_employee().get_id(), attendance.get_payroll_start_date(), policy_row)] += 1

        return result

    def _get_salary_components(self, minutes_after_grace_period: float,absent = 0) -> list[str]:
        result = []
        for policy in self._policies:
            
            if policy['from'] < minutes_after_grace_period <= policy['to']:
                policy_row = policy.policy_row
                
                if absent: 
                    policy_row = policy_row - 1
                result.append(self._policies[policy_row]['salary_component'])

        if result:
            return result

        return [self._policies[-1]['salary_component']]

    def _get_policy_rows(self, minutes_after_grace_period: float,absent = 0):
        results = []
        for policy in self._policies:
            if policy['from'] < minutes_after_grace_period <= policy['to']:
                policy_row = policy.policy_row 
                if absent: 
                    policy_row = policy_row - 1
                results.append(policy_row)

        if results:
            return results

        return [self._policies[-1].policy_row]

    def _get_times_of_violating_policy(self, attendance, policy_row: int) -> int:
        key = (attendance.get_employee().get_id(), attendance.get_payroll_start_date(), policy_row)
        if key not in self._recorder:
            self._recorder[key] = frappe.db.sql(
                f"""
                    SELECT COUNT(*)
                    FROM `tabExtra Salary` e
                    WHERE
                        e.employee = '{attendance.get_employee().get_id()}'
                        AND e.payroll_date between '{attendance.get_payroll_start_date()}' and '{attendance.get_date()}'
                        AND e.shift = '{attendance.get_shift().get_name()}'
                        AND e.applied_policy = '{self.applied_policy}'
                        AND e.policy_row = {policy_row}
                        """
            )[0][0]

        return self._recorder[key]
