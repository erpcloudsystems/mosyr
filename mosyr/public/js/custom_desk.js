frappe.Application.prototype.show_notes = function() {
    var me = this;
        if (frappe.user.has_role('HR Notification')) {
            frappe.call({
                "method": "mosyr.api.show_expier_docs"
            });
        }
		if(frappe.boot.notes.length) {
			frappe.boot.notes.forEach(function(note) {
				if(!note.seen || note.notify_on_every_login) {
					var d = frappe.msgprint({message:note.content, title:note.title});
					d.keep_open = true;
					d.custom_onhide = function() {
						note.seen = true;

						// Mark note as read if the Notify On Every Login flag is not set
						if (!note.notify_on_every_login) {
							frappe.call({
								method: "frappe.desk.doctype.note.note.mark_as_seen",
								args: {
									note: note.name
								}
							});
						}

						// next note
						me.show_notes();

					};
				}
			});
		}
}