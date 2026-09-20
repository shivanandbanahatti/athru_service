"""Delivery Note → Machine Installation + Installation HD Ticket."""

from __future__ import annotations

import frappe
from frappe.utils import nowdate


def on_submit(doc, method=None):
	if not getattr(doc, "custom_create_machine_installation", None):
		return
	for item in doc.items:
		if not item.serial_no:
			continue
		_ensure_machine_and_ticket(doc, item)


def _ensure_machine_and_ticket(dn, item):
	serials = [s.strip() for s in (item.serial_no or "").replace(",", "\n").split("\n") if s.strip()]
	created = []
	for serial in serials:
		mi_name = frappe.db.get_value("Machine Installation", {"serial_no": serial}, "name")
		if not mi_name:
			mi = frappe.get_doc(
				{
					"doctype": "Machine Installation",
					"company": dn.company,
					"customer": dn.customer,
					"item_code": item.item_code,
					"serial_no": serial,
					"delivery_note": dn.name,
					"sales_order": item.against_sales_order,
					"dispatch_date": dn.posting_date or nowdate(),
					"status": "Dispatched",
					"site_address": dn.shipping_address_name,
					"project": getattr(item, "project", None) or dn.get("project"),
				}
			)
			# installation included from SO?
			if item.against_sales_order:
				inst = frappe.db.get_value(
					"Sales Order", item.against_sales_order, "custom_installation_included"
				)
				if inst is not None:
					pass
			mi.insert(ignore_permissions=True)
			mi_name = mi.name
			frappe.get_doc(
				{
					"doctype": "Equipment Activity",
					"machine_installation": mi_name,
					"activity_type": "Dispatched",
					"activity_date": dn.posting_date or nowdate(),
					"description": f"Dispatched via Delivery Note {dn.name}",
				}
			).insert(ignore_permissions=True)

		create_ticket = getattr(dn, "custom_create_installation_ticket", None)
		if create_ticket is None:
			create_ticket = 1
		if create_ticket:
			# avoid duplicate open installation tickets
			existing = frappe.db.exists(
				"HD Ticket",
				{
					"custom_machine_installation": mi_name,
					"ticket_type": "Installation",
					"status": ["not in", ["Closed", "Resolved"]],
				},
			)
			if not existing and frappe.db.exists("DocType", "HD Ticket"):
				from athru_service.athru_service.utils.hd_ticket import create_installation_ticket

				engineers = [
					{"employee": r.employee, "role": r.role}
					for r in (dn.get("custom_installation_engineers") or [])
				]
				create_installation_ticket(mi_name, engineers=engineers)
		created.append(mi_name)
	return created


@frappe.whitelist()
def create_machine_installation_from_dn(delivery_note: str) -> list[str]:
	dn = frappe.get_doc("Delivery Note", delivery_note)
	dn.custom_create_machine_installation = 1
	created = []
	for item in dn.items:
		if not item.serial_no:
			continue
		result = _ensure_machine_and_ticket(dn, item)
		if result:
			created.extend(result)
	return created
