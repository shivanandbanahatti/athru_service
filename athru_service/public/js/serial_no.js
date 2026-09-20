frappe.ui.form.on("Serial No", {
	refresh(frm) {
		if (frm.doc.custom_machine_installation) {
			frm.add_custom_button(__("Machine Installation"), () => {
				frappe.set_route("Form", "Machine Installation", frm.doc.custom_machine_installation);
			});
			frm.add_custom_button(__("SPA Hub"), () => {
				window.open(
					`/athru-service/machines/${encodeURIComponent(frm.doc.custom_machine_installation)}`,
					"_blank"
				);
			});
		}
	},
});
