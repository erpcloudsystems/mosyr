from datetime import datetime, timedelta

import frappe

from .attendance_policy.late_arrival_policy import LateArrivalPolicyFactory
from .attendance_policy.early_leave_policy import EarlyLeavePolicyFactory
from .attendance_policy.absent_policy import AbsentPolicyFactory
from .attendance_policy.missing_fingerprint_policy import MissingFingerprintPolicyFactory
from .constans import AppliedAttendancePolicy, DATE_FORMAT
from .factory  import Factory, DAO
from .helpers  import get_dates_different_in_minutes


class ShiftService:
    @staticmethod
    def apply_late_arrival_policy(attendance):
        shift = attendance.get_shift()
        if not shift.is_late_arrival_policy_enabled():
            return
        
        if shift.is_flexible_hours():
            return

        if not attendance.is_late():
            return
        if  attendance.is_missed_fingerprint():
            return
        ShiftService._apply_policy(attendance, shift.get_late_arrival_policy())

    @staticmethod
    def apply_early_leave_policy(attendance):
        shift = attendance.get_shift()
        if not shift.is_early_leave_policy_enabled():
            return
        # if not attendance.is_early():
        #     return

        if shift.is_flexible_hours():
            return
        if not attendance.get_checkout():
            frappe.msgprint(
                f"{attendance.get_employee().get_id()} does not have checkout time on date {attendance.get_date()}")
            return
        if  attendance.is_missed_fingerprint():
            return
        ShiftService._apply_policy(attendance, shift.get_early_leave_policy())

    @staticmethod
    def apply_missing_fingerprint_policy(attendance):
        shift = attendance.get_shift()
        if not shift.is_missing_fingerprint_policy_enabled():
            return
        if not attendance.is_missed_fingerprint():
            return
        
        ShiftService._apply_policy(attendance, shift.get_missing_fingerprint_policy())

    @staticmethod
    def apply_absent_policy(attendance):
        shift = attendance.get_shift()
        if not shift.is_absent_policy_enabled():
            return
        if not attendance.is_absent():
            return
        if shift.is_enable_weekend_policy():
            if attendance.is_weekend():
                apply_weekend_absent_policy(attendance)
                return
            ShiftService._apply_policy(attendance, shift.get_absent_policy())
        if not shift.is_enable_weekend_policy():
            ShiftService._apply_policy(attendance, shift.get_absent_policy())

    @staticmethod
    def apply_overtime_policy(attendance):
        shift = attendance.get_shift()
        if not shift.is_overtime_policy_enabled():
            return

        if not attendance.get_checkout():
            frappe.msgprint(
                f"{attendance.get_employee().get_id()} does not have checkout time on date {attendance.get_date()}")
            return

        if ShiftService.get_overtime_amount(attendance) <= 0:
            return

        new_doc = frappe.get_doc({
            "doctype": "Extra Salary",
            "employee": attendance.get_employee().get_id(),
            "shift": shift.get_name(),
            "payroll_date": attendance.get_date(),
            "applied_policy": AppliedAttendancePolicy.OVERTIME,
            "amount": ShiftService.get_overtime_amount(attendance),
            "salary_component": shift.get_overtime_salary_component(),
            "attendance": attendance.get_name(),
            'minutes_of_late_early_overtime': ShiftService.get_overtime_amount(attendance),
            'company': frappe.get_value('Employee', {'name': attendance.get_employee().get_id()}, 'company')
        })
        new_doc.insert()

    @staticmethod
    def apply_overtime_holidays_policy(attendance):
        shift = attendance.get_shift()
        if not shift.is_holidays_overtime_enabled():
            return

        if not attendance.get_checkout():
            frappe.msgprint(
                f"{attendance.get_employee().get_id()} does not have checkout time on date {attendance.get_date()}")
            return

        if not attendance.check_attendance_in_holidays_list():
            return 

        new_doc = frappe.get_doc({
            "doctype": "Extra Salary",
            "employee": attendance.get_employee().get_id(),
            "shift": shift.get_name(),
            "payroll_date": attendance.get_date(),
            "applied_policy": AppliedAttendancePolicy.OVERTIME,
            "amount":1,
            "salary_component": shift.holidays_overtime_component(),
            "attendance": attendance.get_name(),
            # 'minutes_of_late_early_overtime': ShiftService.get_overtime_amount(attendance),
            'company': frappe.get_value('Employee', {'name': attendance.get_employee().get_id()}, 'company')
        })
        new_doc.insert()

    @staticmethod
    def apply_flexible_hours_policy(attendance):
        shift = attendance.get_shift()
        if not shift.is_flexible_hours():
            return

        if not attendance.get_checkout():
            frappe.msgprint(
                f"{attendance.get_employee().get_id()} does not have checkout time on date {attendance.get_date()}")
            return
        data = get_deduction_flexible_hours(attendance.get_working_hours(), shift)
        if not data:
            return
        new_doc = frappe.get_doc({
            "doctype": "Extra Salary",
            "employee": attendance.get_employee().get_id(),
            "shift": shift.get_name(),
            "payroll_date": attendance.get_date(),
            "applied_policy": AppliedAttendancePolicy.FLEXIBLE_HOURS,
            "amount":data.deduction,
            "salary_component": data.salary_component,
            "attendance": attendance.get_name(),
            # 'minutes_of_late_early_overtime': ShiftService.get_overtime_amount(attendance),
            'company': frappe.get_value('Employee', {'name': attendance.get_employee().get_id()}, 'company')
        })
        new_doc.insert()

    @staticmethod
    def apply_late_break_policy(attendance):
        shift = attendance.get_shift()
        if not shift.is_late_break_policy():
            return
        if not attendance.is_late_break():
            return 
        if not attendance.get_checkout():
            frappe.msgprint(
                f"{attendance.get_employee().get_id()} does not have checkout time on date {attendance.get_date()}")
            return
        data = get_deduction_late_break(attendance.get_working_hours(), shift)
        if not data:
            return
        new_doc = frappe.get_doc({
            "doctype": "Extra Salary",
            "employee": attendance.get_employee().get_id(),
            "shift": shift.get_name(),
            "payroll_date": attendance.get_date(),
            "applied_policy": AppliedAttendancePolicy.LATE_BREAK,
            "amount":data.deduction,
            "salary_component": data.salary_component,
            "attendance": attendance.get_name(),
            # 'minutes_of_late_early_overtime': ShiftService.get_overtime_amount(attendance),
            'company': frappe.get_value('Employee', {'name': attendance.get_employee().get_id()}, 'company')
        })
        new_doc.insert()

    @staticmethod
    def apply_break_overtime_policy(attendance):
        shift = attendance.get_shift()
        if not shift.is_enable_break():
            return
        if not shift.is_enable_overtime_break():
            return
        # if attendance.is_late():
        #     return
        
        if not attendance.get_checkout():
            frappe.msgprint(
                f"{attendance.get_employee().get_id()} does not have checkout time on date {attendance.get_date()}")
            return
        if  attendance.is_late_break():
            return 
        if attendance.get_break_duration() == shift.get_break_duration() :
            return 
        
        new_doc = frappe.get_doc({
            "doctype": "Extra Salary",
            "employee": attendance.get_employee().get_id(),
            "shift": shift.get_name(),
            "payroll_date": attendance.get_date(),
            "applied_policy": AppliedAttendancePolicy.LATE_BREAK,
            "amount":(shift.get_break_duration() - attendance.get_break_duration()) /60 ,
            "salary_component": shift.get_break_overtime_component(),
            "attendance": attendance.get_name(),
            # 'minutes_of_late_early_overtime': shift.get_amount_overtime(),
            'company': frappe.get_value('Employee', {'name': attendance.get_employee().get_id()}, 'company')
        })
        new_doc.insert()

    @staticmethod
    def _apply_policy(attendance, policy):
        shift = attendance.get_shift()

        amounts, salary_components, policy_rows, minutes = policy.apply(attendance)

        for amount, salary_component, policy_row, minutes in zip(amounts, salary_components, policy_rows, minutes):
            new_doc = frappe.get_doc({
                "doctype": "Extra Salary",
                "employee": attendance.get_employee().get_id(),
                "shift": shift.get_name(),
                "payroll_date": attendance.get_date(),
                "amount": amount,
                "salary_component": salary_component,
                "applied_policy": policy.get_name(),
                "policy_row": policy_row,
                "attendance": attendance.get_name(),
                'minutes_of_late_early_overtime': minutes,
                'company': frappe.get_value('Employee', {'name': attendance.get_employee().get_id()}, 'company')
            })
            new_doc.insert(new_doc)

    @staticmethod
    def get_overtime_amount(attendance) -> float:
        shift = attendance.get_shift()
        overtime_in_minutes = get_dates_different_in_minutes(
            datetime.strptime(attendance.get_checkout(), DATE_FORMAT),
            shift.get_shift_end_date(attendance.get_date()))
        if overtime_in_minutes - shift.get_overtime_starts_after() > 0:
            return overtime_in_minutes
        return 0

    # @staticmethod
    # def get_absent_salary_component(attendance):
    #     return attendance.get_shift().get_absent_policy().get_salary_component()

    # @staticmethod
    # def get_absent_amount(attendance):
    #     shift = attendance.get_shift()
    #     return shift.get_absent_policy().get_amount(attendance)


