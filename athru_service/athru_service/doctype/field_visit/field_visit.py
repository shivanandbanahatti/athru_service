# Copyright (c) 2026, Athru and contributors
# For license information, please see license.txt

from __future__ import annotations

import frappe
from frappe import _
from frappe.model.document import Document

STATE_TO_STATUS = {
	"Pending": "Pending",
	"Approved": "Approved",
	"Rejected": "Rejected",
	"Cancelled": "Cancelled",
}


class FieldVisit(Document):
	def validate(self):
		if self.workflow_state and self.workflow_state in STATE_TO_STATUS:
			self.status = STATE_TO_STATUS[self.workflow_state]
		elif not self.status:
			self.status = "Pending"
		if self.status in ("Approved", "Rejected") and not self.approver:
			self.approver = frappe.session.user
		if self.party_type == "Customer":
			self.lead = None
		elif self.party_type == "Lead":
			self.customer = None
		if self.travel_start_datetime and self.travel_end_datetime:
			if self.travel_end_datetime < self.travel_start_datetime:
				frappe.throw(_("Travel End cannot be before Travel Start."))

	def on_submit(self):
		if self.status not in ("Approved", "Rejected"):
			self.db_set("status", "Approved")

	def on_cancel(self):
		self.db_set("status", "Cancelled")


def validate(doc, method=None):
	doc.validate()


def on_submit(doc, method=None):
	doc.on_submit()


def on_cancel(doc, method=None):
	doc.on_cancel()
