import itertools
from datetime import datetime, timedelta

import frappe
from frappe import _
from frappe.query_builder import Criterion
from frappe.utils import (
	get_datetime,
	get_link_to_form,
	get_time,
	getdate,
	cint,
	flt,
)

from erpnext.hr.utils import validate_active_employee
from erpnext.hr.doctype.holiday_list.holiday_list import is_holiday
from erpnext.hr.doctype.employee.employee import get_holiday_list_for_employee
from erpnext.buying.doctype.supplier_scorecard.supplier_scorecard import daterange

############################################
############## Shift Overrides ############
############################################

from mosyr.overrides import (
	has_overlapping_timings,
	mark_attendance_and_link_log,
	get_overlapping_shift_attendance,
	get_duplicate_attendance_record,
	calculate_working_hours,
	get_employee_shift,
	mark_attendance,
	get_shift_details,
	get_actual_start_end_datetime_of_shift,
)

from erpnext.hr.doctype.shift_assignment.shift_assignment import ShiftAssignment
from erpnext.hr.doctype.shift_request.shift_request import ShiftRequest
from erpnext.hr.doctype.attendance.attendance import Attendance
from erpnext.hr.doctype.employee_checkin.employee_checkin import EmployeeCheckin
from erpnext.hr.doctype.shift_type.shift_type import ShiftType

############################################
############## Validation Error ############
############################################
class OverlappingShiftError(frappe.ValidationError):
	pass


class OverlappingShiftRequestError(frappe.ValidationError):
	pass


class DuplicateAttendanceError(frappe.ValidationError):
	pass


class OverlappingShiftAttendanceError(frappe.ValidationError):
	pass


############################################
############## Shift Assignment ############
############################################
class CustomShiftAssignment(ShiftAssignment):
	def validate(self):
		validate_active_employee(self.employee)
		self.validate_overlapping_shifts()

		if self.end_date:
			self.validate_from_to_dates("start_date", "end_date")

	def validate_overlapping_shifts(self):
		overlapping_dates = self.get_overlapping_dates()
		if len(overlapping_dates):
			# if dates are overlapping, check if timings are overlapping, else allow
			overlapping_timings = has_overlapping_timings(
				self.shift_type, overlapping_dates[0].shift_type
			)
			if overlapping_timings:
				self.throw_overlap_error(overlapping_dates[0])

	def get_overlapping_dates(self):
		if not self.name:
			self.name = "New Shift Assignment"

		shift = frappe.qb.DocType("Shift Assignment")
		query = (
			frappe.qb.from_(shift)
			.select(shift.name, shift.shift_type, shift.docstatus, shift.status)
			.where(
				(shift.employee == self.employee)
				& (shift.docstatus == 1)
				& (shift.name != self.name)
				& (shift.status == "Active")
			)
		)

		if self.end_date:
			query = query.where(
				Criterion.any(
					[
						Criterion.any(
							[
								shift.end_date.isnull(),
								(
									(self.start_date >= shift.start_date)
									& (self.start_date <= shift.end_date)
								),
							]
						),
						Criterion.any(
							[
								(
									(self.end_date >= shift.start_date)
									& (self.end_date <= shift.end_date)
								),
								shift.start_date.between(
									self.start_date, self.end_date
								),
							]
						),
					]
				)
			)
		else:
			query = query.where(
				shift.end_date.isnull()
				| (
					(self.start_date >= shift.start_date)
					& (self.start_date <= shift.end_date)
				)
			)

		return query.run(as_dict=True)

	def throw_overlap_error(self, shift_details):
		shift_details = frappe._dict(shift_details)
		if shift_details.docstatus == 1 and shift_details.status == "Active":
			msg = _(
				"Employee {0} already has an active Shift {1}: {2} that overlaps within this period."
			).format(
				frappe.bold(self.employee),
				frappe.bold(shift_details.shift_type),
				get_link_to_form("Shift Assignment", shift_details.name),
			)
			frappe.throw(msg, title=_("Overlapping Shifts"), exc=OverlappingShiftError)


############################################
############## Shift Request ############
############################################