class _Shift:
    def __init__(self, dictionary):
        for key, value in dictionary.items():
            setattr(self, key, value)

    def get_name(self):
        return self._name

    def get_month_start_day(self):
        return self._month_start_day

    def get_month_end_day(self):
        return self._month_end_day

    def get_late_arrival_policy(self):
        return self._late_arrival_policy

    def get_early_leave_policy(self):
        return self._early_leave_policy

    def get_absent_policy(self):
        return self._absent_policy

    def get_overtime_salary_component(self):
        return self._overtime_salary_component

    def get_overtime_starts_after(self):
        return self._overtime_starts_after

    def get_missing_fingerprint_policy(self):
        return self._missing_fingerprint_policy

    def get_shift_start_date(self, date: str) -> datetime:
        return datetime.strptime(f"{date} {self._start_time}", '%Y-%m-%d %H:%M:%S')

    def get_shift_end_date(self, date: str) -> datetime:
        return self.get_shift_start_date(date) + timedelta(
            hours=self.get_length())

    def get_length(self):
        start = self._start_time
        end = self._end_time
        if end >= start:
            return (end - start).total_seconds() / 3600
        return 24 - (start - end).total_seconds() / 3600

    def get_arrival_minutes_after_grace_period(self, attendance):
        shift_start_date: datetime = self.get_shift_start_date(attendance.get_date())
        checkin_date: datetime = datetime.strptime(attendance.get_checkin(), '%Y-%m-%d %H:%M:%S')
        minutes_after_shift_start_time: float = get_dates_different_in_minutes(checkin_date, shift_start_date)
        minutes_after_grace_period: float = minutes_after_shift_start_time - (
            self._late_entry_grace_period if self._enable_entry_grace_period else 0)
        return minutes_after_grace_period

    def get_leave_minutes_before_grace_period(self, attendance):
        minutes_before_shift_end = get_dates_different_in_minutes(self.get_shift_end_date(attendance.get_date()),
                                                                  datetime.strptime(attendance.get_checkout(),
                                                                                    DATE_FORMAT))
        minutes_before_grace_period: float = minutes_before_shift_end - (
            self._early_exit_grace_period if self._enable_exit_grace_period else 0)
        return minutes_before_grace_period

    def get_shift_start_date(self, date: str) -> datetime:
        return datetime.strptime(f"{date} {self._start_time}", '%Y-%m-%d %H:%M:%S')

    def get_shift_end_date(self, date: str) -> datetime:
        return self.get_shift_start_date(date) + timedelta(
            hours=self.get_length())

    def is_late_arrival_policy_enabled(self):
        return self._enable_late_arrival_policy

    def is_early_leave_policy_enabled(self):
        return self._enable_early_leave_policy

    def is_absent_policy_enabled(self):
        return self._enable_absent_policy

    def is_overtime_policy_enabled(self):
        return self._enable_overtime_policy

    def is_missing_fingerprint_policy_enabled(self):
        return self._enable_missing_fingerprint_policy

    def is_holidays_overtime_enabled(self):
        return self._enable_holidays_overtime

    def holidays_overtime_component(self):
        return self._holidays_overtime_component
    def is_flexible_hours(self):
        return self._is_flexible_hours
    def is_late_break_policy(self):
        return self._is_enable_break_policy
    def is_enable_weekend_policy(self):
        return self._enable_weekend_policy
    def get_weekend_absent(self):
        return self._weekend_absent
    def get_weekend_absent_component(self):
        return self._weekend_absent_component

    def is_enable_overtime_break(self):
        return self._is_enable_overtime_break
    
    def is_enable_break(self):
        return self._is_enable_break
    def get_amount_overtime(self):
        return self._amount_overtime
    def get_break_overtime_component(self):
        return self._break_overtime_component

    def get_break_duration(self):
        return self._break_duration

