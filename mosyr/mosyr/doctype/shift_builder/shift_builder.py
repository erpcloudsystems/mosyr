# Copyright (c) 2023, AnvilERP and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import (
    time_diff_in_seconds,
    cint,
    nowdate,
    now_datetime,
    flt,
)
from frappe.model.naming import make_autoname


class ShiftBuilder(Document):
    def validate(self):
        self.validate_employees()
        if self.shift_type == "Double Shift Work Schedule":
            self.validate_double_shifts()
        elif self.shift_type == "Work Schedule with Different Times":
            self.validate_different_times_shifts()
        elif self.shift_type == "Flexible Work Schedule":
            self.validate_flexible_shifts_times()
        else:
            frappe.throw(_(f"Shift Type {self.shift_type} is not supported"))

    def validate_double_shifts(self):
        # Cehck Workgin Days
        work_days = [
            "sunday_two_shift",
            "monday_two_shift",
            "tuesday_two_shift",
            "wednesday_two_shift",
            "thursday_two_shift",
            "friday_two_shift",
            "saturday_two_shift",
        ]
        has_any_day = False
        for day in work_days:
            if self.get(day):
                has_any_day = True
        if not has_any_day:
            frappe.throw(_("At Least One Working Day is Required"))

        # Check data for two shifts
        times_fields = [
            "first_period_start_time",
            "first_period_end_time",
            "second_period_start_time",
            "second_period_end_time",
        ]
        for field in times_fields:
            if not self.get(field):
                field = field.replace("_", " ")
                frappe.throw(_(f"in Double Shift {field} is Required"))

        # Check if valid times
        if (
            time_diff_in_seconds(
                self.first_period_end_time, self.first_period_start_time
            )
            < 0
        ):
            frappe.throw(
                _(
                    f"First Period Start Time cannot be greater than First Period End Time"
                )
            )
        if (
            time_diff_in_seconds(
                self.second_period_end_time, self.second_period_start_time
            )
            < 0
        ):
            frappe.throw(
                _(
                    f"Second Period Start Time cannot be greater than Second Period End Time"
                )
            )
        is_valid_interval = self.valid_interval_times(
            self.first_period_start_time,
            self.first_period_end_time,
            self.second_period_start_time,
            self.second_period_end_time,
        )
        if not is_valid_interval:
            frappe.throw(_("Shift 1 and Shift 2 are overlapping."))

    def validate_different_times_shifts(self):
        # Cehck Workgin Days
        work_days = [
            "sunday_different_times",
            "monday_different_times",
            "tuesday_different_times",
            "wednesday_different_times",
            "thursday_different_times",
            "friday_different_times",
            "saturday_different_times",
        ]
        has_any_day = False
        for day in work_days:
            if self.get(day) == 1:
                has_any_day = True
        if not has_any_day:
            frappe.throw(_("Select Working Day is mandatory"))

        # Check data for each shift day, at least one shift is required, no overlapping if two shifts are selected
        if self.sunday_different_times:
            if (
                not self.sunday_exit_the_first_period
                or not self.sunday_entering_the_first_period
                or not self.sunday_exit_the_second_period
                or not self.sunday_entering_the_second_period
            ):
                frappe.throw(
                    _(f"In Sunday Shift, Set Entering and Exiting Time for Shifts")
                )
            if (
                time_diff_in_seconds(
                    self.sunday_exit_the_first_period,
                    self.sunday_entering_the_first_period,
                )
                < 0
            ):
                frappe.throw(
                    _(
                        f"In Sunday Shift, Entering Time cannot be greater than Exiting Time"
                    )
                )
            if (
                time_diff_in_seconds(
                    self.sunday_exit_the_second_period,
                    self.sunday_entering_the_second_period,
                )
                < 0
            ):
                frappe.throw(
                    _(
                        f"In Sunday Shift, Entering Time cannot be greater than Exiting Time"
                    )
                )
            is_valid_interval = self.valid_interval_times(
                self.sunday_entering_the_first_period,
                self.sunday_exit_the_first_period,
                self.sunday_entering_the_second_period,
                self.sunday_exit_the_second_period,
            )
            if not is_valid_interval:
                frappe.throw(_("Shift 1 and Shift 2 are overlapping in Sunday Shift"))
        if self.monday_different_times:
            if (
                not self.monday_exit_the_first_period
                or not self.monday_entering_the_first_period
                or not self.monday_exit_the_second_period
                or not self.monday_entering_the_second_period
            ):
                frappe.throw(
                    _(f"In Monday Shift, Set Entering and Exiting Time for Shifts")
                )
            if (
                time_diff_in_seconds(
                    self.monday_exit_the_first_period,
                    self.monday_entering_the_first_period,
                )
                < 0
            ):
                frappe.throw(
                    _(
                        f"In Monday Shift, Entering Time cannot be greater than Exiting Time"
                    )
                )
            if (
                time_diff_in_seconds(
                    self.monday_exit_the_second_period,
                    self.monday_entering_the_second_period,
                )
                < 0
            ):
                frappe.throw(
                    _(
                        f"In Monday Shift, Entering Time cannot be greater than Exiting Time"
                    )
                )
            is_valid_interval = self.valid_interval_times(
                self.monday_entering_the_first_period,
                self.monday_exit_the_first_period,
                self.monday_entering_the_second_period,
                self.monday_exit_the_second_period,
            )
            if not is_valid_interval:
                frappe.throw(_("Shift 1 and Shift 2 are overlapping in Monday Shift"))
        if self.tuesday_different_times:
            if (
                not self.tuesday_exit_the_first_period
                or not self.tuesday_entering_the_first_period
                or not self.tuesday_exit_the_second_period
                or not self.tuesday_entering_the_second_period
            ):
                frappe.throw(
                    _(f"In Tuesday Shift, Set Entering and Exiting Time for Shifts")
                )
            if (
                time_diff_in_seconds(
                    self.tuesday_exit_the_first_period,
                    self.tuesday_entering_the_first_period,
                )
                < 0
            ):
                frappe.throw(
                    _(
                        f"In Tuesday Shift, Entering Time cannot be greater than Exiting Time"
                    )
                )
            if (
                time_diff_in_seconds(
                    self.tuesday_exit_the_second_period,
                    self.tuesday_entering_the_second_period,
                )
                < 0
            ):
                frappe.throw(
                    _(
                        f"In Tuesday Shift, Entering Time cannot be greater than Exiting Time"
                    )
                )
            is_valid_interval = self.valid_interval_times(
                self.tuesday_entering_the_first_period,
                self.tuesday_exit_the_first_period,
                self.tuesday_entering_the_second_period,
                self.tuesday_exit_the_second_period,
            )
            if not is_valid_interval:
                frappe.throw(_("Shift 1 and Shift 2 are overlapping in Tuesday Shift"))
        if self.wednesday_different_times:
            if (
                not self.wednesday_exit_the_first_period
                or not self.wednesday_entering_the_first_period
                or not self.wednesday_exit_the_second_period
                or not self.wednesday_entering_the_second_period
            ):
                frappe.throw(
                    _(f"In Wednesday Shift, Set Entering and Exiting Time for Shifts")
                )
            if (
                time_diff_in_seconds(
                    self.wednesday_exit_the_first_period,
                    self.wednesday_entering_the_first_period,
                )
                < 0
            ):
                frappe.throw(
                    _(
                        f"In Wednesday Shift, Entering Time cannot be greater than Exiting Time"
                    )
                )
            if (
                time_diff_in_seconds(
                    self.wednesday_exit_the_second_period,
                    self.wednesday_entering_the_second_period,
                )
                < 0
            ):
                frappe.throw(
                    _(
                        f"In Wednesday Shift, Entering Time cannot be greater than Exiting Time"
                    )
                )
            is_valid_interval = self.valid_interval_times(
                self.wednesday_entering_the_first_period,
                self.wednesday_exit_the_first_period,
                self.wednesday_entering_the_second_period,
                self.wednesday_exit_the_second_period,
            )
            if not is_valid_interval:
                frappe.throw(
                    _("Shift 1 and Shift 2 are overlapping in Wednesday Shift")
                )
        if self.thursday_different_times:
            if (
                not self.thursday_exit_the_first_period
                or not self.thursday_entering_the_first_period
                or not self.thursday_exit_the_second_period
                or not self.thursday_entering_the_second_period
            ):
                frappe.throw(
                    _(f"In Thursday Shift, Set Entering and Exiting Time for Shifts")
                )
            if (
                time_diff_in_seconds(
                    self.thursday_exit_the_first_period,
                    self.thursday_entering_the_first_period,
                )
                < 0
            ):
                frappe.throw(
                    _(
                        f"In Thursday Shift, Entering Time cannot be greater than Exiting Time"
                    )
                )
            if (
                time_diff_in_seconds(
                    self.thursday_exit_the_second_period,
                    self.thursday_entering_the_second_period,
                )
                < 0
            ):
                frappe.throw(
                    _(
                        f"In Thursday Shift, Entering Time cannot be greater than Exiting Time"
                    )
                )
            is_valid_interval = self.valid_interval_times(
                self.thursday_entering_the_first_period,
                self.thursday_exit_the_first_period,
                self.thursday_entering_the_second_period,
                self.thursday_exit_the_second_period,
            )
            if not is_valid_interval:
                frappe.throw(_("Shift 1 and Shift 2 are overlapping in Thursday Shift"))
        if self.friday_different_times:
            if (
                not self.friday_exit_the_first_period
                or not self.friday_entering_the_first_period
                or not self.friday_exit_the_second_period
                or not self.friday_entering_the_second_period
            ):
                frappe.throw(
                    _(f"In Friday Shift, Set Entering and Exiting Time for Shifts")
                )
            if (
                time_diff_in_seconds(
                    self.friday_exit_the_first_period,
                    self.friday_entering_the_first_period,
                )
                < 0
            ):
                frappe.throw(
                    _(
                        f"In Friday Shift, Entering Time cannot be greater than Exiting Time"
                    )
                )
            if (
                time_diff_in_seconds(
                    self.friday_exit_the_second_period,
                    self.friday_entering_the_second_period,
                )
                < 0
            ):
                frappe.throw(
                    _(
                        f"In Friday Shift, Entering Time cannot be greater than Exiting Time"
                    )
                )
            is_valid_interval = self.valid_interval_times(
                self.friday_entering_the_first_period,
                self.friday_exit_the_first_period,
                self.friday_entering_the_second_period,
                self.friday_exit_the_second_period,
            )
            if not is_valid_interval:
                frappe.throw(_("Shift 1 and Shift 2 are overlapping in Friday Shift"))
        if self.saturday_different_times:
            if (
                not self.saturday_exit_the_first_period
                or not self.saturday_entering_the_first_period
                or not self.saturday_exit_the_second_period
                or not self.saturday_entering_the_second_period
            ):
                frappe.throw(
                    _(f"In Saturday Shift, Set Entering and Exiting Time for Shifts")
                )
            if (
                time_diff_in_seconds(
                    self.saturday_exit_the_first_period,
                    self.saturday_entering_the_first_period,
                )
                < 0
            ):
                frappe.throw(
                    _(
                        f"In Saturday Shift, Entering Time cannot be greater than Exiting Time"
                    )
                )
            if (
                time_diff_in_seconds(
                    self.saturday_exit_the_second_period,
                    self.saturday_entering_the_second_period,
                )
                < 0
            ):
                frappe.throw(
                    _(
                        f"In Saturday Shift, Entering Time cannot be greater than Exiting Time"
                    )
                )
            is_valid_interval = self.valid_interval_times(
                self.saturday_entering_the_first_period,
                self.saturday_exit_the_first_period,
                self.saturday_entering_the_second_period,
                self.saturday_exit_the_second_period,
            )
            if not is_valid_interval:
                frappe.throw(_("Shift 1 and Shift 2 are overlapping in Saturday Shift"))

    def validate_flexible_shifts_times(self):
        # Cehck Workgin Days
        work_days = [
            "sunday_flexible",
            "monday_flexible",
            "tuesday_flexible",
            "wednesday_flexible",
            "thursday_flexible",
            "friday_flexible",
            "saturday_flexible",
        ]
        has_any_day = False
        for day in work_days:
            if self.get(day):
                has_any_day = True
        if not has_any_day:
            frappe.throw(_("At Least One Working Day is Required"))
        if flt(self.required_hours_per_day) == 0:
            frappe.throw(_("Required Hours must be greater than zero"))
        if time_diff_in_seconds(self.attendance_to, self.attendance_from) < 0:
            frappe.throw(_(f"Start Time cannot be greater than End Time"))

    def validate_employees(self):
        employees_lst = [employee.employee for employee in self.shift_builder_employees]
        if len(employees_lst) > 0:
            employees = ",".join([ f"'{d}'" for d in employees_lst])
        else:
            employees = "''"
        employee_in_other_shifts = frappe.db.sql(
            """SELECT sbe.employee as employee
                        FROM `tabShift Builder` sb
                        LEFT JOIN `tabShift Builder Employee` sbe ON sbe.parent = sb.name
                        WHERE sbe.employee IN ({employees}) AND sb.docstatus=1 AND sb.name<>'{name}'""".format(
                employees=employees, name=self.name
            ),
            as_dict=1,
        )
        if len(employee_in_other_shifts) > 0:
            msg = ""
            employee_in_other_shifts = [
                emp.employee for emp in employee_in_other_shifts
            ]
            for emp in self.shift_builder_employees:
                if emp.employee in employee_in_other_shifts:
                    msg += f"<li>{emp.employee}</li>"
            msg = "<ul>" + msg + "</ul>"
            frappe.throw(_("There is Employees already in other Shift {}".format(msg)))

    def valid_interval_times(self, time1_start, time1_end, time2_start, time2_end):
        interval_status = True
        start1_overlap = (
            time_diff_in_seconds(time1_start, time2_start)
            * time_diff_in_seconds(time1_start, time2_end)
        ) < 0
        end1_overlap = (
            time_diff_in_seconds(time1_end, time2_start)
            * time_diff_in_seconds(time1_end, time2_end)
        ) < 0
        start2_overlap = (
            time_diff_in_seconds(time2_start, time1_start)
            * time_diff_in_seconds(time2_start, time1_end)
        ) < 0
        end2_overlap = (
            time_diff_in_seconds(time2_end, time1_start)
            * time_diff_in_seconds(time2_end, time1_end)
        ) < 0
        if start1_overlap or end1_overlap or start2_overlap or end2_overlap:
            interval_status = False
        return interval_status

    def on_submit(self):
        if self.shift_type == "Double Shift Work Schedule":
            self.validate_employees()
            self.validate_double_shifts()
            self.build_double_shifts()
        elif self.shift_type == "Work Schedule with Different Times":
            self.validate_employees()
            self.validate_different_times_shifts()
            self.build_different_times_shifts()
        elif self.shift_type == "Flexible Work Schedule":
            self.validate_employees()
            self.validate_flexible_shifts_times()
            self.build_flexible_shifts_times()
        else:
            frappe.throw(_(f"Shift Type {self.shift_type} is not supported"))

    def build_double_shifts(self):
        try:
            shift1_name = make_autoname("MDST-.YYYY.-.MM.-.DD.-1.####")
            shift1 = self.create_shift_type(
                shift1_name,
                self.first_period_start_time,
                self.first_period_end_time,
                self.minutes_of_late_entry,
                self.minutes_of_early_exit,
            )
            shift2_name = make_autoname("MDST-.YYYY.-.MM.-.DD.-2.####")
            shift2 = self.create_shift_type(
                shift2_name,
                self.second_period_start_time,
                self.second_period_end_time,
                self.minutes_of_late_entry,
                self.minutes_of_early_exit,
            )
        except Exception as e:
            frappe.throw(_(f"Error while create Shift Type for Doucle Shifts"))
        else:
            self.db_set("double_shift_1", shift1)
            self.db_set("double_shift_2", shift2)
            frappe.db.commit()

    def build_different_times_shifts(self):
        def get_data_for_selected_day(day_name, order):
            start_time = self.get(f"{day_name}_entering_the_{order}_period")
            end_time = self.get(f"{day_name}_exit_the_{order}_period")
            entry_grace = self.get(f"{day_name}_entry_grace_period")
            exit_grace = self.get(f"{day_name}_exit_grace_period")
            order = ""
            if order == "first":
                order = "1"
            if order == "second":
                order = "2"

            days = {
                "sunday": "SU",
                "monday": "MO",
                "tuesday": "TU",
                "wednesday": "WE",
                "thursday": "TH",
                "friday": "FR",
                "saturday": "SA",
            }
            abbr = days.get(day_name, "")
            shift_name = make_autoname(f"MDST-.YYYY.-.MM.-.DD.-{abbr}{order}.####")

            return shift_name, start_time, end_time, entry_grace, exit_grace

        work_days = [
            "sunday",
            "monday",
            "tuesday",
            "wednesday",
            "thursday",
            "friday",
            "saturday",
        ]
        for day in work_days:
            if self.get(f"{day}_different_times") == 1:
                try:
                    (
                        _name1,
                        _start_time1,
                        _end_time1,
                        _late_grace1,
                        _early_grace1,
                    ) = get_data_for_selected_day(day, "first")

                    (
                        _name2,
                        _start_time2,
                        _end_time2,
                        _late_grace2,
                        _early_grace2,
                    ) = get_data_for_selected_day(day, "second")

                    shift1_for_day = self.create_shift_type(
                        _name1, _start_time1, _end_time1, _late_grace1, _early_grace1
                    )
                    shift2_for_day = self.create_shift_type(
                        _name2, _start_time2, _end_time2, _late_grace2, _early_grace2
                    )
                    self.db_set(f"{day}_different_times_shift1", shift1_for_day)
                    self.db_set(f"{day}_different_times_shift2", shift2_for_day)
                except Exception as e:
                    frappe.throw(_(f"Error while create Shift Type for Doucle Shifts"))
                else:
                    self.db_set(f"{day}_different_times_shift1", shift1_for_day)
                    self.db_set(f"{day}_different_times_shift2", shift2_for_day)
                    frappe.db.commit()

    def build_flexible_shifts_times(self):
        try:
            shift_name = make_autoname("MFST-.YYYY.-.MM.-.DD.-.####")
            shift = self.create_shift_type(
                shift_name,
                self.attendance_from,
                self.attendance_to,
                self.flexible_grace_period,
                self.flexible_grace_period,
                True,
            )
        except Exception as e:
            frappe.throw(_(f"Error while create Shift Type for Doucle Shifts"))
        else:
            self.db_set("flexible_shift_type", shift)
            frappe.db.commit()

    def create_shift_type(
        self,
        newname,
        start_time,
        end_time,
        late_grace,
        early_grace,
        flexible_shift=False,
    ):
        # shift_type = frappe.new_doc("Shift Type")
        shift_type = frappe.get_doc({"doctype": "Shift Type", "__newname": newname})
        shift_type.start_time = start_time
        shift_type.end_time = end_time
        shift_type.enable_auto_attendance = 1
        shift_type.process_attendance_after = nowdate()
        shift_type.last_sync_of_checkin = now_datetime()
        shift_type.determine_check_in_and_check_out = (
            self.determine_check_in_and_check_out
        )
        shift_type.working_hours_calculation_based_on = (
            self.working_hours_calculation_based_on
        )
        shift_type.begin_check_in_before_shift_start_time = self.allow_entry_time
        shift_type.allow_check_out_after_shift_end_time = self.allow_exit_time
        shift_type.working_hours_threshold_for_half_day = (
            self.working_hours_threshold_for_half_day
        )
        shift_type.working_hours_threshold_for_absent = (
            self.working_hours_threshold_for_absent
        )

        if cint(late_grace) != 0:
            shift_type.enable_entry_grace_period = 1
            shift_type.late_entry_grace_period = cint(late_grace)
        if cint(early_grace) != 0:
            shift_type.enable_exit_grace_period = 1
            shift_type.early_exit_grace_period = cint(early_grace)
        if flexible_shift:
            shift_type.max_working_hours = flt(self.required_hours_per_day)
        shift_type.save()
        frappe.db.commit()
        shift_type.reload()
        return shift_type.name

    def on_update_after_submit(self):
        self.validate_employees()


