# Copyright (c) 2026, Athru and contributors
# For license information, please see license.txt

from __future__ import annotations

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate, nowdate


class InstalledEquipment(Document):
	def validate(self):
		self.sync_serial_link()
		self.set_maintenance_status()

	def on_update(self):
		self.sync_serial_link()

	def sync_serial_link(self):
		if not self.serial_no:
			return
		if frappe.db.has_column("Serial No", "custom_installed_equipment"):
			frappe.db.set_value(
				"Serial No",
				self.serial_no,
				"custom_installed_equipment",
				self.name,
				update_modified=False,
			)
		if self.warranty_expiry_date and frappe.db.has_column("Serial No", "warranty_expiry_date"):
			frappe.db.set_value(
				"Serial No",
				self.serial_no,
				"warranty_expiry_date",
				self.warranty_expiry_date,
				update_modified=False,
			)

	def set_maintenance_status(self):
		today = getdate(nowdate())
		if self.warranty_expiry_date and getdate(self.warranty_expiry_date) >= today:
			self.under_warranty = 1
			self.maintenance_status = "Under Warranty"
			return
		if self.current_service_contract:
			end = frappe.db.get_value("Service Contract", self.current_service_contract, "end_date")
			if end and getdate(end) >= today:
				ctype = frappe.db.get_value("Service Contract", self.current_service_contract, "contract_type")
				self.under_warranty = 0
				self.maintenance_status = f"Under {ctype}" if ctype else "Under Contract"
				return
			self.under_warranty = 0
			self.maintenance_status = "Out of Contract"
			return
		self.under_warranty = 0
		self.maintenance_status = "Out of Warranty"


def validate(doc, method=None):
	doc.validate()


def on_update(doc, method=None):
	doc.on_update()


@frappe.whitelist()
def get_lifetime_history(installed_equipment: str) -> dict:
	if not installed_equipment:
		frappe.throw(_("Installed Equipment is required"))

	return {
		"activities": frappe.get_all(
			"Equipment Activity",
			filters={"installed_equipment": installed_equipment},
			fields=["name", "activity_date", "activity_type", "description", "attachment", "owner"],
			order_by="activity_date desc",
			limit_page_length=100,
		),
		"service_calls": frappe.get_all(
			"Service Call",
			filters={"installed_equipment": installed_equipment},
			fields=["name", "service_call_number", "call_date", "call_type", "status", "complaint"],
			order_by="call_date desc",
			limit_page_length=100,
		),
		"service_reports": frappe.get_all(
			"Service Report",
			filters={"installed_equipment": installed_equipment, "docstatus": 1},
			fields=["name", "report_datetime", "service_type", "root_cause"],
			order_by="report_datetime desc",
			limit_page_length=50,
		),
		"service_contracts": frappe.get_all(
			"Service Contract",
			filters={"installed_equipment": installed_equipment, "docstatus": 1},
			fields=["name", "contract_type", "start_date", "end_date", "status"],
			order_by="end_date desc",
		),
	}


def refresh_warranty_status():
	for name in frappe.get_all(
		"Installed Equipment",
		filters={
			"status": [
				"in",
				["Commissioned", "Active", "Dispatched", "Delivered", "Installation In Progress"],
			]
		},
		pluck="name",
	):
		doc = frappe.get_doc("Installed Equipment", name)
		doc.set_maintenance_status()
		frappe.db.set_value(
			"Installed Equipment",
			name,
			{
				"maintenance_status": doc.maintenance_status,
				"under_warranty": doc.under_warranty,
			},
			update_modified=False,
		)
