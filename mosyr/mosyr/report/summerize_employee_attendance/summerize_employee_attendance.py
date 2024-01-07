# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe import _
# from datetime import datetime
from datetime import datetime,timedelta


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
			"width": 150
		},
		{
			"label": _("Name"),
			"fieldname": "employee_name",
			"fieldtype": "Data",
			"width": 150
		},
		{
			"label": _("Working Hours"),
			"fieldname": "working_hours",
			"fieldtype": "Data",
			"width": 100
		},

		{
			"label": _("Late"),
			"fieldname": "lates",
			"fieldtype": "Data",
			"width": 100
		}
		,
		{
			"label": _("Count Late"),
			"fieldname": "records_with_lates",
			"fieldtype": "Data",
			"width": 100
		},
		{
			"label": _(" Early Leave"),
			"fieldname": "early_leave",
			"fieldtype": "Data",
			"width": 100
		},
		{
			"label": _("Count Early Leave"),
			"fieldname": "records_with_early_leave",
			"fieldtype": "Data",
			"width": 100
		},
		{
			"label": _("Total"),
			"fieldname": "total1",
			"fieldtype": "Data",
			"width": 100
		},
		{
			"label": _("Overtime"),
			"fieldname": "overtime",
			"fieldtype": "Data",
			"width": 100
		},
		{
			"label": _("Count Overtime"),
			"fieldname": "records_with_overtime",
			"fieldtype": "Data",
			"width": 100
		},
		{
			"label": _("Early Overtime"),
			"fieldname": "early_come",
			"fieldtype": "Data",
			"width": 100
		}
		 ,
		 {
			"label": _("Count Early Overtime"),
			"fieldname": "records_with_early_come",
			"fieldtype": "Data",
			"width": 100
		},
		{
			"label": _("Total"),
			"fieldname": "total2",
			"fieldtype": "Data",
			"width": 100
		},
		{
			"label": _("No Finger Print Out"),
			"fieldname": "missed_finger_print",
			"fieldtype": "Data",
			"width": 100
		},
		{
			"label": _("No Entry Finger Print"),
			"fieldname": "missed_finger_print_entry",
			"fieldtype": "Data",
			"width": 100
		},
		{
			"label": _("Absent"),
			"fieldname": "count_absent",
			"fieldtype": "Data",
			"width": 100
		},
		{
			"label": _("Present"),
			"fieldname": "count_present",
			"fieldtype": "Data",
			"width": 100
		},
		{
			"label": _("Total Holidays"),
			"fieldname": "count_on_leave",
			"fieldtype": "Data",
			"width": 100
		},
		{
			"label": _("Count"),
			"fieldname": "shift_count",
			"fieldtype": "Data",
			"width": 100
		},
		
		
		
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
	result= []
	data_attendace = []
	employees = get_all_employee(filters)
	days=[]
	new_data=[]

	for emp in employees:
		# shift_assignments = """
		# 	SELECT count(*) as count from `tabShift Assignment` where employee = '{emp}'
		# """.format(emp=emp['name'])
		
		
	
		count_lates = lates = early_leave =count_early_leave =  early_come =count_early_come = count_overtime = overtime = missed_finger_print = missed_finger_print_entry= 0
		count_holiday = count_absent = count_present = working_hours = count_on_leave =  0 
		
		query = """
				SELECT
					name as name,
					employee as code,
					employee_name as employee_name,
					working_hours as working_hours,
					attendance_date as attendance_date,
					in_time as in_time,
					out_time as out_time,
					status as status,
					shift as shift,
					(SELECT holiday_list FROM `tabShift Type` WHERE name = `tabAttendance`.shift ORDER BY creation DESC LIMIT 1) as holiday_list,
					(SELECT start_time FROM `tabShift Type` WHERE name = `tabAttendance`.shift ORDER BY creation DESC LIMIT 1) as start_time,
					IFNULL((SELECT late_entry_grace_period FROM `tabShift Type` WHERE name = `tabAttendance`.shift ORDER BY creation DESC LIMIT 1), 0) as late_entry_grace_period,
					(SELECT end_time FROM `tabShift Type` WHERE name = `tabAttendance`.shift ORDER BY creation DESC LIMIT 1) as end_time,
					IFNULL((SELECT early_exit_grace_period FROM `tabShift Type` WHERE name = `tabAttendance`.shift ORDER BY creation DESC LIMIT 1), 0) as early_exit_grace_period,
					CASE
						WHEN (TIME_TO_SEC(TIME(in_time)) - TIME_TO_SEC((SELECT start_time FROM `tabShift Type` WHERE name = `tabAttendance`.shift ORDER BY creation DESC LIMIT 1))) < 0 THEN 0
						ELSE (TIME_TO_SEC(TIME(in_time)) - TIME_TO_SEC((SELECT start_time FROM `tabShift Type` WHERE name = `tabAttendance`.shift ORDER BY creation DESC LIMIT 1)))
					END AS lates,
					CASE
						WHEN (TIME_TO_SEC(TIME(in_time)) - TIME_TO_SEC((SELECT start_time FROM `tabShift Type` WHERE name = `tabAttendance`.shift ORDER BY creation DESC LIMIT 1))) > 0 THEN 0
						ELSE ABS((TIME_TO_SEC(TIME(in_time)) - TIME_TO_SEC((SELECT start_time FROM `tabShift Type` WHERE name = `tabAttendance`.shift ORDER BY creation DESC LIMIT 1))))
					END AS early_come,

					(CASE 
						WHEN (SELECT end_time FROM `tabShift Type` WHERE name = `tabAttendance`.shift ORDER BY creation DESC LIMIT 1) < (SELECT start_time FROM `tabShift Type` WHERE name = `tabAttendance`.shift ORDER BY creation DESC LIMIT 1)
							AND DATE(in_time) = DATE(out_time)
							THEN
								CASE
									WHEN (UNIX_TIMESTAMP((out_time)) - UNIX_TIMESTAMP((SELECT DATE_FORMAT(end_time, CONCAT((DATE_ADD(DATE(out_time), INTERVAL 1 DAY)), ' %H:%i:%s')) FROM `tabShift Type` WHERE name = `tabAttendance`.shift ORDER BY creation DESC LIMIT 1))) < 0 THEN 0
									ELSE (UNIX_TIMESTAMP((out_time)) - UNIX_TIMESTAMP((SELECT DATE_FORMAT(end_time, CONCAT((DATE_ADD(DATE(out_time), INTERVAL 1 DAY)), ' %H:%i:%s')) FROM `tabShift Type` WHERE name = `tabAttendance`.shift ORDER BY creation DESC LIMIT 1)))
								END
							Else
								CASE
									WHEN (UNIX_TIMESTAMP((out_time)) - UNIX_TIMESTAMP((SELECT DATE_FORMAT(end_time, CONCAT(DATE(out_time), ' %H:%i:%s')) FROM `tabShift Type` WHERE name = `tabAttendance`.shift ORDER BY creation DESC LIMIT 1))) < 0 THEN 0
									ELSE (UNIX_TIMESTAMP((out_time)) - UNIX_TIMESTAMP((SELECT DATE_FORMAT(end_time, CONCAT(DATE(out_time), ' %H:%i:%s')) FROM `tabShift Type` WHERE name = `tabAttendance`.shift ORDER BY creation DESC LIMIT 1)))
								END
					END)
					AS overtime,
					(CASE 
						WHEN (SELECT end_time FROM `tabShift Type` WHERE name = `tabAttendance`.shift ORDER BY creation DESC LIMIT 1) < (SELECT start_time FROM `tabShift Type` WHERE name = `tabAttendance`.shift ORDER BY creation DESC LIMIT 1)
							AND DATE(in_time) = DATE(out_time)
							THEN
								CASE
									WHEN (UNIX_TIMESTAMP((out_time)) - UNIX_TIMESTAMP((SELECT DATE_FORMAT(end_time, CONCAT(DATE_ADD(DATE(out_time), INTERVAL 1 DAY), ' %H:%i:%s')) FROM `tabShift Type` WHERE name = `tabAttendance`.shift ORDER BY creation DESC LIMIT 1))) > 0 THEN 0
									ELSE ABS((UNIX_TIMESTAMP((out_time)) - UNIX_TIMESTAMP((SELECT DATE_FORMAT(end_time, CONCAT(DATE_ADD(DATE(out_time), INTERVAL 1 DAY), ' %H:%i:%s')) FROM `tabShift Type` WHERE name = `tabAttendance`.shift ORDER BY creation DESC LIMIT 1))))
								END
							Else
								CASE
									WHEN (UNIX_TIMESTAMP((out_time)) - UNIX_TIMESTAMP((SELECT DATE_FORMAT(end_time, CONCAT(DATE(out_time), ' %H:%i:%s')) FROM `tabShift Type` WHERE name = `tabAttendance`.shift ORDER BY creation DESC LIMIT 1))) > 0 THEN 0
									ELSE ABS((UNIX_TIMESTAMP((out_time)) - UNIX_TIMESTAMP((SELECT DATE_FORMAT(end_time, CONCAT(DATE(out_time), ' %H:%i:%s')) FROM `tabShift Type` WHERE name = `tabAttendance`.shift ORDER BY creation DESC LIMIT 1))))
								END
					END)
					AS early_leave,
					CASE
						WHEN (TIME_TO_SEC(TIME(out_time)) - TIME_TO_SEC((SELECT DATE_FORMAT(end_time, CONCAT(DATE(out_time), ' %H:%i:%s')) FROM `tabShift Type` WHERE name = `tabAttendance`.shift ORDER BY creation DESC LIMIT 1))) > 0 THEN 0
						ELSE ABS((TIME_TO_SEC(TIME(out_time)) - TIME_TO_SEC((SELECT DATE_FORMAT(end_time, CONCAT(DATE(out_time), ' %H:%i:%s')) FROM `tabShift Type` WHERE name = `tabAttendance`.shift ORDER BY creation DESC LIMIT 1))))
					END AS early_leave
				FROM
					`tabAttendance`
				WHERE
					docstatus = 1 
					AND attendance_date between '{from_dates}' and '{to_dates}'
					AND employee = '{emp}'
				ORDER BY attendance_date ;

			""".format(from_dates=from_dates, to_dates = to_dates, emp=emp['name'])
		
		attendace = frappe.db.sql(query, as_dict = 1)
		counter = 0
		max_count = 0
		if attendace:
			# frappe.throw(f"{attendace}")
			pervious = None
			counter=1
			index= 0 
			attendace_only=[]
			
			for attend in attendace:
				if pervious == attend['attendance_date']:
					counter += 1
					max_count = counter
					# if isinstance((result[index-1]['employee_name']), int): 
					# result[-1]['employee_name'] = counter
				else:
					counter=1
				max_count = max(counter, max_count)
				late_entry_grace_period = 0 
				early_exit_grace_period = 0 

				if attend['late_entry_grace_period']:
					late_entry_grace_period = late_entry_grace_period * 60
				if attend['early_exit_grace_period']:
					early_exit_grace_period = early_exit_grace_period * 60

				# if attend['lates'] is None:
				# 	attend['lates'] = 0 
				# if attend['lates'] is None:
				# 	attend['lates'] = 0 
				if attend['lates']:
					lates += (attend['lates'] - late_entry_grace_period)
					if (attend['lates'] - late_entry_grace_period) > 0:
						count_lates +=1
				if attend['early_leave']:
					early_leave += (attend['early_leave'] - early_exit_grace_period)
					if  (attend['early_leave'] - early_exit_grace_period) > 0:
						count_early_leave +=1

				if attend['early_come']:
					early_come += attend['early_come']
					count_early_come +=1

				if attend['overtime']:
					overtime += attend['overtime']
					count_overtime +=1
				if  attend['out_time'] is None and attend['in_time']:
					missed_finger_print +=1
				if  attend['in_time'] is None and attend['out_time']:
					missed_finger_print_entry += 1

				if  attend['status'] == "Absent":
					count_absent += 1
				if  attend['status'] == "Present":
					count_present += 1
				if attend['status'] == "On leave":
					count_on_leave +=1
				if attend['working_hours']:
					working_hours += attend['working_hours']
				pervious = attend['attendance_date']
					
		new_data.append(
			{
				"code":  emp['name'],
				"employee_name":  emp['employee_name'],
				"working_hours":  seconds_to_hms(working_hours * 60* 60),
				"lates": seconds_to_hms(lates),
				"records_with_lates": count_lates,
				"early_leave": seconds_to_hms(early_leave),
				"total1": seconds_to_hms(lates+early_leave),
				"records_with_early_leave": count_early_leave,
				"early_come": seconds_to_hms(early_come),
				"records_with_early_come": count_early_come,
				"overtime": seconds_to_hms(overtime),
				"total2": seconds_to_hms(overtime + early_come),
				"records_with_overtime": count_overtime,
				"missed_finger_print": missed_finger_print,
				"missed_finger_print_entry": missed_finger_print_entry,
				"count_absent": count_absent,
				"count_present": count_present,
				"count_on_leave": count_on_leave,
				"shift_count":max_count
			}
		)
		
		
	
	return new_data

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
		SELECT *  from `tabEmployee` where status ='Active'
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

	# return result