def daily_shift_requests_creation():
    # Create Shift Request based on shift builder type
    build_flexible_shifts_requests()
    build_different_times_shift_requests()
    build_double_shift_requests()


def build_flexible_shifts_requests():
    builders = frappe.get_list(
        "Shift Builder",
        filters={
            "docstatus": 1,
            "status": "Enabled",
            "shift_type": "Flexible Work Schedule",
        },
    )
    weekday = frappe.utils.get_weekday().lower()
    nowdate = frappe.utils.nowdate()
    for shift_builder in builders:
        shift_builder = frappe.get_doc("Shift Builder", shift_builder.name)
        if (
            not shift_builder.flexible_shift_type
            or len(shift_builder.flexible_shift_type) == 0
        ):
            continue
        if cint(shift_builder.get(f"{weekday}_flexible")) == 1:
            for employee in shift_builder.shift_builder_employees:
                create_shift_request_for_employee(
                    shift_builder.flexible_shift_type,
                    employee.employee,
                    nowdate,
                    shift_builder.name,
                )
    frappe.db.commit()


def build_different_times_shift_requests():
    builders = frappe.get_list(
        "Shift Builder",
        filters={
            "docstatus": 1,
            "status": "Enabled",
            "shift_type": "Work Schedule with Different Times",
        },
    )
    weekday = frappe.utils.get_weekday().lower()
    nowdate = frappe.utils.nowdate()
    for shift_builder in builders:
        shift_builder = frappe.get_doc("Shift Builder", shift_builder.name)
        if cint(shift_builder.get(f"{weekday}_different_times")) == 1:
            first_shift = shift_builder.get(f"{weekday}_different_times_shift1")
            second_shift = shift_builder.get(f"{weekday}_different_times_shift2")

            for employee in shift_builder.shift_builder_employees:
                if first_shift:
                    create_shift_request_for_employee(
                        first_shift, employee.employee, nowdate, shift_builder.name
                    )
                if second_shift:
                    create_shift_request_for_employee(
                        second_shift, employee.employee, nowdate, shift_builder.name
                    )
    frappe.db.commit()


