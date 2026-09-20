# Copyright (c) 2026, Athru and contributors
# For license information, please see license.txt

from __future__ import annotations

import frappe
from frappe.model.document import Document


class EquipmentActivity(Document):
	def after_insert(self):
		self._apply_status_update()
		self._mirror_key_attachments()

	def on_update(self):
		self._apply_status_update()
		self._mirror_key_attachments()

	def _apply_status_update(self):
		if not self.machine_installation or not self.activity_type:
			return
		new_status = frappe.db.get_value(
			"Equipment Activity Type", self.activity_type, "updates_equipment_status"
		)
		if new_status:
			values = {"status": new_status}
			if new_status == "Commissioned":
				from frappe.utils import getdate

				values["commissioning_date"] = getdate(self.activity_date) if self.activity_date else None
			frappe.db.set_value(
				"Machine Installation",
				self.machine_installation,
				values,
				update_modified=False,
			)

	def _mirror_key_attachments(self):
		if not self.machine_installation or not self.attachment:
			return
		if self.activity_type == "User Manual Sent":
			frappe.db.set_value(
				"Machine Installation",
				self.machine_installation,
				"user_manual",
				self.attachment,
				update_modified=False,
			)
		elif self.activity_type == "Installation Acceptance":
			frappe.db.set_value(
				"Machine Installation",
				self.machine_installation,
				"installation_acceptance_certificate",
				self.attachment,
				update_modified=False,
			)


def after_insert(doc, method=None):
	doc.after_insert()


def on_update(doc, method=None):
	doc.on_update()
