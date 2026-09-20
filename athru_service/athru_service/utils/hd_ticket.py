"""HD Ticket (Service Request) helpers for Athru Service."""

from __future__ import annotations

import frappe
from frappe import _
from frappe.utils import get_datetime, now_datetime


TICKET_TYPES = [
	"Installation",
	"Breakdown",
	"Preventive",
	"Contract Visit",
	"Billable",
	"Parts",
	"Advisory",
	"Other",
]


def ensure_ticket_types():
	if not frappe.db.exists("DocType", "HD Ticket Type"):
		return
	for name in TICKET_TYPES:
		if frappe.db.exists("HD Ticket Type", name):
			continue
		try:
			frappe.get_doc({"doctype": "HD Ticket Type", "name": name}).insert(ignore_permissions=True)
		except Exception:
			# Some Helpdesk versions use different field layout
			doc = frappe.new_doc("HD Ticket Type")
			doc.name = name
			if hasattr(doc, "description"):
				doc.description = name
			doc.insert(ignore_permissions=True)


def make_service_request_number(when=None) -> str:
	dt = get_datetime(when) if when else now_datetime()
	prefix = dt.strftime("%y%m%d")
	day_start = dt.replace(hour=0, minute=0, second=0, microsecond=0)
	day_end = dt.replace(hour=23, minute=59, second=59, microsecond=0)
	count = frappe.db.count(
		"HD Ticket",
		filters={"creation": ["between", [day_start, day_end]]},
	)
	seq = count + 1
	while True:
		candidate = f"{prefix}-{seq:02d}"
		exists = frappe.db.exists(
			"HD Ticket", {"custom_service_request_number": candidate}
		)
		if not exists:
			return candidate
		seq += 1


def before_insert(doc, method=None):
	if not doc.get("custom_service_request_number"):
		doc.custom_service_request_number = make_service_request_number()
	_stamp_previous_visits(doc)
	_stamp_warranty(doc)


def validate(doc, method=None):
	if not doc.get("custom_service_request_number"):
		doc.custom_service_request_number = make_service_request_number(doc.creation)
	_stamp_previous_visits(doc)
	_stamp_warranty(doc)


def on_update(doc, method=None):
	pass


def _stamp_previous_visits(doc):
	mi = doc.get("custom_machine_installation")
	if not mi:
		return
	doc.custom_total_previous_visits = frappe.db.count(
		"Maintenance Visit", {"custom_machine_installation": mi, "docstatus": ["<", 2]}
	)


def _stamp_warranty(doc):
	mi = doc.get("custom_machine_installation")
	if not mi:
		return
	status = frappe.db.get_value("Machine Installation", mi, "maintenance_status")
	doc.custom_warranty_status = status or ""


@frappe.whitelist()
def create_installation_ticket(
	machine_installation: str,
	subject: str | None = None,
	engineers: list | str | None = None,
) -> str:
	"""Create HD Ticket type Installation linked to Machine Installation."""
	if not frappe.db.exists("DocType", "HD Ticket"):
		frappe.throw(_("Helpdesk (HD Ticket) is required. Install the helpdesk app."))

	mi = frappe.get_doc("Machine Installation", machine_installation)
	if isinstance(engineers, str):
		import json

		engineers = json.loads(engineers) if engineers else []

	ensure_ticket_types()
	ticket = frappe.new_doc("HD Ticket")
	ticket.subject = subject or f"Installation — {mi.serial_no or mi.name}"
	if hasattr(ticket, "ticket_type"):
		ticket.ticket_type = "Installation"
	ticket.description = f"Installation service request for {mi.item_code} / {mi.serial_no}"
	ticket.custom_machine_installation = mi.name
	ticket.custom_visit_category = "Installation"
	ticket.custom_service_request_number = make_service_request_number()
	for row in engineers or []:
		ticket.append(
			"custom_service_personnel",
			{"employee": row.get("employee"), "role": row.get("role") or "Engineer"},
		)
	# Customer sync: set if field exists
	if mi.customer and frappe.db.has_column("HD Ticket", "customer"):
		# Helpdesk may use HD Customer link; set description context only if needed
		pass
	ticket.insert(ignore_permissions=True)
	return ticket.name
