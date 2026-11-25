frappe.query_reports["Equipment Lifetime History"] = {
	filters: [
		{
			fieldname: "machine_installation",
			label: __("Machine Installation"),
			fieldtype: "Link",
			options: "Machine Installation",
		},
		{
			fieldname: "serial_no",
			label: __("Serial No"),
			fieldtype: "Link",
			options: "Serial No",
		},
	],
};
