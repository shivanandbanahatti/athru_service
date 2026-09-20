"""Maintenance Visit ↔ HD Ticket sync."""

from __future__ import annotations

import frappe


def on_submit(doc, method=None):
	if not doc.custom_hd_ticket:
		return
	frappe.db.set_value("HD Ticket", doc.custom_hd_ticket, "custom_latest_visit", doc.name)
	mi = doc.custom_machine_installation
	if mi:
		count = frappe.db.count(
			"Maintenance Visit", {"custom_machine_installation": mi, "docstatus": 1}
		)
		frappe.db.set_value(
			"HD Ticket", doc.custom_hd_ticket, "custom_total_previous_visits", count
		)


def on_cancel(doc, method=None):
	if not doc.custom_hd_ticket:
		return
	latest = frappe.db.get_value("HD Ticket", doc.custom_hd_ticket, "custom_latest_visit")
	if latest == doc.name:
		frappe.db.set_value("HD Ticket", doc.custom_hd_ticket, "custom_latest_visit", None)


def before_insert(doc, method=None):
	if doc.custom_hd_ticket and not doc.custom_machine_installation:
		mi = frappe.db.get_value(
			"HD Ticket", doc.custom_hd_ticket, "custom_machine_installation"
		)
		if mi:
			doc.custom_machine_installation = mi
	if doc.custom_hd_ticket and not doc.custom_visit_category:
		cat = frappe.db.get_value("HD Ticket", doc.custom_hd_ticket, "custom_visit_category")
		if cat:
			doc.custom_visit_category = cat
	# Copy personnel from ticket
	if doc.custom_hd_ticket and not doc.custom_service_personnel:
		ticket = frappe.get_doc("HD Ticket", doc.custom_hd_ticket)
		for row in ticket.get("custom_service_personnel") or []:
			doc.append(
				"custom_service_personnel",
				{"employee": row.employee, "role": row.role, "employee_name": row.employee_name},
			)
