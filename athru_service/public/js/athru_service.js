// Athru Service app include
frappe.provide("athru_service");

athru_service.open_register_call = function () {
	frappe.set_route("List", "Service Call");
};
