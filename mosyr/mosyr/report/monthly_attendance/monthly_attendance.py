# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from datetime import datetime,timedelta
from erpnext.hr.doctype.holiday_list.holiday_list import is_holiday


def execute(filters=None):
	columns = get_columns()
	data=get_data(filters,columns)
	return columns, data

def get_columns():
	columns= [

		{
			"label": _("Code"),
			"fieldname": "code",
			"fieldtype": "Data",
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
			"fieldtype": "Data",
			"width": 100
		},
		{
			"label": _("Out Time"),
			"fieldname": "out_time",
			"fieldtype": "Data",
			"width": 100
		},
		{
			"label": _("Working Hours"),
			"fieldname": "working_hours",
			"fieldtype": "Data",
			"width": 100
		},
		
		{
			"label": _("Late Arrive"),
			"fieldname": "lates",
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
			"label": _("Total"),
			"fieldname": "total1",
			"fieldtype": "Data",
			"width": 100
		},
		{
			"label": _("Early Arrive"),
			"fieldname": "early_come",
			"fieldtype": "Data",
			"width": 100
		},
		 {
			"label": _("Overtime Leave"),
			"fieldname": "overtime",
			"fieldtype": "Data",
			"width": 100
		},
		{
			"label": _("Total"),
			"fieldname": "total2",
			"fieldtype": "Data",
			"width": 100
		},
		
	]

	return columns

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
	current_date = datetime.strptime(from_dates, "%Y-%m-%d")
	last_date = datetime.strptime(to_dates, "%Y-%m-%d")
	while current_date <= last_date:
		days.append(current_date.strftime("%Y-%m-%d"))
		current_date += timedelta(days=1)
	current_date = datetime.strptime(from_dates, "%Y-%m-%d")
	for emp in employees:
		# shift_assignments = """
		# 	SELECT count(*) as count from `tabShift Assignment` where employee = '{emp}'
		# """.format(emp=emp['name'])
		
		
		
		result.append({
			"code": emp['name'],
			"employee_name": emp['employee_name'],
			"holiday_list" : None,
			"status": None
		})
		result.append({
			"code": "التاريخ",
			"employee_name": "الفترة",
			"in_time": "دخول",
			"out_time": "خروج",
			"lates": "تاخير",
			"early_leave": "تقصير",
			"early_come": "مبكر",
			"overtime": "اضافى",
			"working_hours": "ساعات العمل",
			"status": "الحاله",
			"holiday_list" : None
		})
		count_lates = lates = early_leave =count_early_leave =  early_come =count_early_come = count_overtime = overtime = missed_finger_print = missed_finger_print_entry= 0
		count_holiday = count_absent = count_present = 0 
		for day in days:
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
    AND attendance_date = '{day}'
    AND employee = '{emp}'
ORDER BY attendance_date, shift;

				""".format(day=day, emp=emp['name'])
			# if conditions:
			# 	query += " AND " + " AND ".join(conditions)
			attendace = frappe.db.sql(query, as_dict = 1)
			if attendace:
				# frappe.throw(f"{attendace}")
				pervious = None
				counter=1
				index= 0 
				attendace_only=[]
				for attend in attendace:
					if pervious == attend['attendance_date']:
						counter += 1
						# if isinstance((result[index-1]['employee_name']), int): 
						result[-1]['employee_name'] = counter
					else:
						counter = 1
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
					attendace_only.append({
						"code": attend['attendance_date'],
						"employee_name": counter,
						"shift": attend['shift'],
						"in_time": attend['in_time'].strftime("%H:%M:%S")if attend['in_time'] is not None else None,
						"out_time": attend['out_time'].strftime("%H:%M:%S") if attend['out_time'] is not None else None,
						"lates": seconds_to_hms((attend['lates'] - late_entry_grace_period) if attend['lates']  is not None else 0 ),
						"early_leave": seconds_to_hms((attend['early_leave'] - early_exit_grace_period) if attend['early_leave']  is not None else 0),
						"early_come": seconds_to_hms(attend['early_come']),
						"overtime": seconds_to_hms(attend['overtime']),
						"working_hours": seconds_to_hms(attend['working_hours']* 60 *60),
						"status": attend['status'],
						"total1":seconds_to_hms(((attend['early_leave'] - early_exit_grace_period) if attend['early_leave']  is not None else 0) + ((attend['lates'] - late_entry_grace_period) if attend['lates']  is not None else 0)),
						"total2":seconds_to_hms((attend['overtime'] if attend['overtime']  is not None else 0) + (attend['early_come'] if attend['early_come']  is not None else 0))
					
					})
					
					result.append({
						"code": attend['attendance_date'],
						"employee_name": counter,
						"shift": attend['shift'],
						"in_time": attend['in_time'].strftime("%H:%M:%S")if attend['in_time'] is not None else None,
						"out_time": attend['out_time'].strftime("%H:%M:%S") if attend['out_time'] is not None else None,
						"lates": seconds_to_hms((attend['lates'] - late_entry_grace_period) if attend['lates']  is not None else 0 ),
						"early_leave": seconds_to_hms((attend['early_leave'] - early_exit_grace_period) if attend['early_leave']  is not None else 0),
						"early_come": seconds_to_hms(attend['early_come']),
						"overtime": seconds_to_hms(attend['overtime']),
						"working_hours": seconds_to_hms(attend['working_hours']* 60 *60),
						"status": attend['status'],
						"total1":seconds_to_hms(((attend['early_leave'] - early_exit_grace_period) if attend['early_leave']  is not None else 0) + ((attend['lates'] - late_entry_grace_period) if attend['lates']  is not None else 0)),
						"total2":seconds_to_hms((attend['overtime'] if attend['overtime']  is not None else 0) + (attend['early_come'] if attend['early_come']  is not None else 0))
					})
				
					result[-1]['holiday_list'] = attend['holiday_list'] or emp['holiday_list']
					pervious = attend['attendance_date']
					index += 1
					if  attend['status'] == "Absent":
						count_absent += 1
					if  attend['status'] == "Present":
						count_present += 1

		
			else:
				if is_holiday(emp['holiday_list'], day):
					result.append({
					"code": day,
					"holiday_list":emp['holiday_list'] or None,
					"status": "عطله"
				})
					count_holiday += 1
				else:
					result.append({
					"code": day,
					"holiday_list":emp['holiday_list'] or None,
					"status": "لا شيفت"
				})
		emp['lates'] = seconds_to_hms(lates)
		emp['count_lates'] = count_lates
		emp['early_leave'] = seconds_to_hms(early_leave)
		emp['count_early_leave'] = count_early_leave
		emp['total_count1'] = count_early_leave + count_lates
		emp['total1'] = seconds_to_hms(early_leave + lates)
		emp['early_come'] = seconds_to_hms(early_come)
		emp['count_early_come'] = count_early_come
		emp['overtime'] = seconds_to_hms(overtime)
		emp['count_overtime'] = count_overtime
		emp['total_count2'] = count_overtime + count_early_come

		emp['total2'] = seconds_to_hms(overtime + early_come)

		emp['missed_finger_print'] = missed_finger_print
		emp['missed_finger_print_entry'] = missed_finger_print_entry
		
				
				
						
			
		emp['count_absent'] = count_absent
		emp['count_present'] = count_present
		emp['count_holiday'] = count_holiday
		emp['current_date'] = current_date.strftime("%Y-%m-%d")
		emp['last_date'] = last_date.strftime("%Y-%m-%d")

		
		
		
	result[0]['lenght_emp'] = employees		
	result[0]['days'] = len(days)	
	result[0]['data_attendace'] = data_attendace
	return result

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