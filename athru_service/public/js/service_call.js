// Deprecated: Service Call replaced by HD Ticket (Service Request)
frappe.ui.form.on("Service Call", {
	onload(frm) {
		frappe.msgprint({
			title: __("Deprecated"),
			message: __(
				"Service Call is deprecated. Use HD Ticket (Service Request) via the Service Console or Desk."
			),
			indicator: "orange",
		});
	},
	refresh(frm) {
		frm.add_custom_button(__("Open Service Console"), () => {
			window.open("/athru-service", "_blank");
		});
		frm.add_custom_button(__("New HD Ticket"), () => {
			frappe.new_doc("HD Ticket");
		});
	},
});