class CustomShiftRequest(ShiftRequest):
	def validate(self):
		validate_active_employee(self.employee)
		self.validate_dates()
		self.validate_overlapping_shift_requests()
		self.validate_approver()
		self.validate_default_shift()

	def validate_overlapping_shift_requests(self):
		overlapping_dates = self.get_overlapping_dates()
		if len(overlapping_dates):
			# if dates are overlapping, check if timings are overlapping, else allow
			overlapping_timings = has_overlapping_timings(
				self.shift_type, overlapping_dates[0].shift_type
			)
			if overlapping_timings:
				self.throw_overlap_error(overlapping_dates[0])

	def get_overlapping_dates(self):
		if not self.name:
			self.name = "New Shift Request"

		shift = frappe.qb.DocType("Shift Request")
		query = (
			frappe.qb.from_(shift)
			.select(shift.name, shift.shift_type)
			.where(
				(shift.employee == self.employee)
				& (shift.docstatus < 2)
				& (shift.name != self.name)
			)
		)

		if self.to_date:
			query = query.where(
				Criterion.any(
					[
						Criterion.any(
							[
								shift.to_date.isnull(),
								(
									(self.from_date >= shift.from_date)
									& (self.from_date <= shift.to_date)
								),
							]
						),
						Criterion.any(
							[
								(
									(self.to_date >= shift.from_date)
									& (self.to_date <= shift.to_date)
								),
								shift.from_date.between(self.from_date, self.to_date),
							]
						),
					]
				)
			)
		else:
			query = query.where(
				shift.to_date.isnull()
				| (
					(self.from_date >= shift.from_date)
					& (self.from_date <= shift.to_date)
				)
			)

		return query.run(as_dict=True)

	def throw_overlap_error(self, shift_details):
		shift_details = frappe._dict(shift_details)
		msg = _(
			"Employee {0} has already applied for Shift {1}: {2} that overlaps within this period"
		).format(
			frappe.bold(self.employee),
			frappe.bold(shift_details.shift_type),
			get_link_to_form("Shift Request", shift_details.name),
		)

		frappe.throw(
			msg, title=_("Overlapping Shift Requests"), exc=OverlappingShiftRequestError
		)


############################################
################ Attendance ################
############################################


class CustomAttendance(Attendance):
	def validate(self):
		from erpnext.controllers.status_updater import validate_status

		validate_status(
			self.status, ["Present", "Absent", "On Leave", "Half Day", "Work From Home"]
		)
		validate_active_employee(self.employee)
		self.validate_attendance_date()
		self.validate_duplicate_record()
		self.validate_overlapping_shift_attendance()
		self.validate_employee_status()
		self.check_leave_record()

	def validate_duplicate_record(self):
		duplicate = get_duplicate_attendance_record(
			self.employee, self.attendance_date, self.shift, self.name
		)

		if duplicate:
			frappe.throw(
				_(
					"Attendance for employee {0} is already marked for the date {1}: {2}"
				).format(
					frappe.bold(self.employee),
					frappe.bold(self.attendance_date),
					get_link_to_form("Attendance", duplicate[0].name),
				),
				title=_("Duplicate Attendance"),
				exc=DuplicateAttendanceError,
			)

	def validate_overlapping_shift_attendance(self):
		attendance = get_overlapping_shift_attendance(
			self.employee, self.attendance_date, self.shift, self.name
		)

		if attendance:
			frappe.throw(
				_(
					"Attendance for employee {0} is already marked for an overlapping shift {1}: {2}"
				).format(
					frappe.bold(self.employee),
					frappe.bold(attendance.shift),
					get_link_to_form("Attendance", attendance.name),
				),
				title=_("Overlapping Shift Attendance"),
				exc=OverlappingShiftAttendanceError,
			)


############################################
############## Employee Checkin ############
############################################
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

def get_dates_different_in_minutes(date1: datetime, date2: datetime) -> float:
	return (date1 - date2).total_seconds() / 60
def get_date(date_time):
		if type(date_time) == datetime:
			date_time = date_time.strftime(DATE_FORMAT)
		return date_time
