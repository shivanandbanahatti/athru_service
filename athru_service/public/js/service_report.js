frappe.ui.form.on("Service Report", {
	refresh(frm) {
		if (frm.doc.docstatus === 1) {
			frm.add_custom_button(__("Promote to Problem Record"), () => {
				frappe.call({
					method: "athru_service.api.knowledge.promote_from_service_report",
					args: { service_report: frm.doc.name },
					callback(r) {
						if (r.message) frappe.set_route("Form", "Problem Record", r.message);
					},
				});
			});
		}
	},
	hd_ticket(frm) {
		if (!frm.doc.hd_ticket) return;
		frappe.db
			.get_value("HD Ticket", frm.doc.hd_ticket, [
				"custom_machine_installation",
				"custom_serial_no",
				"custom_item_code",
				"custom_erp_customer",
			])
			.then((r) => {
				if (!r.message) return;
				frm.set_value("machine_installation", r.message.custom_machine_installation);
				frm.set_value("serial_no", r.message.custom_serial_no);
				frm.set_value("item_code", r.message.custom_item_code);
				frm.set_value("customer", r.message.custom_erp_customer);
			});
	},
});
