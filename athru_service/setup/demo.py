"""Demo seed — brand-neutral sample chain (Machine Installation + HD Ticket)."""

from __future__ import annotations

import frappe
from frappe.utils import nowdate


def load_demo_seed():
	"""Create Demo Customer / Item / Serial / Machine Installation sample chain."""
	company = frappe.defaults.get_global_default("company") or frappe.db.get_single_value(
		"Global Defaults", "default_company"
	)
	if not company:
		frappe.throw("Set a default Company before loading demo seed")

	customer = "Demo Equipment Customer"
	if not frappe.db.exists("Customer", customer):
		frappe.get_doc(
			{"doctype": "Customer", "customer_name": customer, "customer_type": "Company"}
		).insert(ignore_permissions=True)

	item = "DEMO-EQ-001"
	if not frappe.db.exists("Item", item):
		frappe.get_doc(
			{
				"doctype": "Item",
				"item_code": item,
				"item_name": "Demo Serviceable Equipment",
				"item_group": "Products",
				"stock_uom": "Nos",
				"is_stock_item": 1,
				"has_serial_no": 1,
				"custom_is_serviceable_equipment": 1,
			}
		).insert(ignore_permissions=True)

	serial = "DEMO-SN-001"
	if not frappe.db.exists("Serial No", serial):
		frappe.get_doc(
			{
				"doctype": "Serial No",
				"serial_no": serial,
				"item_code": item,
				"company": company,
			}
		).insert(ignore_permissions=True)

	mi_name = frappe.db.get_value("Machine Installation", {"serial_no": serial}, "name")
	if not mi_name:
		mi = frappe.get_doc(
			{
				"doctype": "Machine Installation",
				"company": company,
				"customer": customer,
				"item_code": item,
				"serial_no": serial,
				"status": "Commissioned",
				"dispatch_date": nowdate(),
				"commissioning_date": nowdate(),
			}
		).insert(ignore_permissions=True)
		mi_name = mi.name
		frappe.get_doc(
			{
				"doctype": "Equipment Activity",
				"machine_installation": mi_name,
				"activity_type": "Installation Acceptance",
				"activity_date": nowdate(),
				"description": "Demo commissioning",
			}
		).insert(ignore_permissions=True)

	if frappe.db.exists("DocType", "HD Ticket"):
		from athru_service.athru_service.utils.hd_ticket import create_installation_ticket

		existing = frappe.db.exists(
			"HD Ticket", {"custom_machine_installation": mi_name, "ticket_type": "Breakdown"}
		)
		if not existing:
			ticket_name = create_installation_ticket(
				mi_name, subject=f"Demo support — {serial}"
			)
			frappe.db.set_value("HD Ticket", ticket_name, "ticket_type", "Breakdown")

	return {"machine_installation": mi_name, "serial_no": serial, "customer": customer}
