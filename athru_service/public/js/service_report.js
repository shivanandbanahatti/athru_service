frappe.ui.form.on("Service Report", {
	refresh(frm) {
		if (frm.doc.docstatus === 1) {
			frm.add_custom_button(__("Promote to Problem Record"), () => {
				frappe.call({
					method: "athru_service.api.knowledge.promote_from_service_report",
					args: { service_report: frm.doc.name },
					callback(r) {
						frappe.set_route("Form", "Problem Record", r.message);
					},
				});
			});
		}
	},
});
