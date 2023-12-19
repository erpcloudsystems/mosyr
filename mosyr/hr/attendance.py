from .employee import Employee
from .shift import ShiftFactory
import frappe

from datetime import datetime, timedelta, date

from .constans import AppliedAttendancePolicy, AttendanceStatus

from .helpers import get_dates_different_in_minutes
from .constans import DATE_FORMAT


class AttendanceService:
    @staticmethod
    def _get_subquery(self, applied_policy: str) -> str:
        return f"""
                    SELECT
                        employee
                    FROM
                        `tabSalary Adjustments`
                    WHERE
                        `tabSalary Adjustments`.employee                = tabAttendance.employee
                        and `tabSalary Adjustments`.payroll_date        = tabAttendance.attendance_date
                        and `tabSalary Adjustments`.applied_policy      = '{applied_policy}'
                        and `tabSalary Adjustments`.shift               = tabAttendance.shift
                """

    # additional_conditions must start with AND
    # example: "AND tabAttendance.status = 'Present'"
    @staticmethod
    def _get_attendance(from_date: str, status: str, applied_policy: str, additional_conditions: str = "") -> list[
        dict]:
        return frappe.db.sql(f"""
                                   SELECT a.name AS name,
                                          a.attendance_date,
                                          a.employee AS employee,
                                          a.shift AS shift,
                                          a.status AS status,
                                          a.in_time AS checkin,
                                          a.out_time AS checkout,
                                          a.is_late AS is_late,
                                          a.is_early AS is_early
                                   FROM tabAttendance AS a
                                   WHERE a.attendance_date >= '{from_date}'
                                   AND tabAttendance.status = '{status}'
                                   {additional_conditions}
                                   AND tabAttendance.employee NOT EXISTS ({AttendanceService._get_subquery(applied_policy)}) -- is this condition efficient?
                                   ORDER BY tabAttendance.attendance_date ASC 
                                   """, as_dict=1)

    @staticmethod
    def get_late_arrival_attendances(from_date: str) -> list[dict]:
        additional_conditions = "AND tabAttendance.late_entry = 1"
        return AttendanceService._get_attendance(from_date, AttendanceStatus.PRESENT, AppliedAttendancePolicy.LATE,
                                                 additional_conditions)

    @staticmethod
    def get_early_leave_attendances(from_date: str) -> list[dict]:
        additional_conditions = "AND tabAttendance.early_entry = 1"
        return AttendanceService._get_attendance(from_date, AttendanceStatus.PRESENT, AppliedAttendancePolicy.EARLY,
                                                 additional_conditions)

    @staticmethod
    def get_overtime_attendances(from_date: str) -> list[dict]:
        return AttendanceService._get_attendance(from_date, AttendanceStatus.PRESENT, AppliedAttendancePolicy.OVERTIME)

    @staticmethod
    def get_absent_attendances(from_date: str) -> list[dict]:
        return AttendanceService._get_attendance(from_date, AttendanceStatus.ABSENT, AppliedAttendancePolicy.ABSENT)


