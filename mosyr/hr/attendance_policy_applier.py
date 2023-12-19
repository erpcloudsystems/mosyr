from .attendance import Attendance
from .shift import ShiftService


class AttendancePoliciesApplier:
    # def apply_policy_on_all_attendances(self):
    #     pass

    @staticmethod
    def apply_policy_on(doc):
        # `doc` is attendance doc
        attendance = Attendance(doc.name, doc.employee, doc.shift,
                                doc.status, doc.attendance_date, doc.in_time,
                                doc.out_time, doc.late_entry, doc.early_exit, doc.working_hours, doc.late_break_duration, doc.break_duration, doc.late_break )

        shift_service = ShiftService()
        shift_service.apply_absent_policy(attendance)
        if doc.status != "Absent":
            shift_service.apply_missing_fingerprint_policy(attendance)
        shift_service.apply_late_arrival_policy(attendance)
        shift_service.apply_early_leave_policy(attendance)
        shift_service.apply_overtime_policy(attendance)
        shift_service.apply_flexible_hours_policy(attendance)
        shift_service.apply_late_break_policy(attendance)
        shift_service.apply_break_overtime_policy(attendance)
        # shift_service.apply_overtime_holidays_policy(attendance)
        

#
# class LateArrivalPolicyApplier(_AttendancePolicyApplier):
#
#     def apply_policy_on(self, doc):
#         if not doc.late_entry:
#             return
#         # doc is attendance doc
#         attendance = Attendance(doc.name, doc.employee, doc.shift,
#                                 doc.status, doc.attendance_date, doc.in_time,
#                                 doc.out_time, doc.late_entry, doc.early_exit)
#         new_doc = frappe.get_doc({
#             "doctype": "Extra Salary",
#             "employee": attendance.get_employee().get_id(),
#             "shift": attendance.get_shift().get_name(),
#             "payroll_date": attendance.get_date(),
#             "amount": attendance.get_shift().get_late_amount(attendance),
#             "salary_component": attendance.get_shift().get_late_salary_component(attendance),
#             "applied_policy": AppliedAttendancePolicy.LATE,
#             "policy_row": attendance.get_shift().get_applied_late_policy_row(attendance)
#         })
#         new_doc.insert()
#
#     # apply policy from given date until today inclusive
#     def apply_policy_on_all_attendances(self):
#         from_date = '1000-01-01'
#         late_attendances = AttendanceService.get_late_arrival_attendances(from_date)
#
#         # this is the list that should be inserted into extra salary table
#         salary_adjustments_list = []
#
#         for late_attendance in late_attendances:
#             attendance = Attendance(**late_attendance)
#
#             keys_to_include = ['employee', 'shift', 'payroll_date']
#             salary_adjustment = get_subset_of_dict(late_attendance, keys_to_include)
#             salary_adjustment['amount'] = attendance.get_shift().get_late_amount(attendance)
#             salary_adjustment['salary_component'] = attendance.get_shift().get_late_salary_component(attendance)
#
#             salary_adjustments_list.append(salary_adjustment)
#
#         frappe.db.insert_many("Extra Salary", salary_adjustments_list)
#
#
# class EarlyLeavePolicyApplier(_AttendancePolicyApplier):
#     def apply_policy_on(self, doc):
#         pass  # todo
#
#     def apply_policy_on_all_attendances(self):
#         from_date = '1000-01-01'
#         early_attendances = AttendanceService.get_early_leave_attendances(from_date)
#         # todo
#
#
# class AbsentPolicyApplier(_AttendancePolicyApplier):
#     def apply_policy_on(self, doc):
#         if not (doc.status == AppliedAttendancePolicy.ABSENT):
#             return
#
#     def apply_policy_on_all_attendances(self):
#         from_date = '1000-01-01'
#         absent_attendances = AttendanceService.get_absent_attendances(from_date)
#         pass  # todo
#
#
# class OvertimePolicyApplier(_AttendancePolicyApplier):
#     def apply_policy_on(self, doc):
#         attendance = Attendance(doc.name, doc.employee, doc.shift,
#                                 doc.status, doc.attendance_date, doc.in_time,
#                                 doc.out_time, doc.late_entry, doc.early_exit)
#
#         if attendance.get_shift().get_overtime_amount(attendance) <= 0:
#             return
#
#         new_doc = frappe.get_doc({
#             "doctype": "Extra Salary",
#             "employee": attendance.get_employee().get_id(),
#             "shift": attendance.get_shift().get_name(),
#             "payroll_date": attendance.get_date(),
#             "applied_policy": AppliedAttendancePolicy.OVERTIME,
#             "amount": attendance.get_shift().get_overtime_amount(attendance),
#             "salary_component": attendance.get_shift().get_overtime_salary_component(attendance),
#             "policy_row": attendance.get_shift().get_policy_row(attendance)
#         })
#         new_doc.insert()
#
#     def apply_policy_on_all_attendances(self):
#         from_date = '1000-01-01'
#         early_attendances = AttendanceService.get_early_leave_attendances(from_date)
#         # todo
