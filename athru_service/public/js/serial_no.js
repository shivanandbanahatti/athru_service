frappe.ui.form.on("Serial No", {
	refresh(frm) {
		if (frm.doc.custom_installed_equipment) {
			frm.add_custom_button(__("Installed Equipment"), () => {
				frappe.set_route("Form", "Installed Equipment", frm.doc.custom_installed_equipment);
			});
		}
	},
});
