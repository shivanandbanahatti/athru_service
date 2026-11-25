# Copyright (c) 2026, Athru and contributors
# For license information, please see license.txt

from __future__ import annotations

import frappe
from frappe.model.document import Document


class CustomerFeedback(Document):
	def validate(self):
		if self.hd_ticket and not self.customer:
			self.customer = frappe.db.get_value("HD Ticket", self.hd_ticket, "custom_erp_customer")
