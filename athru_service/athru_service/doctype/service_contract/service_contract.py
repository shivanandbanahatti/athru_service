# Copyright (c) 2026, Athru and contributors
# For license information, please see license.txt

from __future__ import annotations

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import add_days, getdate, nowdate


class ServiceContract(Document):
	def validate(self):
		if self.start_date and self.end_date and getdate(self.start_date) > getdate(self.end_date):
			frappe.throw(_("End Date cannot be before Start Date"))
		if self.docstatus == 0:
			self.status = "Draft"

	def on_submit(self):
		self.db_set("status", "Active")
		if self.installed_equipment:
			frappe.db.set_value(
				"Installed Equipment",
				self.installed_equipment,
				"current_service_contract",
				self.name,
			)
			# Refresh maintenance status
			ie = frappe.get_doc("Installed Equipment", self.installed_equipment)
			ie.set_maintenance_status()
			frappe.db.set_value(
				"Installed Equipment",
				self.installed_equipment,
				{
					"maintenance_status": ie.maintenance_status,
					"under_warranty": ie.under_warranty,
				},
				update_modified=False,
			)
		self._sync_serial_amc()

	def on_cancel(self):
		self.db_set("status", "Cancelled")
		if self.installed_equipment:
			current = frappe.db.get_value(
				"Installed Equipment", self.installed_equipment, "current_service_contract"
			)
			if current == self.name:
				frappe.db.set_value(
					"Installed Equipment",
					self.installed_equipment,
					"current_service_contract",
					None,
				)

	def _sync_serial_amc(self):
		if not self.serial_no:
			return
		if frappe.db.has_column("Serial No", "amc_expiry_date"):
			frappe.db.set_value("Serial No", self.serial_no, "amc_expiry_date", self.end_date, update_modified=False)


def validate(doc, method=None):
	doc.validate()


def on_submit(doc, method=None):
	doc.on_submit()


def on_cancel(doc, method=None):
	doc.on_cancel()


def create_renewal_followups():
	"""Daily: open Contract Renewal Followup N days before expiry."""
	settings = frappe.get_single("Athru Service Settings")
	lead = settings.renewal_lead_days or 30
	target = add_days(nowdate(), lead)
	contracts = frappe.get_all(
		"Service Contract",
		filters={"docstatus": 1, "status": "Active", "end_date": target},
		fields=["name", "installed_equipment", "customer", "end_date"],
	)
	for row in contracts:
		exists = frappe.db.exists(
			"Contract Renewal Followup",
			{"service_contract": row.name, "status": ["in", ["Open", "Contacted"]]},
		)
		if exists:
			continue
		frappe.get_doc(
			{
				"doctype": "Contract Renewal Followup",
				"service_contract": row.name,
				"installed_equipment": row.installed_equipment,
				"customer": row.customer,
				"contract_end_date": row.end_date,
				"followup_date": nowdate(),
				"status": "Open",
			}
		).insert(ignore_permissions=True)

	# Mark expired
	frappe.db.sql(
		"""
		update `tabService Contract`
		set status='Expired'
		where docstatus=1 and status='Active' and end_date < %s
		""",
		(nowdate(),),
	)
