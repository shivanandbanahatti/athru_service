frappe.query_reports["Equipment Lifetime History"] = {
	filters: [
		{
			fieldname: "installed_equipment",
			label: __("Installed Equipment"),
			fieldtype: "Link",
			options: "Installed Equipment",
		},
		{
			fieldname: "serial_no",
			label: __("Serial No"),
			fieldtype: "Link",
			options: "Serial No",
		},
	],
};
