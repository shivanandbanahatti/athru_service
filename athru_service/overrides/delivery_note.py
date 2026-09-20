"""Delivery Note hooks for Installed Equipment handoff."""

from __future__ import annotations

import frappe
from frappe.utils import nowdate


def on_submit(doc, method=None):
	# Optional auto-create is controlled by a custom field on DN if present
	if not getattr(doc, "custom_create_installed_equipment", None):
		return
	for item in doc.items:
		if not item.serial_no:
			continue
		_ensure_installed_equipment(doc, item)


def _ensure_installed_equipment(dn, item):
	existing = frappe.db.exists("Installed Equipment", {"serial_no": item.serial_no})
	if existing:
		return existing
	# serial_no on DN item may be a list string
	serials = [s.strip() for s in (item.serial_no or "").split("\n") if s.strip()]
	names = []
	for serial in serials:
		if frappe.db.exists("Installed Equipment", {"serial_no": serial}):
			continue
		ie = frappe.get_doc(
			{
				"doctype": "Installed Equipment",
				"company": dn.company,
				"customer": dn.customer,
				"item_code": item.item_code,
				"serial_no": serial,
				"delivery_note": dn.name,
				"sales_order": item.against_sales_order,
				"dispatch_date": dn.posting_date or nowdate(),
				"status": "Dispatched",
				"site_address": dn.shipping_address_name,
			}
		)
		ie.insert(ignore_permissions=True)
		frappe.get_doc(
			{
				"doctype": "Equipment Activity",
				"installed_equipment": ie.name,
				"activity_type": "Dispatched",
				"activity_date": dn.posting_date or nowdate(),
				"description": f"Dispatched via Delivery Note {dn.name}",
			}
		).insert(ignore_permissions=True)
		names.append(ie.name)
	return names


@frappe.whitelist()
def create_installed_equipment_from_dn(delivery_note: str) -> list[str]:
	dn = frappe.get_doc("Delivery Note", delivery_note)
	created = []
	for item in dn.items:
		if not item.serial_no:
			continue
		result = _ensure_installed_equipment(dn, item)
		if isinstance(result, list):
			created.extend(result)
		elif result:
			created.append(result)
	return created
