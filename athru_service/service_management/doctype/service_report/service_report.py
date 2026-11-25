# Copyright (c) 2026, Athru and contributors
# For license information, please see license.txt

from __future__ import annotations

import frappe
from frappe.model.document import Document


class ServiceReport(Document):
	def on_submit(self):
		if self.maintenance_visit:
			frappe.db.set_value(
				"Maintenance Visit", self.maintenance_visit, "custom_service_report", self.name
			)
		if self.hd_ticket and frappe.db.exists("DocType", "HD Ticket"):
			if frappe.db.has_column("HD Ticket", "status"):
				frappe.db.set_value("HD Ticket", self.hd_ticket, "status", "Resolved")
		if self.promote_to_problem_record:
			from athru_service.api.knowledge import promote_from_service_report

			promote_from_service_report(self.name)

	def on_cancel(self):
		if self.maintenance_visit:
			current = frappe.db.get_value(
				"Maintenance Visit", self.maintenance_visit, "custom_service_report"
			)
			if current == self.name:
				frappe.db.set_value(
					"Maintenance Visit", self.maintenance_visit, "custom_service_report", None
				)


def on_submit(doc, method=None):
	doc.on_submit()


def on_cancel(doc, method=None):
	doc.on_cancel()
