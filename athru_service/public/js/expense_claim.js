frappe.ui.form.on("Expense Claim", {
	refresh(frm) {
		if (frm.doc.custom_machine_installation) {
			frm.add_custom_button(__("Machine Hub"), () => {
				window.open(
					`/athru-service/machines/${encodeURIComponent(frm.doc.custom_machine_installation)}`,
					"_blank"
				);
			});
		}
		if (frm.doc.custom_maintenance_visit) {
			frm.add_custom_button(__("Visit Console"), () => {
				window.open(
					`/athru-service/visits/${encodeURIComponent(frm.doc.custom_maintenance_visit)}`,
					"_blank"
				);
			});
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
