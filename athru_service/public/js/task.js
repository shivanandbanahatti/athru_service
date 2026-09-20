frappe.ui.form.on("Task", {
	refresh(frm) {
		if (!frm.doc.custom_work_date && !frm.is_new()) {
			frm.set_value("custom_work_date", frappe.datetime.get_today());
		}
	},
	custom_maintenance_visit(frm) {
		if (!frm.doc.custom_maintenance_visit) return;
		frappe.db
			.get_value("Maintenance Visit", frm.doc.custom_maintenance_visit, [
				"custom_hd_ticket",
				"custom_machine_installation",
			])
			.then((r) => {
				if (!r.message) return;
				frm.set_value("custom_hd_ticket", r.message.custom_hd_ticket);
				frm.set_value("custom_machine_installation", r.message.custom_machine_installation);
			});
	},
});
