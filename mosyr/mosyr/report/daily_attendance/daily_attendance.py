# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe import _
import datetime
from erpnext.hr.doctype.holiday_list.holiday_list import is_holiday

def execute(filters=None):
	current_date = datetime.date.today()
	columns = get_columns()
	from_date_str = filters.get("from_date")
	from_date = datetime.datetime.strptime(from_date_str, "%Y-%m-%d").date() if from_date_str else None

	if from_date and current_date >= from_date:
		# If the condition is met, get the data
		data = get_data(filters, columns)
	else:
		# If the condition is not met, return an empty data list
		data = []
	return columns, data

def get_columns():
	return [
		{
			"label": _("Code"),
			"fieldname": "code",
			"fieldtype": "Link",
			"options": "Employee",
			"width": 70
		},
	
		{
			"label": _("Name"),
			"fieldname": "employee_name",
			"fieldtype": "Data",
			"width": 200
		},
		{
			"label": _("Count"),
			"fieldname": "shift_count",
			"fieldtype": "int",
			"width": 70
		},
		{
			"label": _("Department"),
			"fieldname": "department",
			"fieldtype": "Link",
			"options": "Department",
			"width": 170
		},
		{
			"label": _("Shift"),
			"fieldname": "shift",
			"fieldtype": "Data",
			"width": 120
		},
		{
			"label": _("Status"),
			"fieldname": "status",
			"fieldtype": "Data",
			"width": 100
		},

		{
			"label": _("In Time"),
			"fieldname": "in_time",
			"fieldtype": "Time",
			"width": 120
		},
		{
			"label": _("Out Time"),
			"fieldname": "out_time",
			"fieldtype": "Time",
			"width": 120
		},
		{
			"label": _("Working Hours"),
			"fieldname": "working_hours",
			"fieldtype": "Data",
			"width": 120
		},
		{
			"label": _("Attendance Request"),
			"fieldname": "attendance_request",
			"fieldtype": "Link",
			"options": "Attendance Request",
			"width": 160
		},
		{
			"label": _("Leave Application"),
			"fieldname": "leave_application",
			"fieldtype": "Link",
			"options": "Leave Application",
			"width": 160
		},
		{
			"label": _("Overtime Leave"),
			"fieldname": "overtime",
			"fieldtype": "Data",
			"width": 100
		},
		{
			"label": _("Late Arrive"),
			"fieldname": "lates",
			"fieldtype": "Data",
			"width": 100
		}
		,
		{
			"label": _("Early Arrive"),
			"fieldname": "early_come",
			"fieldtype": "Data",
			"width": 100
		}
		 ,
		{
			"label": _(" Early Leave"),
			"fieldname": "early_leave",
			"fieldtype": "Data",
			"width": 100
		}
	]

def get_data(filters, columns):
	item_price_qty_data = []
	item_price_qty_data = get_attendance_data(filters)
	return item_price_qty_data

