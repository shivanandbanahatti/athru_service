"""Mark Service Call as deprecated; prefer HD Ticket Service Requests."""

from __future__ import annotations

import frappe


def execute():
	if not frappe.db.exists("DocType", "Service Call"):
		return
	# Soft-deprecate: keep data, discourage new creates via description on DocType
	try:
		frappe.db.set_value(
			"DocType",
			"Service Call",
			{
				"description": "DEPRECATED — use HD Ticket (Service Request) via Athru Service SPA.",
			},
			update_modified=False,
		)
	except Exception:
		pass
	frappe.clear_cache(doctype="Service Call")
