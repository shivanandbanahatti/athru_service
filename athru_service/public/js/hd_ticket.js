frappe.ui.form.on("HD Ticket", {
	refresh(frm) {
		frm.set_intro(__("Athru presents HD Ticket as a Service Request in the SPA."));
		if (frm.doc.custom_machine_installation) {
			frm.add_custom_button(__("Machine Hub"), () => {
				window.open(
					`/athru-service/machines/${encodeURIComponent(frm.doc.custom_machine_installation)}`,
					"_blank"
				);
			});
		}
		if (!frm.is_new()) {
			frm.add_custom_button(__("Maintenance Visit"), () => {
				frappe.call({
					method: "athru_service.api.spa.create_visit_from_ticket",
					args: { hd_ticket: frm.doc.name },
					freeze: true,
					callback(r) {
						if (r.message) frappe.set_route("Form", "Maintenance Visit", r.message);
					},
				});
			}, __("Create"));
			if (["Preventive", "Contract Visit", "PMC"].includes(frm.doc.ticket_type) ||
				["PMC", "AMC", "CAMC"].includes(frm.doc.custom_visit_category)) {
				frm.add_custom_button(__("Maintenance Schedule"), () => {
					frappe.call({
						method: "athru_service.api.spa.create_schedule_from_ticket",
						args: { hd_ticket: frm.doc.name },
						freeze: true,
						callback(r) {
							if (r.message) frappe.set_route("Form", "Maintenance Schedule", r.message);
						},
					});
				}, __("Create"));
			}
			frm.add_custom_button(__("Service Report"), () => {
				frappe.new_doc("Service Report", {
					hd_ticket: frm.doc.name,
					machine_installation: frm.doc.custom_machine_installation,
				});
			}, __("Create"));
		}
	},
	custom_machine_installation(frm) {
		if (!frm.doc.custom_machine_installation) return;
		frappe.db
			.get_value("Machine Installation", frm.doc.custom_machine_installation, [
				"serial_no",
				"item_code",
				"customer",
				"project",
				"current_service_contract",
				"maintenance_status",
			])
			.then((r) => {
				if (!r.message) return;
				frm.set_value("custom_serial_no", r.message.serial_no);
				frm.set_value("custom_item_code", r.message.item_code);
				frm.set_value("custom_erp_customer", r.message.customer);
				frm.set_value("custom_project", r.message.project);
				frm.set_value("custom_service_contract", r.message.current_service_contract);
				frm.set_value("custom_warranty_status", r.message.maintenance_status);
			});
	},
});
