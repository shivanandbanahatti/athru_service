"""Seed generic masters and roles (no OEM / customer brands)."""

from __future__ import annotations

import frappe

from athru_service.athru_service.utils.hd_ticket import ensure_ticket_types

ROLES = [
	"Service Manager",
	"Service Engineer",
	"Service Desk Agent",
	"Service Read Only",
]

ACTIVITY_TYPES = [
	("Dispatched", "Equipment left factory / warehouse", "Dispatched"),
	("Invoice Filed", "Commercial invoice or delivery document filed", None),
	("Received by Customer", "Customer confirmed receipt", "Delivered"),
	("Goods Inward", "Customer goods-inward / receiving note", "Delivered"),
	("Store Acceptance", "Optional store / warehouse acceptance", None),
	("User Manual Sent", "User manual shared with customer", None),
	("Installation Started", "On-site installation began", "Installation In Progress"),
	("Installation Progress", "Day-wise installation update", "Installation In Progress"),
	("Installation Completed", "Installation work finished", None),
	("Installation Acceptance", "Customer signed installation acceptance certificate", "Commissioned"),
	("Other", "Miscellaneous activity", None),
]

PROBLEM_CODE_SEEDS = [
	("SYM-GEN-001", "Abnormal Noise", "Symptom", "noise vibration"),
	("SYM-GEN-002", "No Power", "Symptom", "power boot"),
	("SYM-GEN-003", "Overheating", "Symptom", "temperature thermal"),
	("FLR-GEN-001", "Sensor Fault", "Failure", "sensor"),
	("FLR-GEN-002", "Drive Fault", "Failure", "motor drive"),
	("RCA-GEN-001", "Loose Connection", "Root Cause", "wiring connector"),
	("RCA-GEN-002", "Worn Consumable", "Root Cause", "wear consumable"),
	("RES-GEN-001", "Replaced Part", "Resolution", "replace spare"),
	("RES-GEN-002", "Adjusted Setting", "Resolution", "calibrate adjust"),
]


def ensure_defaults():
	_ensure_roles()
	_ensure_settings()
	_ensure_activity_types()
	_ensure_problem_codes()
	ensure_ticket_types()


def _ensure_roles():
	for role in ROLES:
		if not frappe.db.exists("Role", role):
			doc = frappe.get_doc({"doctype": "Role", "role_name": role, "desk_access": 1})
			doc.insert(ignore_permissions=True)


def _ensure_settings():
	settings = frappe.get_single("Athru Service Settings")
	dirty = False
	if not settings.call_intake_mode:
		settings.call_intake_mode = "Any Service User"
		dirty = True
	if not settings.service_call_naming:
		settings.service_call_naming = "YYMMDD-##"
		dirty = True
	if settings.renewal_lead_days is None:
		settings.renewal_lead_days = 30
		dirty = True
	if dirty:
		settings.save(ignore_permissions=True)


def _ensure_activity_types():
	for name, description, status in ACTIVITY_TYPES:
		if frappe.db.exists("Equipment Activity Type", name):
			continue
		frappe.get_doc(
			{
				"doctype": "Equipment Activity Type",
				"activity_type": name,
				"description": description,
				"is_active": 1,
				"updates_equipment_status": status,
			}
		).insert(ignore_permissions=True)


def _ensure_problem_codes():
	for code, title, category, keywords in PROBLEM_CODE_SEEDS:
		if frappe.db.exists("Problem Code", code):
			continue
		frappe.get_doc(
			{
				"doctype": "Problem Code",
				"code": code,
				"title": title,
				"category": category,
				"keywords": keywords,
				"is_active": 1,
			}
		).insert(ignore_permissions=True)
