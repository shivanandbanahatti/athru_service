# Copyright (c) 2026, Athru and contributors

import frappe


def execute(filters=None):
	filters = filters or {}
	columns = [
		{"label": "Event Type", "fieldname": "event_type", "fieldtype": "Data", "width": 140},
		{"label": "Date", "fieldname": "event_date", "fieldtype": "Datetime", "width": 160},
		{"label": "Reference", "fieldname": "reference", "fieldtype": "Dynamic Link", "options": "reference_doctype", "width": 140},
		{"label": "Summary", "fieldname": "summary", "fieldtype": "Data", "width": 320},
		{"label": "Machine Installation", "fieldname": "machine_installation", "fieldtype": "Link", "options": "Machine Installation", "width": 160},
	]
	data = []
	mi = filters.get("machine_installation")
	serial_no = filters.get("serial_no")
	equipment_names = []
	if mi:
		equipment_names = [mi]
	elif serial_no:
		equipment_names = frappe.get_all(
			"Machine Installation", filters={"serial_no": serial_no}, pluck="name"
		)
	else:
		equipment_names = frappe.get_all("Machine Installation", pluck="name", limit_page_length=50)

	for name in equipment_names:
		for a in frappe.get_all(
			"Equipment Activity",
			filters={"machine_installation": name},
			fields=["name", "activity_date", "activity_type", "description"],
			order_by="activity_date desc",
		):
			data.append(
				{
					"event_type": "Activity",
					"event_date": a.activity_date,
					"reference_doctype": "Equipment Activity",
					"reference": a.name,
					"summary": f"{a.activity_type}: {(a.description or '')[:100]}",
					"machine_installation": name,
				}
			)
		if frappe.db.exists("DocType", "HD Ticket"):
			for t in frappe.get_all(
				"HD Ticket",
				filters={"custom_machine_installation": name},
				fields=["name", "creation", "subject", "status", "custom_service_request_number"],
				order_by="creation desc",
			):
				data.append(
					{
						"event_type": "Service Request",
						"event_date": t.creation,
						"reference_doctype": "HD Ticket",
						"reference": t.name,
						"summary": f"{t.custom_service_request_number or t.name} [{t.status}] {(t.subject or '')[:100]}",
						"machine_installation": name,
					}
				)
		for r in frappe.get_all(
			"Service Report",
			filters={"machine_installation": name, "docstatus": 1},
			fields=["name", "report_datetime", "root_cause"],
			order_by="report_datetime desc",
		):
			data.append(
				{
					"event_type": "Service Report",
					"event_date": r.report_datetime,
					"reference_doctype": "Service Report",
					"reference": r.name,
					"summary": (r.root_cause or r.name or "")[:120],
					"machine_installation": name,
				}
			)
	data.sort(key=lambda row: str(row.get("event_date") or ""), reverse=True)
	return columns, data
