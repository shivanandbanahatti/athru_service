# Copyright (c) 2026, Athru and contributors
# For license information, please see license.txt

"""Company-driven print helpers.

Print formats in this app must stay brand-neutral: they render the company
header (name, address, GSTIN, logo) from the ERPNext ``Company`` and
``Letter Head`` records of the document's own company, never from hardcoded
strings. These helpers are exposed to Jinja via the ``jinja.methods`` hook.
"""

from __future__ import annotations

import frappe
from frappe.utils import escape_html


def company_letter_head(company: str | None) -> str | None:
	"""Return the default Letter Head name for a company, if any."""
	if not company:
		return None
	lh = frappe.db.get_value("Letter Head", {"is_default": 1, "disabled": 0}, "name")
	return lh or None


def company_header_html(company: str | None) -> str:
	"""Build a generic, escaped company header block from master data.

	Prefer the company's default Letter Head content when available; otherwise
	assemble a simple header from Company name/address/GSTIN. No brand strings
	are embedded here — everything comes from the site's own records.
	"""
	if not company:
		return ""

	lh_name = company_letter_head(company)
	if lh_name:
		content = frappe.db.get_value("Letter Head", lh_name, "content")
		if content:
			return content

	data = frappe.db.get_value(
		"Company",
		company,
		["company_name", "tax_id", "phone_no", "email", "website"],
		as_dict=True,
	)
	if not data:
		return ""

	address = _primary_company_address(company)
	lines = [f'<div class="ath-print-company">']
	lines.append(f'<div class="ath-print-company-name">{escape_html(data.company_name or company)}</div>')
	if address:
		lines.append(f'<div class="ath-print-company-addr">{escape_html(address)}</div>')
	meta = []
	if data.tax_id:
		meta.append(f"GSTIN: {escape_html(data.tax_id)}")
	if data.phone_no:
		meta.append(escape_html(data.phone_no))
	if data.email:
		meta.append(escape_html(data.email))
	if data.website:
		meta.append(escape_html(data.website))
	if meta:
		lines.append(f'<div class="ath-print-company-meta">{" &nbsp;|&nbsp; ".join(meta)}</div>')
	lines.append("</div>")
	return "".join(lines)


def _primary_company_address(company: str) -> str | None:
	"""Best-effort single-line address for the company."""
	address_name = frappe.db.get_value(
		"Dynamic Link",
		{"link_doctype": "Company", "link_name": company, "parenttype": "Address"},
		"parent",
	)
	if not address_name:
		return None
	addr = frappe.db.get_value(
		"Address",
		address_name,
		["address_line1", "address_line2", "city", "state", "pincode", "country"],
		as_dict=True,
	)
	if not addr:
		return None
	parts = [
		addr.address_line1,
		addr.address_line2,
		addr.city,
		addr.state,
		addr.pincode,
		addr.country,
	]
	return ", ".join(p for p in parts if p)
