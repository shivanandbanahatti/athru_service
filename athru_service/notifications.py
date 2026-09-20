"""Optional notifications for Athru Service."""

from __future__ import annotations

import frappe


def notify_service_request_created(doc, method=None):
	"""Optional: mail assigned engineers when an HD Ticket is created with personnel."""
	recipients = []
	for row in doc.get("custom_service_personnel") or []:
		if not row.employee:
			continue
		user = frappe.db.get_value("Employee", row.employee, "user_id")
		if user:
			recipients.append(user)
	if not recipients:
		return
	frappe.sendmail(
		recipients=recipients,
		subject=f"Service Request {doc.get('custom_service_request_number') or doc.name}",
		message=f"New service request for {doc.get('custom_serial_no') or ''}: {doc.subject or ''}",
		delayed=True,
		reference_doctype=doc.doctype,
		reference_name=doc.name,
	)
