"""Generic notification helpers for Athru Service."""

from __future__ import annotations

import frappe


def notify_service_call_created(doc, method=None):
	"""Optional hook: send mail to assigned engineers when a Service Call is created."""
	recipients = []
	for row in doc.service_personnel or []:
		if row.user_id:
			recipients.append(row.user_id)
	if not recipients and doc.received_by:
		return
	if not recipients:
		return
	frappe.sendmail(
		recipients=recipients,
		subject=f"Service Call {doc.service_call_number or doc.name}",
		message=f"New Service Call for {doc.serial_no or ''}: {doc.complaint or ''}",
		reference_doctype=doc.doctype,
		reference_name=doc.name,
		now=False,
	)