class _ShiftDao(DAO):
    @staticmethod
    def create(name: str) -> _Shift:
        shift_dict = {'_late_arrival_policy': LateArrivalPolicyFactory.create(name),
                      '_early_leave_policy': EarlyLeavePolicyFactory.create(name),
                      '_absent_policy': AbsentPolicyFactory.create(name),
                      '_missing_fingerprint_policy': MissingFingerprintPolicyFactory.create(name)}
        for key, value in _ShiftDao._get_shift_properties_from_db(name).items():
            shift_dict[f"_{key}"] = value

        return _Shift(shift_dict)

    @staticmethod
    def _get_shift_properties_from_db(shift_name):
        return frappe.db.sql(f"""
                                SELECT
                                    name,
                                    start_time,
                                    end_time, 
                                    month_start_in AS month_start_day,
                                    month_end_in AS month_end_day,
                                    enable_entry_grace_period, 
                                    late_entry_grace_period,
                                    enable_exit_grace_period,   
                                    early_exit_grace_period,
                                    last_sync_of_checkin,
                                    overtime_starts_after,
                                    overtime AS overtime_salary_component,
                                    enable_early_leave_policy,
                                    enable_late_arrival_policy,
                                    enable_absent_policy,
                                    enable_overtime_policy,
                                    enable_missing_fingerprint_policy,
                                    enable_holidays_overtime as enable_holidays_overtime, 
                                    holidays_overtime_component as holidays_overtime_component,
                                    is_flexible_hours as is_flexible_hours,
                                    enable_weekend_policy as enable_weekend_policy,
                                    weekend_absent  as weekend_absent,
                                    weekend_absent_component as weekend_absent_component,
                                    enable_break_policy as is_enable_break_policy,
                                    overtime_break as  is_enable_overtime_break,
                                    enable_break as is_enable_break,
                                    break_overtime_component as   break_overtime_component,
                                    amount_overtime	 as   amount_overtime,
                                    break_duration as 	break_duration
                                FROM `tabShift Type`
                                WHERE name = '{shift_name}'
                            """, as_dict=1)[0]