def _handle_multiple_same_checks(date1, date2):
		if get_date(date1) is None or get_date(date2) is None:
			return
		
		checkin_date = datetime.strptime(get_date(date1), DATE_FORMAT)
		checkout_date = datetime.strptime(get_date(date2), DATE_FORMAT)
		minutes = (get_dates_different_in_minutes(checkout_date, checkin_date))
		return minutes
class CustomEmployeeCheckin(EmployeeCheckin):
	def validate(self):
		validate_active_employee(self.employee)
		self.validate_duplicate_log()
		self.fetch_shift()
		
	def fetch_shift(self):
		shift_actual_timings = get_actual_start_end_datetime_of_shift(
			self.employee, get_datetime(self.time), True
		)
		# frappe.throw(f"{shift_actual_timings}")
		if shift_actual_timings:
			if (
				shift_actual_timings.shift_type.determine_check_in_and_check_out
				== "Strictly based on Log Type in Employee Checkin"
				and not self.log_type
				and not self.skip_auto_attendance
			):
				frappe.throw(
					_(
						"Log Type is required for check-ins falling in the shift: {0}."
					).format(shift_actual_timings.shift_type.name)
				)
			if not self.attendance:
				self.shift = shift_actual_timings.shift_type.name
				self.shift_actual_start = shift_actual_timings.actual_start
				self.shift_actual_end = shift_actual_timings.actual_end
				self.shift_start = shift_actual_timings.start_datetime
				self.shift_end = shift_actual_timings.end_datetime
		else:
			self.shift = None