def get_attendance_data(filters):
	from_dates = filters.get("from_date")
	to_dates = filters.get("to_date")
	conditions = []
	if 'department' in filters:
		conditions.append(
			f"(department = '{filters['department']}' )")
	if 'employee' in filters:
		conditions.append(
			f"(employee = '{filters['employee']}' )")
	if 'shift' in filters:
		conditions.append(
			f"(shift = '{filters['shift']}' )")
	query = """
		select
			name as name,
			employee as code,
				IFNULL(
						(SELECT COUNT(*) FROM `tabShift Assignment`
						WHERE docstatus = 1
						AND employee = `tabAttendance`.employee
						AND start_date >= '{from_dates}'
						AND end_date <= '{from_dates}'
					
						), 0) AS shift_count,
			employee_name as employee_name,
			department as department,
			shift as shift ,
			status as status,
			in_time as in_time,
			out_time as out_time,
			working_hours as working_hours,
			attendance_date as attendance_date,
			attendance_request as attendance_request,
			leave_application as leave_application,
			(SELECT holiday_list FROM `tabShift Type` WHERE name = `tabAttendance`.shift ORDER BY creation DESC LIMIT 1) as holiday_list,

		CASE
			WHEN  ( TIME_TO_SEC(TIME(in_time)) - TIME_TO_SEC(( SELECT (start_time) from `tabShift Type` where name =  `tabAttendance`.shift  ORDER BY creation DESC LIMIT 1) )) < 0 THEN 0
			ELSE ( TIME_TO_SEC(TIME(in_time)) - TIME_TO_SEC(( SELECT (start_time) from `tabShift Type` where name =  `tabAttendance`.shift  ORDER BY creation DESC LIMIT 1) )) / 60
		END AS lates,

		CASE
			WHEN  ( TIME_TO_SEC(TIME(in_time)) - TIME_TO_SEC(( SELECT (start_time) from `tabShift Type` where name =  `tabAttendance`.shift  ORDER BY creation DESC LIMIT 1) )) > 0 THEN 0
			ELSE ABS((TIME_TO_SEC(TIME(in_time)) - TIME_TO_SEC(( SELECT (start_time) from `tabShift Type` where name =  `tabAttendance`.shift  ORDER BY creation DESC LIMIT 1) )) / 60)
		END AS early_come,

		CASE
			WHEN ( TIME_TO_SEC(TIME(out_time)) - TIME_TO_SEC(( SELECT (end_time) from `tabShift Type` where name =  `tabAttendance`.shift  ORDER BY creation DESC LIMIT 1) ))  < 0 THEN 0
			ELSE ( TIME_TO_SEC(TIME(out_time)) - TIME_TO_SEC(( SELECT (end_time) from `tabShift Type` where name =  `tabAttendance`.shift  ORDER BY creation DESC LIMIT 1) )) / 60
		END AS overtime,
								 
		CASE
			WHEN ( TIME_TO_SEC(TIME(out_time)) - TIME_TO_SEC(( SELECT (end_time) from `tabShift Type` where name =  `tabAttendance`.shift  ORDER BY creation DESC LIMIT 1) ))  > 0 THEN 0
			ELSE ABS(( TIME_TO_SEC(TIME(out_time)) - TIME_TO_SEC(( SELECT (end_time) from `tabShift Type` where name =  `tabAttendance`.shift  ORDER BY creation DESC LIMIT 1) )) / 60)
		END AS early_leave
		   
		from
			`tabAttendance`
			
		where
			docstatus = 1 
		AND
			attendance_date = '{from_dates}'
		ORDER BY code, attendance_date, shift
		""".format(from_dates=from_dates, to_dates=to_dates)
		
	if conditions:
			query += " AND " + " AND ".join(conditions)

	item_results = frappe.db.sql(query, as_dict = 1)
	pervious = None
	counter=1
	index= 0 
	for row in item_results:
		if row['code'] == pervious:
			counter = int(counter) + int(1)
			item_results[index-1]['shift_count'] = counter
			row['attendance_date']= None
			row['employee_name']= None
			row['department']= None
			row['code']= None
			row['shift_count']= None
		else:
			row['shift_count'] = counter

		if row['in_time'] is not None:
			row['in_time'] = row['in_time'].time()
		

		if row['out_time'] is not None:
			row['out_time'] = row['out_time'].time()
	
		row['working_hours'] = seconds_to_hms(row['working_hours'] * 60 * 60)
		row['overtime'] = seconds_to_hms(row['overtime'])
		row['lates'] = seconds_to_hms(row['lates'])
		row['early_come'] = seconds_to_hms(row['early_come'])
		row['early_leave'] = seconds_to_hms(row['early_leave'])
		pervious = row['code']
		counter = 1
		index += 1
	employees = get_all_employee(filters)
	list_emp = []
	for row in employees:
		list_emp.append(row['name'])
	attendace_list=[]
	for row in item_results:
		attendace_list.append(row["code"])
	for emp in list_emp:
		if emp not in attendace_list:
			item_results.append({
				"code": emp,
				"employee_name": [item for item in employees if item.get('name') == emp][0].get('employee_name'),
				"holiday_list":[item for item in employees if item.get('name') == emp][0].get('holiday_list') or None,
				"status": None
			})
	
	for res in item_results:
		if res['status'] is None:
			if res['holiday_list']:
				if is_holiday(res['holiday_list'], from_dates):
					res['status'] = "عطله"
				else:
					res['status'] = "لا شيفت"
			else:
				res['status'] = "لا شيفت"
			
				
	return item_results

def seconds_to_hms(seconds):
	if seconds is None or seconds == 0:
		return "0:0:0"

	hours, remainder = divmod(seconds, 3600)
	minutes, seconds = divmod(remainder, 60)
	return f"{int(hours)}:{int(minutes)}:{int(seconds)}"
def get_all_employee(filters):
	conditions = []
	if 'employee' in filters:
		conditions.append(
			f"(employee = '{filters['employee']}' )")
	if 'department' in filters:
		conditions.append(
			f"(department = '{filters['department']}' )")
	query = """
		SELECT name,employee_name, holiday_list  from `tabEmployee` where status ='Active'
	"""
	if conditions:
			query += " AND " + " AND ".join(conditions)
	return frappe.db.sql(query, as_dict = 1)
	# frappe.msgprint(str(item_results))
	# result = []
	# if item_results:
	#     for item_dict in item_results:
	#         data = {
	#             'name': item_dict.name,
	#             'code': item_dict.code,
	#             'employee_name': item_dict.employee_name,
	#             'department': item_dict.department,
	#             'shift': item_dict.shift,
	#             'status': item_dict.status,
	#             'in_time': item_dict.in_time,
	#             'out_time': item_dict.out_time,
	#             'working_hours': item_dict.working_hours,
	#             'attendance_date': item_dict.attendance_date,
	#             'attendance_request': item_dict.attendance_request,
	#             'leave_application': item_dict.leave_application,
	#         }
	#         pp = frappe.get_last_doc('Shift Type', filters={"name": item_dict.shift})
			
	#         def calculate_difference(time1, time2):
	#             if time1 and time2:
	#                 time1 = datetime.strptime(str(time1.time()), '%H:%M:%S')
	#                 time2 = datetime.strptime(str(time2), '%H:%M:%S')
	#                 time_difference = (time1 - time2).total_seconds()
	#                 return int(time_difference) if time_difference > 0 else 0
	#             return 0

	#         data['lates'] = calculate_difference(item_dict.in_time, pp.start_time)
	#         data['overtime'] = calculate_difference(item_dict.out_time, pp.end_time)

	#         result.append(data)

	return result

