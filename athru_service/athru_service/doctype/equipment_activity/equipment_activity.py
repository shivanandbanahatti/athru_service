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
		if not self.installed_equipment or not self.activity_type:
			return
		new_status = frappe.db.get_value(
			"Equipment Activity Type", self.activity_type, "updates_equipment_status"
		)
		if new_status:
			frappe.db.set_value(
				"Installed Equipment",
				self.installed_equipment,
				"status",
				new_status,
				update_modified=False,
			)
			if new_status == "Commissioned":
				from frappe.utils import getdate

				frappe.db.set_value(
					"Installed Equipment",
					self.installed_equipment,
					"commissioning_date",
					getdate(self.activity_date) if self.activity_date else None,
					update_modified=False,
				)

	def _mirror_key_attachments(self):
		if not self.installed_equipment or not self.attachment:
			return
		if self.activity_type == "User Manual Sent":
			frappe.db.set_value(
				"Installed Equipment",
				self.installed_equipment,
				"user_manual",
				self.attachment,
				update_modified=False,
			)
		elif self.activity_type == "Installation Acceptance":
			frappe.db.set_value(
				"Installed Equipment",
				self.installed_equipment,
				"installation_acceptance_certificate",
				self.attachment,
				update_modified=False,
			)


def after_insert(doc, method=None):
	doc.after_insert()


def on_update(doc, method=None):
	doc.on_update()
