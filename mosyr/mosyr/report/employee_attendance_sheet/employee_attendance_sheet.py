# Copyright (c) 2022, AnvilERP and contributors
# For license information, please see license.txt

import frappe
from frappe import _, msgprint
from frappe.utils import cint, cstr, getdate
import pandas
from datetime import date,timedelta
import datetime
status_map = {
	"Absent": "Absent",
	"Half Day": "Half Day",
	"Holiday": "<b>Holiday</b>",
	"Weekly Off": "<b>Weekly Off</b>",
	"On Leave": "On Leave",
	"Present": "Present",
	"Work From Home": "Work From Home",
}

day_abbr = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

def execute(filters=None):
	_from,to = filters.get('from'),filters.get('to')

	if not filters:
		filters = {}

	if filters.hide_year_field == 1:
		filters.year = 2020

	conditions, filters = get_conditions(filters)
	columns, days = get_columns(filters)
	att_map = get_attendance_list(conditions, filters)
	if not att_map:
		return columns, [], None, None

	if filters.group_by:
		emp_map, group_by_parameters = get_employee_details(filters.group_by, filters.company, filters.branch, filters.department)
		holiday_list = []
		for parameter in group_by_parameters:
			h_list = [
				emp_map[parameter][d]["holiday_list"]
				for d in emp_map[parameter]
				if emp_map[parameter][d]["holiday_list"]
			]
			holiday_list += h_list
	else:
		emp_map = get_employee_details(filters.group_by, filters.company, filters.branch, filters.department)
		holiday_list = [emp_map[d]["holiday_list"] for d in emp_map if emp_map[d]["holiday_list"]]

	default_holiday_list = frappe.get_cached_value(
		"Company", filters.get("company"), "default_holiday_list"
	)
	holiday_list.append(default_holiday_list)
	holiday_list = list(set(holiday_list))
	holiday_map = get_holiday(holiday_list, _from,to)

	data = []

	leave_types = None
	if filters.summarized_view:
		leave_types = frappe.get_all("Leave Type", pluck="name")
		columns.extend([leave_type + ":Float:120" for leave_type in leave_types])
		columns.extend([_("Total Late Entries") + ":Float:120", _("Total Early Exits") + ":Float:120"])

	if filters.group_by:
		emp_att_map = {}
		for parameter in group_by_parameters:
			emp_map_set = set([key for key in emp_map[parameter].keys()])
			att_map_set = set([key for key in att_map.keys()])
			if att_map_set & emp_map_set:
				parameter_row = ["<b>" + parameter + "</b>"] + [
					"" for day in range(filters["total_days_in_month"] + 2)
				]
				data.append(parameter_row)
				record, emp_att_data = add_data(
					emp_map[parameter],
					att_map,
					filters,
					holiday_map,
					conditions,
					default_holiday_list,
					leave_types=leave_types,
				)
				emp_att_map.update(emp_att_data)
				data += record
	else:
		record, emp_att_map = add_data(
			emp_map,
			att_map,
			filters,
			holiday_map,
			conditions,
			default_holiday_list,
			leave_types=leave_types,
		)
		data += record
	chart_data = get_chart_data(emp_att_map, days)
	return columns, data, None, chart_data

def get_chart_data(emp_att_map, days):
	labels = []
	datasets = [
		{"name": "Absent", "values": []},
		{"name": "Present", "values": []},
		{"name": "Leave", "values": []},
	]
	for idx, day in enumerate(days, start=0):
		labels.append(day.replace("::130", ""))
		total_absent_on_day = 0
		total_leave_on_day = 0
		total_present_on_day = 0
		for emp in emp_att_map.keys():
			if emp_att_map[emp][idx]:
				if "Absent" in emp_att_map[emp][idx]:
					total_absent_on_day += 1
				if "Present" in emp_att_map[emp][idx] or "Work From Home" in emp_att_map[emp][idx]:
					total_present_on_day += 1
				if "Half Day" in emp_att_map[emp][idx]:
					total_present_on_day += 0.5
					total_leave_on_day += 0.5
				if "On Leave" in emp_att_map[emp][idx]:
					total_leave_on_day += 1

		datasets[0]["values"].append(total_absent_on_day)
		datasets[1]["values"].append(total_present_on_day)
		datasets[2]["values"].append(total_leave_on_day)

	chart = {"data": {"labels": labels, "datasets": datasets}}

	chart["type"] = "line"

	return chart


