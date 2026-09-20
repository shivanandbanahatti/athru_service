# Copyright (c) 2026, Athru and contributors
# For license information, please see license.txt

from __future__ import annotations

import frappe
from frappe.model.document import Document
from frappe.utils import now_datetime


class InstallationReport(Document):
	def on_submit(self):
		if self.maintenance_visit:
			frappe.db.set_value(
				"Maintenance Visit",
				self.maintenance_visit,
				"custom_installation_report",
				self.name,
			)
		if self.machine_installation:
			frappe.db.set_value(
				"Machine Installation",
				self.machine_installation,
				{
					"status": "Commissioned",
					"commissioning_date": self.report_date,
					"installation_acceptance_certificate": self.customer_signature,
				},
			)
		if self.hd_ticket:
			# Close installation request when report is accepted
			status_field = "status"
			if frappe.db.has_column("HD Ticket", "status"):
				frappe.db.set_value("HD Ticket", self.hd_ticket, status_field, "Closed")
		if not self.signed_on:
			self.db_set("signed_on", now_datetime())
		self.db_set("status", "Accepted")

	def on_cancel(self):
		if self.maintenance_visit:
			current = frappe.db.get_value(
				"Maintenance Visit", self.maintenance_visit, "custom_installation_report"
			)
			if current == self.name:
				frappe.db.set_value(
					"Maintenance Visit", self.maintenance_visit, "custom_installation_report", None
				)


def on_submit(doc, method=None):
	doc.on_submit()


def on_cancel(doc, method=None):
	doc.on_cancel()
