"""Rename the Frappe module 'Athru Service' -> 'Service Management'.

The app now ships module files under service_management/ with
module == 'Service Management', so a fresh migrate re-files the doctypes.
On an already-installed site we must move any records still pointing at the
old module and delete the orphan Module Def. Idempotent.
"""

from __future__ import annotations

import frappe

OLD = "Athru Service"
NEW = "Service Management"

# Doctypes that carry a `module` field and may reference the old module.
MODULE_SCOPED = [
	"DocType",
	"Report",
	"Workspace",
	"Print Format",
	"Web Form",
	"Dashboard",
	"Dashboard Chart",
	"Number Card",
	"Notification",
	"Workflow",
	"Client Script",
	"Server Script",
]


def execute():
	if not frappe.db.exists("Module Def", OLD):
		return

	# Make sure the new module exists before repointing to it.
	if not frappe.db.exists("Module Def", NEW):
		frappe.get_doc(
			{"doctype": "Module Def", "module_name": NEW, "app_name": "athru_service"}
		).insert(ignore_permissions=True)

	for dt in MODULE_SCOPED:
		if not frappe.db.has_column(dt, "module"):
			continue
		for name in frappe.get_all(dt, filters={"module": OLD}, pluck="name"):
			try:
				frappe.db.set_value(dt, name, "module", NEW, update_modified=False)
			except Exception:
				frappe.log_error(f"rename_module: could not repoint {dt} {name}")

	# Remove the now-empty old module definition.
	try:
		frappe.delete_doc("Module Def", OLD, ignore_missing=True, force=True)
	except Exception:
		frappe.log_error("rename_module: could not delete old Module Def")

	frappe.clear_cache()