def add_data(
	employee_map, att_map, filters, holiday_map, conditions, default_holiday_list, leave_types=None
):
	record = []
	emp_att_map = {}
	for emp in employee_map:
		emp_det = employee_map.get(emp)
		if not emp_det or emp not in att_map:
			continue
		row = []
		if filters.group_by:
			row += [" "]
		row += [emp, emp_det.employee_name, emp_det.department, emp_det.branch]
		total_p = total_a = total_l = total_h = total_um = 0.0
		emp_status_map = []
		date_list = pandas.date_range(filters.get("from"),filters.get("to"))
		for day in date_list:
			status = None
			status = att_map.get(emp).get(datetime.date(day.year,day.month,day.day))
			if status is None and holiday_map:
				emp_holiday_list = emp_det.holiday_list if emp_det.holiday_list else default_holiday_list
				if emp_holiday_list in holiday_map:
					for idx, ele in enumerate(holiday_map[emp_holiday_list]):
						if day == holiday_map[emp_holiday_list][idx][0]:
							if holiday_map[emp_holiday_list][idx][1]:
								status = "Weekly Off"
							else:
								status = "Holiday"
							total_h += 1
			
			abbr = status
			emp_status_map.append(abbr)
			if filters.summarized_view:
				if status:
					if "Present" in status or "Work From Home" in status:
						total_p += 1
					elif "Absent" in  status:
						total_a += 1
					elif "On Leave" in status:
						total_l += 1
					elif "Half Day" in status:
						total_p += 0.5
						total_l += 0.5
					elif not status:
						total_um += 1

		if not filters.summarized_view:
			row += emp_status_map
		if filters.summarized_view:
			row += [total_p, total_l, total_a, total_h, total_um]
		if not filters.get("employee"):
			filters.update({"employee": emp})
			conditions += " and employee = %(employee)s"
		elif not filters.get("employee") == emp:
			filters.update({"employee": emp})
		if filters.summarized_view:
			leave_details = frappe.db.sql(
				"""select leave_type, status, count(*) as count from `tabAttendance`\
				where leave_type is not NULL %s group by leave_type, status"""
				% conditions,
				filters,
				as_dict=1,
			)
			time_default_counts = frappe.db.sql(
				"""select (select count(*) from `tabAttendance` where \
				late_entry = 1 %s) as late_entry_count, (select count(*) from tabAttendance where \
				early_exit = 1 %s) as early_exit_count"""
				% (conditions, conditions),
				filters,
			)
			leaves = {}
			for d in leave_details:
				if d.status == "Half Day":
					d.count = d.count * 0.5
				if d.leave_type in leaves:
					leaves[d.leave_type] += d.count
				else:
					leaves[d.leave_type] = d.count

			for d in leave_types:
				if d in leaves:
					row.append(leaves[d])
				else:
					row.append("0.0")

			row.extend([time_default_counts[0][0], time_default_counts[0][1]])
		emp_att_map[emp] = emp_status_map
		record.append(row)
	return record, emp_att_map


def get_columns(filters):
	columns = []
	if filters.group_by:
		columns = [_(filters.group_by) + ":Link/Branch:120"]
	columns += [_("Employee") + ":Link/Employee:108", _("Employee Name") + ":Data/:150"]
	columns += [_("Department") + ":Link/Department:108", _("Branch") + ":Link/Branch:108"]
	days = []
	from_date = filters.get("from")
	to_date = filters.get("to")
	date_list = pandas.date_range(from_date,to_date)
	for day in date_list:
		date = day.date()
		day_name = day_abbr[getdate(date).weekday()]
		days.append(cstr(date.day) + " " + day_name + "::130")
	if not filters.summarized_view:
		columns += days

	if filters.summarized_view:
		columns += [
			_("Total Present") + ":Float:120",
			_("Total Leaves") + ":Float:120",
			_("Total Absent") + ":Float:120",
			_("Total Holidays") + ":Float:120",
			_("Unmarked Days") + ":Float:120",
		]
	return columns, days

