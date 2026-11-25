# Copyright (c) 2026, Athru and contributors
# For license information, please see license.txt

from __future__ import annotations

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import nowdate


class CorrectiveActionReport(Document):
	def validate(self):
		if self.status == "Closed" and not self.closed_on:
			self.closed_on = nowdate()
		if self.status != "Closed":
			self.closed_on = None

	def on_submit(self):
		if self.status == "Open":
			frappe.throw(_("Set a status beyond 'Open' before submitting."))


def validate(doc, method=None):
	doc.validate()


def on_submit(doc, method=None):
	doc.on_submit()
