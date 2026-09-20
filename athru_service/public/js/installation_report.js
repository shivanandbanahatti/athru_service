frappe.ui.form.on("Installation Report", {
	refresh(frm) {
		if (frm.doc.machine_installation) {
			frm.add_custom_button(__("Machine Hub"), () => {
				window.open(
					`/athru-service/machines/${encodeURIComponent(frm.doc.machine_installation)}`,
					"_blank"
				);
			});
		}
	},
	hd_ticket(frm) {
		if (!frm.doc.hd_ticket) return;
		frappe.db
			.get_value("HD Ticket", frm.doc.hd_ticket, ["custom_machine_installation", "custom_erp_customer"])
			.then((r) => {
				if (!r.message) return;
				frm.set_value("machine_installation", r.message.custom_machine_installation);
				if (r.message.custom_erp_customer) frm.set_value("customer", r.message.custom_erp_customer);
			});
	},
});