def get_attendance_list(conditions, filters):
	attendance_list = frappe.db.sql(
		f"""select employee, attendance_date as day_of_month, in_time,  out_time,
		status from tabAttendance where docstatus = 1 %s and (attendance_date BETWEEN '{filters.get('from')}' AND '{filters.get('to')}') order by employee, attendance_date"""
		% conditions,
		filters,
		as_dict=1,
	)
	if not attendance_list:
		msgprint(_("No attendance record found"), alert=True, indicator="orange")

	att_map = {}
	for d in attendance_list:
		att_map.setdefault(d.employee, frappe._dict()).setdefault(d.day_of_month, "")
		att_map[d.employee][d.day_of_month] = d.status
		if d.status == "Absent": att_map[d.employee][d.day_of_month] = f"<p style=color:#F683AE;>{d.status}</p>"
		if d.status == "Work From Home":att_map[d.employee][d.day_of_month] = f"<p style=color:green;>{d.status}</p>"
		if d.status == "On Leave":att_map[d.employee][d.day_of_month] = f"<p style=color:green;>{d.status}</p>"
		if d.status == "Half Day":att_map[d.employee][d.day_of_month] = f"<p style=color:blue;>{d.status}</p>"
		if d.status == "Present":att_map[d.employee][d.day_of_month] = f"<p style='margin:0 ;text-align: left !important; color:#318AD8 '>{d.status}</p><p style='margin:0;color:#ffab00'>{f'In Time: {d.in_time.hour}' if d.in_time else ''} {f':{d.in_time.minute}' if d.in_time else ''}</p><p style='margin:0;color:#ffab00'>{f'Out Time: {d.out_time.hour}' if d.out_time else ''} {f':{d.out_time.minute}' if d.out_time else ''}</p>"
	return att_map


def get_conditions(filters):
	if not (filters.get("from") and filters.get("to")):
		msgprint(_("Please select from date and to date"), raise_exception=1)

	filters["total_days_in_month"] = (days_between(filters.get("from"), filters.get("to"))) + 1
	conditions = f" and (attendance_date BETWEEN '{filters.get('from')}' AND '{filters.get('to')}')"
	

	if filters.get("company"):
		conditions += " and company = %(company)s"
	if filters.get("employee"):
		conditions += " and employee = %(employee)s"

	return conditions, filters
def days_between(d1, d2):
			from datetime import datetime
			d1 = datetime.strptime(d1, "%Y-%m-%d")
			d2 = datetime.strptime(d2, "%Y-%m-%d")
			return abs((d2 - d1).days)
		

def get_employee_details(group_by, company, branch=None, department=None):
	emp_map = {}
	conds = []
	if branch:
		conds.append(" branch='{}' ".format(branch))
	if department:
		conds.append(" department='{}' ".format(department))
	if len(conds) > 0:
		conds = " AND ".join(conds)
		conds = " AND {}".format(conds)
	else:
		conds = ""

	query = """select name, employee_name, designation, department, branch, company,
		holiday_list from `tabEmployee` where company = %s """ % frappe.db.escape(
		company
	)

	query = f" {query} {conds} "
	if group_by:
		group_by = group_by.lower()
		query += " order by " + group_by + " ASC"

	employee_details = frappe.db.sql(query, as_dict=1)

	group_by_parameters = []
	if group_by:

		group_by_parameters = list(
			set(detail.get(group_by, "") for detail in employee_details if detail.get(group_by, ""))
		)
		for parameter in group_by_parameters:
			emp_map[parameter] = {}

	for d in employee_details:
		if group_by and len(group_by_parameters):
			if d.get(group_by, None):

				emp_map[d.get(group_by)][d.name] = d
		else:
			emp_map[d.name] = d

	if not group_by:
		return emp_map
	else:
		return emp_map, group_by_parameters


def get_holiday(holiday_list, _from , to):
	holiday_map = frappe._dict()
	for d in holiday_list:
		if d:
			holiday_map.setdefault(
				d,
				frappe.db.sql(
					f"""select holiday_date, weekly_off from `tabHoliday`
				where parent=%s and (holiday_date BETWEEN '{_from}' AND '{to}')""",
					(d),
				),
			)

	return holiday_map


@frappe.whitelist()
def get_attendance_years():
	year_list = frappe.db.sql_list(
		"""select distinct YEAR(attendance_date) from tabAttendance ORDER BY YEAR(attendance_date) DESC"""
	)
	if not year_list:
		year_list = [getdate().year]

	return "\n".join(str(year) for year in year_list)
