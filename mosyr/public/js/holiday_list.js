frappe.ui.form.on('Holiday List', {
	start_from: function (frm) {
		if (frm.doc.start_from) {
			if (!(frm.doc.from_date && frm.doc.to_date)) {
				frm.events.clear_field(frm, "start_from")
				frappe.throw(__("Please Select From and To Date before"))
			}
			if (!(frm.doc.start_from > frm.doc.from_date && frm.doc.start_from < frm.doc.to_date)) {
				frm.events.clear_field(frm, "start_from")
				frappe.throw(__("Period Start Date must be between From Date and To Date"))
			}
		}
	},
	ends_on: function (frm) {
		if (frm.doc.ends_on) {
			if (!(frm.doc.from_date && frm.doc.to_date)) {
				frm.events.clear_field(frm, "ends_on")
				frappe.throw(__("Please Select From and To Date before"))
			}
			if (!(frm.doc.ends_on > frm.doc.from_date && frm.doc.ends_on < frm.doc.to_date)) {
				frm.events.clear_field(frm, "ends_on")
				frappe.throw(__("Period end Date must be between From Date and To Date"))
			}
		}
	},
	clear_field: function(frm, field){
		frm.set_value(field, "")
		frm.refresh_field(field)
	},
	add_period_holidays: function (frm) {
		if (!(frm.doc.period_description)) {
			frappe.throw(__("Please Enter Period Description"))
		}
		if (!(frm.doc.start_from || frm.doc.ends_on)) {
			frappe.throw(__("Please Select Period From and Period Ends Date"))
		}
		let holiday_list = []
		let day = frm.doc.start_from
		while (day <= frm.doc.ends_on) {
			let is_day_exists = false
			if (frm.doc.holidays.length > 0) {
				frm.doc.holidays.forEach(row => {
					if (row.holiday_date == day) {
						row.description = frm.doc.period_description
						is_day_exists = true
					}
				});
			}
			if (!is_day_exists){
				let data = { "holiday_date": day, "description": frm.doc.period_description }
				holiday_list.push(data)
			}
			console.log(holiday_list);
			day = frappe.datetime.add_days(day, 1);
		}
		if (holiday_list) {
			holiday_list.forEach(row => {
				cur_frm.add_child("holidays", row);
			});
		}
		frm.set_value("period_description", "")
		frm.set_value("start_from", "")
		frm.set_value("ends_on", "")
		frm.refresh_fields()
		console.log("252525");
	}
})