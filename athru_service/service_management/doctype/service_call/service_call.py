# Copyright (c) 2026, Athru and contributors
# For license information, please see license.txt

from __future__ import annotations

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import get_datetime, now_datetime


class ServiceCall(Document):
	def before_insert(self):
		self._assert_intake_allowed()
		if not self.service_call_number:
			self.service_call_number = make_service_call_number(self.call_date)
		# Use Service Call Number as document name
		self.name = self.service_call_number
		self._stamp_warranty_status()

	def validate(self):
		self._assert_intake_allowed()
		if not self.service_call_number:
			self.service_call_number = make_service_call_number(self.call_date)
		self._stamp_warranty_status()
		if self.status in ("Resolved", "Closed") and not self.resolved_on:
			self.resolved_on = now_datetime()

	def on_update(self):
		pass

	def _stamp_warranty_status(self):
		if not self.installed_equipment:
			return
		status = frappe.db.get_value("Installed Equipment", self.installed_equipment, "maintenance_status")
		self.warranty_status = status or ""

	def _assert_intake_allowed(self):
		settings = frappe.get_single("Athru Service Settings")
		if settings.call_intake_mode != "Central Desk Only":
			return
		role = settings.central_desk_role or "Service Desk Agent"
		if frappe.session.user == "Administrator":
			return
		if role not in frappe.get_roles():
			frappe.throw(_("Only users with role {0} may register Service Calls").format(role))


def before_insert(doc, method=None):
	doc.before_insert()


def validate(doc, method=None):
	doc.validate()


def on_update(doc, method=None):
	doc.on_update()


def make_service_call_number(call_date=None) -> str:
	"""Generate YYMMDD-## style Service Call Number (daily sequence)."""
	settings = frappe.get_single("Athru Service Settings")
	pattern = (settings.service_call_naming or "YYMMDD-##").strip()
	dt = get_datetime(call_date) if call_date else now_datetime()
	prefix = dt.strftime("%y%m%d")

	if "YYMMDD" in pattern.upper() or pattern == "YYMMDD-##":
		day_start = dt.replace(hour=0, minute=0, second=0, microsecond=0)
		day_end = dt.replace(hour=23, minute=59, second=59, microsecond=0)
		count = frappe.db.count(
			"Service Call",
			filters={"call_date": ["between", [day_start, day_end]]},
		)
		seq = count + 1
		while True:
			candidate = f"{prefix}-{seq:02d}"
			if not frappe.db.exists("Service Call", candidate):
				return candidate
			seq += 1

	return frappe.model.naming.make_autoname(pattern)


@frappe.whitelist()
def register_service_call(
	installed_equipment: str,
	complaint: str,
	call_type: str | None = None,
	complainant: str | None = None,
	complainant_phone: str | None = None,
	action_taken: str | None = None,
) -> str:
	"""Quick-register API used by desk dialog."""
	doc = frappe.get_doc(
		{
			"doctype": "Service Call",
			"installed_equipment": installed_equipment,
			"complaint": complaint,
			"call_type": call_type or "Breakdown",
			"complainant": complainant,
			"complainant_phone": complainant_phone,
			"action_taken": action_taken,
			"received_by": frappe.session.user,
			"call_date": now_datetime(),
			"status": "Open",
		}
	)
	doc.insert()
	return doc.name
