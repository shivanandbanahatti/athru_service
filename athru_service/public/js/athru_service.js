// Athru Service app include — Desk escape hatch helpers
frappe.provide("athru_service");

athru_service.open_spa = function (path) {
	const base = "/athru-service";
	window.open(path ? `${base}/#${path}` : base, "_blank");
};

athru_service.open_register_call = function () {
	// Deprecated Service Call intake — route to HD Ticket (Service Request)
	frappe.new_doc("HD Ticket");
};

athru_service.open_machine_hub = function (name) {
	if (!name) {
		frappe.set_route("List", "Machine Installation");
		return;
	}
	window.open(`/athru-service/machines/${encodeURIComponent(name)}`, "_blank");
};
