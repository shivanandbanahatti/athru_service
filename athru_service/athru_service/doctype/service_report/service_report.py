# Copyright (c) 2026, Athru and contributors
# For license information, please see license.txt

from __future__ import annotations

import frappe
from frappe.model.document import Document


class ServiceReport(Document):
	def on_submit(self):
		if self.service_call:
			frappe.db.set_value("Service Call", self.service_call, "service_report", self.name)
			if frappe.db.get_value("Service Call", self.service_call, "status") not in ("Closed", "Cancelled"):
				frappe.db.set_value("Service Call", self.service_call, "status", "Resolved")
		if self.promote_to_problem_record:
			from athru_service.api.knowledge import promote_from_service_report

			promote_from_service_report(self.name)

	def on_cancel(self):
		if self.service_call and frappe.db.get_value("Service Call", self.service_call, "service_report") == self.name:
			frappe.db.set_value("Service Call", self.service_call, "service_report", None)


def on_submit(doc, method=None):
	doc.on_submit()


def on_cancel(doc, method=None):
	doc.on_cancel()
