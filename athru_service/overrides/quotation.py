"""Quotation → Service Contract bridge."""

from __future__ import annotations

import frappe
from frappe.utils import add_years, getdate


def on_submit(doc, method=None):
	if not getattr(doc, "custom_is_service_contract", None):
		return
	ie = getattr(doc, "custom_installed_equipment", None)
	if not ie:
		return
	if frappe.db.exists("Service Contract", {"quotation": doc.name, "docstatus": ["<", 2]}):
		return
	start = getdate(doc.transaction_date)
	end = add_years(start, 1)
	contract = frappe.get_doc(
		{
			"doctype": "Service Contract",
			"company": doc.company,
			"customer": doc.party_name if doc.quotation_to == "Customer" else None,
			"installed_equipment": ie,
			"quotation": doc.name,
			"contract_type": getattr(doc, "custom_contract_type", None) or "AMC",
			"start_date": start,
			"end_date": end,
			"included_pm_visits": getattr(doc, "custom_included_pm_visits", None) or 0,
			"included_emergency_visits": getattr(doc, "custom_included_emergency_visits", None) or 0,
			"coverage_notes": doc.terms,
		}
	)
	# customer field is fetched; set explicitly if needed
	if not contract.customer:
		contract.customer = frappe.db.get_value("Installed Equipment", ie, "customer")
	contract.insert(ignore_permissions=True)
