"""Expense Claim validation against visit engineers."""

from __future__ import annotations

import frappe
from frappe import _


def validate(doc, method=None):
	settings = frappe.get_single("Athru Service Settings")
	# Soft rule: if visit set, stamp ticket/machine
	if doc.custom_maintenance_visit:
		visit = frappe.db.get_value(
			"Maintenance Visit",
			doc.custom_maintenance_visit,
			["custom_hd_ticket", "custom_machine_installation"],
			as_dict=True,
		)
		if visit:
			if not doc.custom_hd_ticket:
				doc.custom_hd_ticket = visit.custom_hd_ticket
			if not doc.custom_machine_installation:
				doc.custom_machine_installation = visit.custom_machine_installation

	if getattr(settings, "call_intake_mode", None) and doc.custom_maintenance_visit and doc.employee:
		# Optional: warn if employee not on visit personnel
		personnel = frappe.get_all(
			"Service Personnel",
			filters={
				"parent": doc.custom_maintenance_visit,
				"parenttype": "Maintenance Visit",
				"parentfield": "custom_service_personnel",
			},
			pluck="employee",
		)
		if personnel and doc.employee not in personnel:
			frappe.msgprint(
				_("Employee {0} is not listed on Maintenance Visit personnel").format(doc.employee),
				indicator="orange",
				alert=True,
			)
