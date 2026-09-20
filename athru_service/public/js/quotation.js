frappe.ui.form.on("Quotation", {
	refresh(frm) {
		frm.toggle_display(
			["custom_contract_type", "custom_installed_equipment", "custom_included_pm_visits", "custom_included_emergency_visits"],
			frm.doc.custom_is_service_contract
		);
	},
	custom_is_service_contract(frm) {
		frm.trigger("refresh");
	},
});