class Attendance:
    def __init__(self, name, employee: str, shift: str, status, attendance_date: str,
                 checkin: datetime, checkout: datetime, is_late, is_early, working_hours, late_break_duration, break_duration,  late_break):
        self._name = name
        self._date = attendance_date
        self._employee = Employee(employee)
        if not shift:
            shift = frappe.get_value("Employee", filters={"name": employee}, fieldname="default_shift")
        self._shift = ShiftFactory.create(shift)
        self._status = status
        self._checkin = checkin
        self._checkout = checkout
        self._is_late = is_late
        self._is_early = is_early
        self._working_hours = working_hours
        self._late_break_duration = late_break_duration
        self._break_duration = break_duration
        self._late_break =  late_break

        self._handle_multiple_same_checks()

    def _handle_multiple_same_checks(self):
        if self.get_checkin() is None or self.get_checkout() is None:
            return

        checkin_date = datetime.strptime(self.get_checkin(), DATE_FORMAT)
        checkout_date = datetime.strptime(self.get_checkout(), DATE_FORMAT)

        minutes = get_dates_different_in_minutes(checkout_date, checkin_date)

        if minutes > 10:
            return

        if get_dates_different_in_minutes(
                checkin_date,
                self.get_shift().get_shift_start_date(self.get_date())) <= get_dates_different_in_minutes(
            self.get_shift().get_shift_end_date(self.get_date()), checkin_date):
            self._checkout = None
        else:
            self._checkin = None

    def get_name(self):
        return self._name

    def get_shift(self):
        return self._shift

    def get_employee(self):
        return self._employee

    def get_date(self) -> str:
        if type(self._date) == datetime:
            self._date = self._date.strftime(DATE_FORMAT)
        if type(self._date) == date:
            self._date = self._date.strftime(DATE_FORMAT.split(" ")[0])
        return self._date

    def get_checkin(self):
        if type(self._checkin) == datetime:
            self._checkin = self._checkin.strftime(DATE_FORMAT)
        return self._checkin

    def get_checkout(self):
        # frappe.msgprint(
        #     f"checkout:  {type(self._checkout)}, {self._checkout}, {self.get_date()}, {self.get_employee().get_id()}")

        if type(self._checkout) == datetime:
            self._checkout = self._checkout.strftime(DATE_FORMAT)
        return self._checkout

    def get_status(self):
        return self._status

    def get_payroll_start_date(self):
        """
        if payroll start from 26 to 25 of the next month
        and we are on 2023-05-07 then the payroll_start_date is 2023-04-26
        if we are on 2023-04-28 then the payroll_start_date is also 2023-04-26
        if we are on 2023-05-25 then the payroll_start_date is also 2023-04-26

        :return: str

        """
        attendance_date = datetime.strptime(self.get_date(), "%Y-%m-%d")
        shift_start_day: str = self.get_shift().get_month_start_day()
        shift_start_day = int(shift_start_day)
        if attendance_date.day >= shift_start_day:
            payroll_start_date = attendance_date.replace(day=shift_start_day)
            return payroll_start_date.strftime('%Y-%m-%d')
        else:
            last_day_prev_month = attendance_date.replace(day=1) - timedelta(days=1)
            payroll_start_date = last_day_prev_month.replace(day=shift_start_day)
            return payroll_start_date.strftime('%Y-%m-%d')

    def is_late(self):
        return self._is_late

    def is_early(self):
        return self._is_early

    def is_absent(self):
        return self.get_status() == AttendanceStatus.ABSENT

    def is_missed_fingerprint(self):
        return self.get_checkin() is None or self.get_checkout() is None
    
    def check_attendance_in_holidays_list(self):
        employe = frappe.get_doc("Employee", self.get_employee())
        query = frappe.db.sql(
            f"""
                SELECT `tabHoliday`.holiday_date from `tabHoliday List` JOIN `tabHoliday` ON `tabHoliday`.parent = `tabHoliday List`.name where `tabHoliday List`.name = '{employe.holiday_list}' and `tabHoliday`.holiday_date = '{ self.get_date()}' 
            """
        )

        if query:

            return True
        return False
    def get_working_hours(self):
        return self._working_hours

    def is_weekend(self):
        # Convert the input string to a datetime object
        date_object = datetime.strptime(self.get_date(), '%Y-%m-%d')

        # Get the day of the week (0 = Monday, 1 = Tuesday, ..., 6 = Sunday)
        day_of_week = date_object.weekday()

        # Check if the day is a weekend day (Saturday or Sunday)
        return day_of_week == 3 or day_of_week == 6

    def get_late_break_duration(self):
        return self._late_break_duration
    
    def get_break_duration(self):
        return self._break_duration

    def is_late_break(self):
        return self._late_break