############################################
################## Shift Type ##############
############################################
class CustomShiftType(ShiftType):
	def get_attendance(self, logs):
		"""Return attendance_status, working_hours, late_entry, early_exit, in_time, out_time
		for a set of logs belonging to a single shift.
		Assumptions:
		1. These logs belongs to a single shift, single employee and it's not in a holiday date.
		2. Logs are in chronological order
		"""
		late_entry = early_exit = False
		total_working_hours, in_time, out_time = calculate_working_hours(
			logs,
			self.determine_check_in_and_check_out,
			self.working_hours_calculation_based_on,
			flt(self.max_working_hours)
		)
		if (
			cint(self.enable_entry_grace_period)
			and in_time
			and in_time
			> logs[0].shift_start
			+ timedelta(minutes=cint(self.late_entry_grace_period))
		):
			late_entry = True

		if (
			cint(self.enable_exit_grace_period)
			and out_time
			and out_time
			< logs[0].shift_end - timedelta(minutes=cint(self.early_exit_grace_period))
		):
			early_exit = True

		if (
			self.working_hours_threshold_for_half_day
			and total_working_hours < self.working_hours_threshold_for_half_day
		):
			return (
				"Half Day",
				total_working_hours,
				late_entry,
				early_exit,
				in_time,
				out_time,
			)
		if (
			self.working_hours_threshold_for_absent
			and total_working_hours < self.working_hours_threshold_for_absent
		):
			return (
				"Absent",
				total_working_hours,
				late_entry,
				early_exit,
				in_time,
				out_time,
			)
		return "Present", total_working_hours, late_entry, early_exit, in_time, out_time

	def mark_absent_for_dates_with_no_attendance(self, employee):
		"""Marks Absents for the given employee on working days in this shift which have no attendance marked.
		The Absent is marked starting from 'process_attendance_after' or employee creation date.
		"""
		start_date, end_date = self.get_start_and_end_dates(employee)

		# no shift assignment found, no need to process absent attendance records
		
		if start_date is None:
			return

		holiday_list_name = self.holiday_list
		if not holiday_list_name:
			holiday_list_name = get_holiday_list_for_employee(employee, False)

		start_time = get_time(self.start_time)
		
		for date in daterange(getdate(start_date), getdate(end_date)):
			if is_holiday(holiday_list_name, date):
				# skip marking absent on a holiday
				continue

			timestamp = datetime.combine(date, start_time)
			shift_details = get_employee_shift(employee, timestamp, True)

			if shift_details and shift_details.shift_type.name == self.name:
				mark_attendance(employee, date, "Absent", self.name)

	@frappe.whitelist()
	def process_auto_attendance_v2(self):
		self.process_auto_attendance()

	@frappe.whitelist()
	def process_auto_attendance(self):
		if (
			not cint(self.enable_auto_attendance)
			or not self.process_attendance_after
			or not self.last_sync_of_checkin
		):
			return

		filters = {
			"skip_auto_attendance": 0,
			"attendance": ("is", "not set"),
			"time": (">=", self.process_attendance_after),
			"shift_actual_end": ("<", self.last_sync_of_checkin),
			"shift": self.name,
		}
		logs = frappe.db.get_list(
			"Employee Checkin", fields="*", filters=filters, order_by="employee,time"
		)

		for key, group in itertools.groupby(
			logs, key=lambda x: (x["employee"], x["shift_actual_start"])
		):
			single_shift_logs = list(group)
			(
				attendance_status,
				working_hours,
				late_entry,
				early_exit,
				in_time,
				out_time,
			) = self.get_attendance(single_shift_logs)

			mark_attendance_and_link_log(
				single_shift_logs,
				attendance_status,
				key[1].date(),
				working_hours,
				late_entry,
				early_exit,
				in_time,
				out_time,
				self.name,
			)

		for employee in self.get_assigned_employees(self.process_attendance_after, True):
			
			self.mark_absent_for_dates_with_no_attendance(employee)

	def get_start_and_end_dates(self, employee):
		"""Returns start and end dates for checking attendance and marking absent
		return: start date = max of `process_attendance_after` and DOJ
		return: end date = min of shift before `last_sync_of_checkin` and Relieving Date
		"""
		date_of_joining, relieving_date, employee_creation = frappe.db.get_value(
			"Employee", employee, ["date_of_joining", "relieving_date", "creation"]
		)

		if not date_of_joining:
			date_of_joining = employee_creation.date()

		start_date = max(getdate(self.process_attendance_after), date_of_joining)
		end_date = None

		shift_details = get_shift_details(
			self.name, get_datetime(self.last_sync_of_checkin)
		)
		last_shift_time = (
			shift_details.actual_start
			if shift_details
			else get_datetime(self.last_sync_of_checkin)
		)

		# check if shift is found for 1 day before the last sync of checkin
		# absentees are auto-marked 1 day after the shift to wait for any manual attendance records
		prev_shift = get_employee_shift(
			employee, last_shift_time - timedelta(days=1), True, "reverse"
		)
		if prev_shift:
			end_date = (
				min(prev_shift.start_datetime.date(), relieving_date)
				if relieving_date
				else prev_shift.start_datetime.date()
			)
		else:
			# no shift found
			return None, None
		return start_date, end_date

	def get_assigned_employees(self, from_date=None, consider_default_shift=False):
		filters = {"shift_type": self.name, "docstatus": "1", "status": "Active"}
		if from_date:
			filters["start_date"] = (">=", from_date)

		assigned_employees = frappe.get_all("Shift Assignment", filters=filters, pluck="employee")

		if consider_default_shift:
			default_shift_employees = self.get_employees_with_default_shift(filters)
			assigned_employees = set(assigned_employees + default_shift_employees)

		# exclude inactive employees
		inactive_employees = frappe.db.get_all("Employee", {"status": "Inactive"}, pluck="name")

		return set(assigned_employees) - set(inactive_employees)
	
	def get_employees_with_default_shift(self, filters: dict) -> list:
		default_shift_employees = frappe.get_all(
			"Employee", filters={"default_shift": self.name, "status": "Active"}, pluck="name"
		)

		if not default_shift_employees:
			return []

		# exclude employees from default shift list if any other valid shift assignment exists
		del filters["shift_type"]
		filters["employee"] = ("in", default_shift_employees)

		active_shift_assignments = frappe.get_all(
			"Shift Assignment",
			filters=filters,
			pluck="employee",
		)

		return list(set(default_shift_employees) - set(active_shift_assignments))