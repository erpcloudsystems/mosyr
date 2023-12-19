# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from datetime import datetime


def execute(filters=None):
	columns = get_columns()
	data=get_data(filters,columns)
	return columns, data

def get_columns():
	return [

		{
			"label": _("Code"),
			"fieldname": "code",
			"fieldtype": "Link",
			"options": "Employee",
			"width": 170
		},
		{
			"label": _("Name"),
			"fieldname": "employee_name",
			"fieldtype": "Data",
			"width": 170
		},
		{
			"label": _("Working Hours"),
			"fieldname": "working_hours",
			"fieldtype": "Data",
			"width": 200
		},
		{
			"label": _("Overtime"),
			"fieldname": "overtime",
			"fieldtype": "Data",
			"width": 200
		},
		{
			"label": _("Late"),
			"fieldname": "lates",
			"fieldtype": "Data",
			"width": 200
		}
		,
		{
			"label": _("Early Overtime"),
			"fieldname": "early_come",
			"fieldtype": "Data",
			"width": 200
		}
		 ,
		{
			"label": _(" Early Leave"),
			"fieldname": "early_leave",
			"fieldtype": "Data",
			"width": 200
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
			employee_name as employee_name,
			working_hours as working_hours,
			attendance_date as attendance_date,

		CASE
			WHEN  ( TIME_TO_SEC(TIME(in_time)) - TIME_TO_SEC(( SELECT (start_time) from `tabShift Type` where name =  `tabAttendance`.shift  ORDER BY creation DESC LIMIT 1) )) < 0 THEN 0
			ELSE ( TIME_TO_SEC(TIME(in_time)) - TIME_TO_SEC(( SELECT (start_time) from `tabShift Type` where name =  `tabAttendance`.shift  ORDER BY creation DESC LIMIT 1) ))
		END AS lates,

		CASE
			WHEN  ( TIME_TO_SEC(TIME(in_time)) - TIME_TO_SEC(( SELECT (start_time) from `tabShift Type` where name =  `tabAttendance`.shift  ORDER BY creation DESC LIMIT 1) )) > 0 THEN 0
			ELSE ABS((TIME_TO_SEC(TIME(in_time)) - TIME_TO_SEC(( SELECT (start_time) from `tabShift Type` where name =  `tabAttendance`.shift  ORDER BY creation DESC LIMIT 1) )) )
		END AS early_come,

		CASE
			WHEN ( TIME_TO_SEC(TIME(out_time)) - TIME_TO_SEC(( SELECT (end_time) from `tabShift Type` where name =  `tabAttendance`.shift  ORDER BY creation DESC LIMIT 1) ))  < 0 THEN 0
			ELSE ( TIME_TO_SEC(TIME(out_time)) - TIME_TO_SEC(( SELECT (end_time) from `tabShift Type` where name =  `tabAttendance`.shift  ORDER BY creation DESC LIMIT 1) )) 
		END AS overtime,
								 
		CASE
			WHEN ( TIME_TO_SEC(TIME(out_time)) - TIME_TO_SEC(( SELECT (end_time) from `tabShift Type` where name =  `tabAttendance`.shift  ORDER BY creation DESC LIMIT 1) ))  > 0 THEN 0
			ELSE ABS(( TIME_TO_SEC(TIME(out_time)) - TIME_TO_SEC(( SELECT (end_time) from `tabShift Type` where name =  `tabAttendance`.shift  ORDER BY creation DESC LIMIT 1) )) )
		END AS early_leave
		   
		from
			`tabAttendance`
			
		where
			docstatus = 1 
		AND
			attendance_date between '{from_dates}' and '{to_dates}'
		Group by 
		code
		""".format(from_dates=from_dates, to_dates=to_dates)
		
	if conditions:
			query += " AND " + " AND ".join(conditions)

	item_results = frappe.db.sql(query, as_dict = 1)
	for row in item_results:
		row['working_hours'] = seconds_to_hms(row['working_hours'])
		row['overtime'] = seconds_to_hms(row['overtime'])
		row['lates'] = seconds_to_hms(row['lates'])
		row['early_come'] = seconds_to_hms(row['early_come'])
		row['early_leave'] = seconds_to_hms(row['early_leave'])
	return item_results

def seconds_to_hms(seconds):
    if seconds is None or seconds == 0:
        return "0:0:0"

    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{int(hours)}:{int(minutes)}:{int(seconds)}"



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

	# return result