def build_double_shift_requests():
    builders = frappe.get_list(
        "Shift Builder",
        filters={
            "docstatus": 1,
            "status": "Enabled",
            "shift_type": "Double Shift Work Schedule",
        },
    )
    weekday = frappe.utils.get_weekday().lower()
    nowdate = frappe.utils.nowdate()
    for shift_builder in builders:
        shift_builder = frappe.get_doc("Shift Builder", shift_builder.name)
        if cint(shift_builder.get(f"{weekday}_two_shift")) == 1:
            for employee in shift_builder.shift_builder_employees:
                if shift_builder.double_shift_1:
                    create_shift_request_for_employee(
                        shift_builder.double_shift_1,
                        employee.employee,
                        nowdate,
                        shift_builder.name,
                    )
                if shift_builder.double_shift_2:
                    create_shift_request_for_employee(
                        shift_builder.double_shift_2,
                        employee.employee,
                        nowdate,
                        shift_builder.name,
                    )
    frappe.db.commit()


def create_shift_request_for_employee(shift_type, employee, date, shift_builder_name):
    try:
        shift_request = frappe.new_doc("Shift Request")
        shift_request.update(
            {
                "shift_type": shift_type,
                "employee": employee,
                "from_date": date,
                "to_date": date,
                "status": "Approved",
            }
        )
        shift_request.flags.ignore_permissions = True
        shift_request.flags.ignore_mandatory = True
        shift_request.insert(ignore_permissions=True)
        shift_request.submit()
    except Exception as e:
        frappe.log_error(
            title=_(
                "Error while Create/Approve Shift Request for Shift Builder{0}"
            ).format(shift_builder_name),
            message=e,
        )