frappe.ui.form.on("Delivery Note", {
	refresh(frm) {
		if (frm.doc.docstatus === 1) {
			frm.add_custom_button(__("Create Machine Installation"), () => {
				frappe.call({
					method: "athru_service.overrides.delivery_note.create_machine_installation_from_dn",
					args: { delivery_note: frm.doc.name },
					freeze: true,
					callback(r) {
						const names = r.message || [];
						if (!names.length) {
							frappe.msgprint(__("No Machine Installation created (check serialised items)."));
							return;
						}
						frappe.msgprint(__("Created: {0}", [names.join(", ")]));
					},
				});
			}, __("Create"));
		}
	},
});
