frappe.ui.form.on("Maintenance Visit", {
	refresh(frm) {
		if (frm.doc.custom_hd_ticket) {
			frm.add_custom_button(__("Open Service Request"), () => {
				frappe.set_route("Form", "HD Ticket", frm.doc.custom_hd_ticket);
			});
			frm.add_custom_button(__("Visit Console (SPA)"), () => {
				window.open(`/athru-service/visits/${encodeURIComponent(frm.doc.name)}`, "_blank");
			});
		}
		if (frm.doc.custom_hd_ticket && !frm.doc.custom_service_report) {
			frm.add_custom_button(__("Service Report"), () => {
				frappe.new_doc("Service Report", {
					hd_ticket: frm.doc.custom_hd_ticket,
					maintenance_visit: frm.doc.name,
					machine_installation: frm.doc.custom_machine_installation,
				});
			}, __("Create"));
		}
		if (frm.doc.custom_visit_category === "Installation" && !frm.doc.custom_installation_report) {
			frm.add_custom_button(__("Installation Report"), () => {
				frappe.new_doc("Installation Report", {
					hd_ticket: frm.doc.custom_hd_ticket,
					maintenance_visit: frm.doc.name,
					machine_installation: frm.doc.custom_machine_installation,
				});
			}, __("Create"));
		}
		if (frm.doc.custom_machine_installation) {
			frm.add_custom_button(__("Checklist Response"), () => {
				frappe.new_doc("Checklist Response", {
					machine_installation: frm.doc.custom_machine_installation,
					hd_ticket: frm.doc.custom_hd_ticket,
					maintenance_visit: frm.doc.name,
				});
			}, __("Create"));
			frm.add_custom_button(__("Day Task"), () => {
				frappe.new_doc("Task", {
					custom_maintenance_visit: frm.doc.name,
					custom_hd_ticket: frm.doc.custom_hd_ticket,
					custom_machine_installation: frm.doc.custom_machine_installation,
					custom_work_date: frappe.datetime.get_today(),
				});
			}, __("Create"));
			frm.add_custom_button(__("Expense Claim"), () => {
				frappe.call({
					method: "athru_service.api.spa.create_expense_for_visit",
					args: { visit: frm.doc.name },
					callback(r) {
						if (r.message) frappe.set_route("Form", "Expense Claim", r.message);
					},
				});
			}, __("Create"));
		}
	},
	custom_hd_ticket(frm) {
		if (!frm.doc.custom_hd_ticket) return;
		frappe.db
			.get_value("HD Ticket", frm.doc.custom_hd_ticket, [
				"custom_machine_installation",
				"custom_erp_customer",
				"custom_visit_category",
			])
			.then((r) => {
				if (!r.message) return;
				if (r.message.custom_machine_installation) {
					frm.set_value("custom_machine_installation", r.message.custom_machine_installation);
				}
				if (r.message.custom_erp_customer) {
					frm.set_value("customer", r.message.custom_erp_customer);
				}
				if (r.message.custom_visit_category) {
					frm.set_value("custom_visit_category", r.message.custom_visit_category);
				}
			});
	},
});