class ShiftFactory(Factory):
    _store = {}
    _shiftDao = _ShiftDao()

    @staticmethod
    def create(shift_name: str):
        if shift_name in ShiftFactory._store:
            return ShiftFactory._store[shift_name]
        else:
            ShiftFactory._store[shift_name] = ShiftFactory._shiftDao.create(shift_name)
            return ShiftFactory._store[shift_name]


def get_deduction_flexible_hours(working_hours, shift):
    shift_doc = frappe.get_doc("Shift Type" , shift.get_name())

    filtered_shifts =   next(
    (x for x in shift_doc.flexible_hours_policy if x.hours >= float(working_hours)),
        None
    )

    return filtered_shifts

def get_deduction_late_break(late_duration, shift):
    shift_doc = frappe.get_doc("Shift Type" , shift.get_name())

    filtered_shifts =   next(
    (x for x in shift_doc.late_break_policy if (int(x.minutes * 60)) >= float(late_duration)),
        None
    )

    return filtered_shifts

def apply_weekend_absent_policy(attendance):
    shift = attendance.get_shift()
    new_doc = frappe.get_doc({
        "doctype": "Extra Salary",
        "employee": attendance.get_employee().get_id(),
        "shift": shift.get_name(),
        "payroll_date": attendance.get_date(),
        "applied_policy": AppliedAttendancePolicy.WEEKEND_ABSENT,
        "amount":shift.get_weekend_absent(),
        "salary_component": shift.get_weekend_absent_component(),
        "attendance": attendance.get_name(),
        # 'minutes_of_late_early_overtime': ShiftService.get_overtime_amount(attendance),
        'company': frappe.get_value('Employee', {'name': attendance.get_employee().get_id()}, 'company')
    })
    new_doc.insert()
    return True