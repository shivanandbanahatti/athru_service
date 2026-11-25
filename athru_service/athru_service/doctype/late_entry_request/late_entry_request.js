// Copyright (c) 2026, Athru and contributors
// For license information, please see license.txt

frappe.ui.form.on("Late Entry Request", {
	refresh(frm) {
		const colors = {
			Pending: "orange",
			Approved: "green",
			Rejected: "red",
			Cancelled: "gray",
		};
		if (frm.doc.status) {
			frm.page.set_indicator(frm.doc.status, colors[frm.doc.status] || "blue");
		}
	},

	employee(frm) {
		if (!frm.doc.employee) {
			frm.set_value("employee_name", null);
			frm.set_value("company", null);
			frm.set_value("department", null);
		}
	},
});
