frappe.ui.form.on("Maintenance Visit", {
	refresh(frm) {
		if (frm.doc.custom_service_call && !frm.doc.custom_service_report) {
			frm.add_custom_button(__("Service Report"), () => {
				frappe.new_doc("Service Report", {
					service_call: frm.doc.custom_service_call,
					maintenance_visit: frm.doc.name,
					installed_equipment: frm.doc.custom_installed_equipment,
				});
			}, __("Create"));
		}
		if (frm.doc.custom_installed_equipment) {
			frm.add_custom_button(__("Checklist Response"), () => {
				frappe.new_doc("Checklist Response", {
					installed_equipment: frm.doc.custom_installed_equipment,
					service_call: frm.doc.custom_service_call,
					maintenance_visit: frm.doc.name,
				});
			}, __("Create"));
		}
	},
	custom_service_call(frm) {
		if (!frm.doc.custom_service_call) return;
		frappe.db.get_value("Service Call", frm.doc.custom_service_call, ["installed_equipment", "customer"]).then((r) => {
			if (r.message) {
				frm.set_value("custom_installed_equipment", r.message.installed_equipment);
				if (r.message.customer) frm.set_value("customer", r.message.customer);
			}
		});
	},
});
