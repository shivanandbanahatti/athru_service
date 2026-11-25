# Copyright (c) 2026, Athru and contributors
# For license information, please see license.txt

from __future__ import annotations

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import get_time, getdate, nowdate

# Workflow states map to a simple status for list views / reporting.
STATE_TO_STATUS = {
	"Pending": "Pending",
	"Approved": "Approved",
	"Rejected": "Rejected",
	"Cancelled": "Cancelled",
}


class LateEntryRequest(Document):
	def validate(self):
		self._sync_status()
		self._validate_times()

	def _sync_status(self):
		"""Keep the plain `status` field in step with the workflow state."""
		if self.workflow_state and self.workflow_state in STATE_TO_STATUS:
			self.status = STATE_TO_STATUS[self.workflow_state]
		elif not self.status:
			self.status = "Pending"
		if self.status in ("Approved", "Rejected") and not self.approver:
			self.approver = frappe.session.user

	def _validate_times(self):
		if self.expected_time and self.actual_time:
			if get_time(self.actual_time) < get_time(self.expected_time):
				frappe.throw(_("Actual Reporting Time cannot be earlier than the Expected Reporting Time."))

	def on_submit(self):
		# Submission corresponds to an approved request.
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
