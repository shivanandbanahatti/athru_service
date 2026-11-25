"""Replace the old 'Athru Service' workspace with the generic 'Service Management'.

The module ships the renamed workspace as JSON, but migrate does not delete the
old record, so an installed site would keep an orphan 'Athru Service' workspace
in the sidebar. Remove it here (idempotent).
"""

from __future__ import annotations

import frappe


def execute():
	old = "Athru Service"
	if frappe.db.exists("Workspace", old):
		frappe.delete_doc("Workspace", old, ignore_missing=True, force=True)
		frappe.clear_cache()
