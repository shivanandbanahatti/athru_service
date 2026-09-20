"""Permission helpers for service personnel scoping."""

from __future__ import annotations

import frappe


def _is_service_manager() -> bool:
	roles = set(frappe.get_roles())
	return bool(roles & {"System Manager", "Administrator", "Service Manager", "Service Desk Agent"})


def get_permission_query_conditions_for_hd_ticket(user: str | None = None) -> str:
	if not user:
		user = frappe.session.user
	if user == "Administrator" or _is_service_manager():
		return ""
	employee = frappe.db.get_value("Employee", {"user_id": user}, "name")
	if not employee:
		return f"`tabHD Ticket`.owner = {frappe.db.escape(user)}"
	return (
		f"(`tabHD Ticket`.owner = {frappe.db.escape(user)} "
		f"or `tabHD Ticket`.name in ("
		f"select parent from `tabService Personnel` "
		f"where parenttype='HD Ticket' and parentfield='custom_service_personnel' "
		f"and employee={frappe.db.escape(employee)}"
		f"))"
	)


def has_permission_hd_ticket(doc, user=None, permission_type=None):
	if not user:
		user = frappe.session.user
	if user == "Administrator" or _is_service_manager():
		return True
	if getattr(doc, "owner", None) == user:
		return True
	employee = frappe.db.get_value("Employee", {"user_id": user}, "name")
	if not employee:
		return False
	return any(
		row.employee == employee for row in (doc.get("custom_service_personnel") or [])
	)


def get_permission_query_conditions_for_maintenance_visit(user: str | None = None) -> str:
	if not user:
		user = frappe.session.user
	if user == "Administrator" or _is_service_manager():
		return ""
	employee = frappe.db.get_value("Employee", {"user_id": user}, "name")
	if not employee:
		return f"`tabMaintenance Visit`.owner = {frappe.db.escape(user)}"
	return (
		f"(`tabMaintenance Visit`.owner = {frappe.db.escape(user)} "
		f"or `tabMaintenance Visit`.custom_hd_ticket in ("
		f"select parent from `tabService Personnel` "
		f"where parenttype='HD Ticket' and parentfield='custom_service_personnel' "
		f"and employee={frappe.db.escape(employee)}"
		f"))"
	)
