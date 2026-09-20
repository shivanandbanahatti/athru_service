"""Optional neutral demo seed for development sites."""

from __future__ import annotations

import json
from pathlib import Path

import frappe
from frappe.utils import add_days, now_datetime, nowdate


def load_demo_seed():
	"""Create Demo Customer / Item / Serial / Installed Equipment sample chain."""
	company = frappe.db.get_single_value("Global Defaults", "default_company") or frappe.db.get_value(
		"Company", {}, "name"
	)
	if not company:
		frappe.throw("Create a Company before loading demo seed")

	_ensure_demo_masters(company)
	_ensure_checklist_templates()
	frappe.msgprint("Athru Service demo seed loaded")


def _ensure_demo_masters(company: str):
	if not frappe.db.exists("Customer", "Demo Customer"):
		frappe.get_doc(
			{
				"doctype": "Customer",
				"customer_name": "Demo Customer",
				"customer_type": "Company",
				"customer_group": frappe.db.get_value("Customer Group", {}, "name") or "All Customer Groups",
				"territory": frappe.db.get_value("Territory", {}, "name") or "All Territories",
			}
		).insert(ignore_permissions=True)

	if not frappe.db.exists("Item", "SAMPLE-EQUIPMENT-MODEL"):
		item_group = (
			frappe.db.exists("Item Group", "All Item Groups")
			or frappe.db.get_value("Item Group", {}, "name")
		)
		frappe.get_doc(
			{
				"doctype": "Item",
				"item_code": "SAMPLE-EQUIPMENT-MODEL",
				"item_name": "Sample Equipment Model",
				"item_group": item_group,
				"stock_uom": "Nos",
				"is_stock_item": 1,
				"include_item_in_manufacturing": 0,
				"custom_is_serviceable_equipment": 1,
				"custom_product_family": "General Equipment",
			}
		).insert(ignore_permissions=True)

	serial = "DEMO-SN-0001"
	if not frappe.db.exists("Serial No", serial):
		frappe.get_doc(
			{
				"doctype": "Serial No",
				"serial_no": serial,
				"item_code": "SAMPLE-EQUIPMENT-MODEL",
				"company": company,
			}
		).insert(ignore_permissions=True)

	ie_name = frappe.db.get_value("Installed Equipment", {"serial_no": serial}, "name")
	if not ie_name:
		ie = frappe.get_doc(
			{
				"doctype": "Installed Equipment",
				"company": company,
				"customer": "Demo Customer",
				"item_code": "SAMPLE-EQUIPMENT-MODEL",
				"serial_no": serial,
				"dispatch_date": add_days(nowdate(), -20),
				"status": "Dispatched",
				"warranty_expiry_date": add_days(nowdate(), 345),
			}
		)
		ie.insert(ignore_permissions=True)
		ie_name = ie.name

		for idx, (atype, days_ago, desc) in enumerate(
			[
				("Dispatched", 20, "Dispatched from factory"),
				("Received by Customer", 18, "Customer confirmed receipt"),
				("User Manual Sent", 17, "User manual emailed"),
				("Installation Started", 10, "Team mobilized"),
				("Installation Progress", 9, "Positioning and anchoring"),
				("Installation Progress", 8, "Wiring completed"),
				("Installation Acceptance", 5, "Customer signed acceptance certificate"),
			]
		):
			frappe.get_doc(
				{
					"doctype": "Equipment Activity",
					"installed_equipment": ie_name,
					"activity_type": atype,
					"activity_date": add_days(now_datetime(), -days_ago),
					"description": desc,
				}
			).insert(ignore_permissions=True)

		call = frappe.get_doc(
			{
				"doctype": "Service Call",
				"installed_equipment": ie_name,
				"call_type": "Breakdown",
				"complaint": "Abnormal noise during operation",
				"complainant": "Demo Operator",
				"action_taken": "Inspected couplings; tightened fasteners",
				"resolution_summary": "Loose coupling bolts",
				"status": "Resolved",
			}
		)
		call.append("problem_codes", {"problem_code": "SYM-GEN-001"})
		call.append("problem_codes", {"problem_code": "RCA-GEN-001"})
		call.insert(ignore_permissions=True)

		report = frappe.get_doc(
			{
				"doctype": "Service Report",
				"service_call": call.name,
				"installed_equipment": ie_name,
				"problem_description": "Abnormal noise during operation",
				"root_cause": "Loose coupling bolts after transport",
				"corrective_action": "Torqued coupling bolts to specification",
				"service_type": "Warranty",
				"promote_to_problem_record": 1,
			}
		)
		report.append("problem_codes", {"problem_code": "SYM-GEN-001"})
		report.append("problem_codes", {"problem_code": "RCA-GEN-001"})
		report.insert(ignore_permissions=True)
		report.submit()


def _ensure_checklist_templates():
	path = Path(__file__).resolve().parents[1] / "fixtures" / "demo" / "checklist_templates.json"
	if not path.exists():
		return
	payload = json.loads(path.read_text(encoding="utf-8"))
	for tmpl in payload.get("checklist_templates", []):
		if frappe.db.exists("Checklist Template", tmpl["template_name"]):
			continue
		doc = frappe.get_doc(
			{
				"doctype": "Checklist Template",
				"template_name": tmpl["template_name"],
				"purpose": tmpl["purpose"],
				"version": tmpl.get("version") or "1.0",
				"is_active": 1,
				"items": tmpl["items"],
			}
		)
		doc.insert(ignore_permissions=True)
