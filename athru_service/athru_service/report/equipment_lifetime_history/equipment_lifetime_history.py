# Copyright (c) 2026, Athru and contributors
# For license information, please see license.txt

from __future__ import annotations

import frappe


def execute(filters=None):
	filters = filters or {}
	columns = [
		{"label": "Date", "fieldname": "event_date", "fieldtype": "Datetime", "width": 160},
		{"label": "Event Type", "fieldname": "event_type", "fieldtype": "Data", "width": 140},
		{"label": "Reference", "fieldname": "reference", "fieldtype": "Dynamic Link", "options": "reference_doctype", "width": 160},
		{"label": "Reference DocType", "fieldname": "reference_doctype", "fieldtype": "Data", "width": 140},
		{"label": "Summary", "fieldname": "summary", "fieldtype": "Data", "width": 320},
		{"label": "Serial No", "fieldname": "serial_no", "fieldtype": "Link", "options": "Serial No", "width": 140},
		{"label": "Installed Equipment", "fieldname": "installed_equipment", "fieldtype": "Link", "options": "Installed Equipment", "width": 160},
	]

	ie = filters.get("installed_equipment")
	serial_no = filters.get("serial_no")
	equipment_names = []
	if ie:
		equipment_names = [ie]
	elif serial_no:
		equipment_names = frappe.get_all(
			"Installed Equipment", filters={"serial_no": serial_no}, pluck="name"
		)
	else:
		equipment_names = frappe.get_all("Installed Equipment", pluck="name", limit_page_length=50)

	rows = []
	for name in equipment_names:
		ie_doc = frappe.db.get_value(
			"Installed Equipment", name, ["serial_no", "item_code", "customer"], as_dict=True
		) or {}
		for act in frappe.get_all(
			"Equipment Activity",
			filters={"installed_equipment": name},
			fields=["name", "activity_date", "activity_type", "description"],
		):
			rows.append(
				{
					"event_date": act.activity_date,
					"event_type": "Activity",
					"reference": act.name,
					"reference_doctype": "Equipment Activity",
					"summary": f"{act.activity_type}: {(act.description or '')[:120]}",
					"serial_no": ie_doc.get("serial_no"),
					"installed_equipment": name,
				}
			)
		for call in frappe.get_all(
			"Service Call",
			filters={"installed_equipment": name},
			fields=["name", "call_date", "service_call_number", "complaint", "status"],
		):
			rows.append(
				{
					"event_date": call.call_date,
					"event_type": "Service Call",
					"reference": call.name,
					"reference_doctype": "Service Call",
					"summary": f"{call.service_call_number or call.name} [{call.status}] {(call.complaint or '')[:100]}",
					"serial_no": ie_doc.get("serial_no"),
					"installed_equipment": name,
				}
			)
		for report in frappe.get_all(
			"Service Report",
			filters={"installed_equipment": name, "docstatus": 1},
			fields=["name", "report_datetime", "root_cause"],
		):
			rows.append(
				{
					"event_date": report.report_datetime,
					"event_type": "Service Report",
					"reference": report.name,
					"reference_doctype": "Service Report",
					"summary": (report.root_cause or report.name)[:160],
					"serial_no": ie_doc.get("serial_no"),
					"installed_equipment": name,
				}
			)

	rows.sort(key=lambda r: r.get("event_date") or "", reverse=True)
	return columns, rows
