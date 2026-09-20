"""Generate core Athru Service DocTypes."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "athru_service" / "athru_service" / "doctype"


def field(**kwargs):
	return kwargs


def write_doctype(name: str, meta: dict, fields: list):
	slug = name.lower().replace(" ", "_")
	folder = ROOT / slug
	folder.mkdir(parents=True, exist_ok=True)
	doc = {
		"actions": [],
		"allow_rename": meta.get("allow_rename", 1),
		"creation": "2026-09-20 12:00:00.000000",
		"doctype": "DocType",
		"engine": "InnoDB",
		"field_order": [f["fieldname"] for f in fields],
		"fields": fields,
		"index_web_pages_for_search": 1,
		"is_submittable": meta.get("is_submittable", 0),
		"issingle": meta.get("issingle", 0),
		"istable": meta.get("istable", 0),
		"links": meta.get("links", []),
		"modified": "2026-09-20 12:00:00.000000",
		"modified_by": "Administrator",
		"module": "Athru Service",
		"name": name,
		"owner": "Administrator",
		"permissions": meta.get(
			"permissions",
			[
				{
					"role": "System Manager",
					"read": 1,
					"write": 1,
					"create": 1,
					"delete": 1,
					"submit": meta.get("is_submittable", 0),
					"cancel": meta.get("is_submittable", 0),
					"amend": meta.get("is_submittable", 0),
				},
				{
					"role": "Service Manager",
					"read": 1,
					"write": 1,
					"create": 1,
					"delete": 1,
					"submit": meta.get("is_submittable", 0),
					"cancel": meta.get("is_submittable", 0),
					"amend": meta.get("is_submittable", 0),
				},
				{
					"role": "Service Desk Agent",
					"read": 1,
					"write": 1,
					"create": 1,
					"submit": meta.get("is_submittable", 0),
				},
				{
					"role": "Service Engineer",
					"read": 1,
					"write": 1,
					"create": 1,
					"submit": meta.get("is_submittable", 0),
				},
				{"role": "Service Read Only", "read": 1},
			],
		),
		"sort_field": "modified",
		"sort_order": "DESC",
		"states": [],
		"track_changes": 1,
	}
	for key in ("autoname", "naming_rule", "title_field", "search_fields"):
		if meta.get(key):
			doc[key] = meta[key]
	(folder / f"{slug}.json").write_text(json.dumps(doc, indent=1) + "\n", encoding="utf-8")
	class_name = "".join(p.title() for p in slug.split("_"))
	(folder / f"{slug}.py").write_text(
		f'# Copyright (c) 2026, Athru and contributors\n# For license information, please see license.txt\n\n'
		f'from frappe.model.document import Document\n\n\nclass {class_name}(Document):\n\tpass\n',
		encoding="utf-8",
	)
	(folder / f"{slug}.js").write_text(
		f'frappe.ui.form.on("{name}", {{\n\trefresh(frm) {{}}\n}});\n',
		encoding="utf-8",
	)
	(folder / "__init__.py").write_text("", encoding="utf-8")
	print("wrote", name)


def main():
	write_doctype(
		"Installed Equipment",
		{
			"autoname": "naming_series:",
			"naming_rule": 'By "Naming Series" field',
			"title_field": "serial_no",
			"search_fields": "serial_no,item_code,customer,project,status",
			"links": [
				{"link_doctype": "Equipment Activity", "link_fieldname": "installed_equipment"},
				{"link_doctype": "Service Call", "link_fieldname": "installed_equipment"},
				{"link_doctype": "Service Report", "link_fieldname": "installed_equipment"},
				{"link_doctype": "Service Contract", "link_fieldname": "installed_equipment"},
				{"link_doctype": "Problem Record", "link_fieldname": "installed_equipment"},
				{"link_doctype": "Checklist Response", "link_fieldname": "installed_equipment"},
			],
		},
		[
			field(fieldname="naming_series", fieldtype="Select", label="Series", options="IE-.YYYY.-.#####", default="IE-.YYYY.-.#####", reqd=1),
			field(fieldname="status", fieldtype="Select", label="Status", options="Draft\nDispatched\nDelivered\nInstallation In Progress\nCommissioned\nActive\nDecommissioned\nTransferred", default="Draft", reqd=1, in_list_view=1, in_standard_filter=1),
			field(fieldname="column_break_ie_1", fieldtype="Column Break"),
			field(fieldname="company", fieldtype="Link", label="Company", options="Company", reqd=1),
			field(fieldname="dispatch_date", fieldtype="Date", label="Dispatch Date"),
			field(fieldname="commissioning_date", fieldtype="Date", label="Commissioning Date"),
			field(fieldname="customer_section", fieldtype="Section Break", label="Customer & Site"),
			field(fieldname="customer", fieldtype="Link", label="Customer", options="Customer", reqd=1, in_list_view=1, in_standard_filter=1),
			field(fieldname="customer_name", fieldtype="Data", label="Customer Name", fetch_from="customer.customer_name", read_only=1),
			field(fieldname="column_break_ie_2", fieldtype="Column Break"),
			field(fieldname="site_address", fieldtype="Link", label="Site Address", options="Address"),
			field(fieldname="contact_person", fieldtype="Link", label="Contact Person", options="Contact"),
			field(fieldname="contact_phone", fieldtype="Data", label="Contact Phone"),
			field(fieldname="equipment_section", fieldtype="Section Break", label="Equipment Identity"),
			field(fieldname="item_code", fieldtype="Link", label="Item", options="Item", reqd=1, in_list_view=1, in_standard_filter=1),
			field(fieldname="item_name", fieldtype="Data", label="Item Name", fetch_from="item_code.item_name", read_only=1),
			field(fieldname="product_family", fieldtype="Data", label="Product Family", fetch_from="item_code.custom_product_family"),
			field(fieldname="column_break_ie_3", fieldtype="Column Break"),
			field(fieldname="serial_no", fieldtype="Link", label="Serial No", options="Serial No", reqd=1, in_list_view=1, in_standard_filter=1),
			field(fieldname="project", fieldtype="Link", label="Project", options="Project", in_standard_filter=1),
			field(fieldname="commercial_section", fieldtype="Section Break", label="Commercial References"),
			field(fieldname="sales_order", fieldtype="Link", label="Sales Order", options="Sales Order"),
			field(fieldname="delivery_note", fieldtype="Link", label="Delivery Note", options="Delivery Note"),
			field(fieldname="column_break_ie_4", fieldtype="Column Break"),
			field(fieldname="sales_invoice", fieldtype="Link", label="Sales Invoice", options="Sales Invoice"),
			field(fieldname="warranty_section", fieldtype="Section Break", label="Warranty & Contract"),
			field(fieldname="under_warranty", fieldtype="Check", label="Under Warranty"),
			field(fieldname="warranty_expiry_date", fieldtype="Date", label="Warranty Expiry Date"),
			field(fieldname="column_break_ie_5", fieldtype="Column Break"),
			field(fieldname="current_service_contract", fieldtype="Link", label="Current Service Contract", options="Service Contract"),
			field(fieldname="maintenance_status", fieldtype="Data", label="Maintenance Status", read_only=1),
			field(fieldname="documents_section", fieldtype="Section Break", label="Documents"),
			field(fieldname="user_manual", fieldtype="Attach", label="User Manual"),
			field(fieldname="installation_acceptance_certificate", fieldtype="Attach", label="Installation Acceptance Certificate"),
			field(fieldname="column_break_ie_6", fieldtype="Column Break"),
			field(fieldname="other_attachments", fieldtype="Attach", label="Other Attachments"),
			field(fieldname="history_tab", fieldtype="Tab Break", label="Lifetime History"),
			field(fieldname="lifetime_history_html", fieldtype="HTML", label="Lifetime History"),
			field(fieldname="notes_section", fieldtype="Section Break", label="Notes"),
			field(fieldname="notes", fieldtype="Text Editor", label="Notes"),
		],
	)

	write_doctype(
		"Equipment Activity",
		{
			"autoname": "naming_series:",
			"naming_rule": 'By "Naming Series" field',
			"title_field": "activity_type",
			"search_fields": "installed_equipment,activity_type,activity_date,serial_no",
		},
		[
			field(fieldname="naming_series", fieldtype="Select", label="Series", options="EA-.YYYY.-.#####", default="EA-.YYYY.-.#####", reqd=1),
			field(fieldname="installed_equipment", fieldtype="Link", label="Installed Equipment", options="Installed Equipment", reqd=1, in_list_view=1, in_standard_filter=1),
			field(fieldname="serial_no", fieldtype="Link", label="Serial No", options="Serial No", fetch_from="installed_equipment.serial_no", read_only=1, in_list_view=1),
			field(fieldname="customer", fieldtype="Link", label="Customer", options="Customer", fetch_from="installed_equipment.customer", read_only=1),
			field(fieldname="column_break_ea_1", fieldtype="Column Break"),
			field(fieldname="activity_date", fieldtype="Datetime", label="Activity Date", reqd=1, in_list_view=1, default="Now"),
			field(fieldname="activity_type", fieldtype="Link", label="Activity Type", options="Equipment Activity Type", reqd=1, in_list_view=1, in_standard_filter=1),
			field(fieldname="service_call", fieldtype="Link", label="Service Call", options="Service Call"),
			field(fieldname="maintenance_visit", fieldtype="Link", label="Maintenance Visit", options="Maintenance Visit"),
			field(fieldname="details_section", fieldtype="Section Break", label="Details"),
			field(fieldname="description", fieldtype="Text Editor", label="Description"),
			field(fieldname="service_personnel", fieldtype="Table", label="Service Personnel", options="Service Personnel"),
			field(fieldname="attachments_section", fieldtype="Section Break", label="Attachments"),
			field(fieldname="attachment", fieldtype="Attach", label="Attachment"),
			field(fieldname="attachment_2", fieldtype="Attach", label="Attachment 2"),
		],
	)

	write_doctype(
		"Service Call",
		{
			"autoname": "hash",
			"title_field": "complaint",
			"search_fields": "service_call_number,serial_no,customer,status,call_type",
			"links": [
				{"link_doctype": "Service Report", "link_fieldname": "service_call"},
				{"link_doctype": "Equipment Activity", "link_fieldname": "service_call"},
				{"link_doctype": "Checklist Response", "link_fieldname": "service_call"},
			],
		},
		[
			field(fieldname="service_call_number", fieldtype="Data", label="Service Call Number", read_only=1, in_list_view=1, in_standard_filter=1, bold=1),
			field(fieldname="call_date", fieldtype="Datetime", label="Call Date", reqd=1, default="Now", in_list_view=1),
			field(fieldname="call_type", fieldtype="Link", label="Call Type", options="Service Call Type", reqd=1, in_standard_filter=1),
			field(fieldname="column_break_sc_1", fieldtype="Column Break"),
			field(fieldname="status", fieldtype="Select", label="Status", options="Open\nAssigned\nScheduled\nIn Progress\nResolved\nClosed\nCancelled", default="Open", reqd=1, in_list_view=1, in_standard_filter=1),
			field(fieldname="priority", fieldtype="Select", label="Priority", options="Low\nMedium\nHigh\nCritical", default="Medium"),
			field(fieldname="company", fieldtype="Link", label="Company", options="Company"),
			field(fieldname="equipment_section", fieldtype="Section Break", label="Equipment"),
			field(fieldname="installed_equipment", fieldtype="Link", label="Installed Equipment", options="Installed Equipment", reqd=1, in_standard_filter=1),
			field(fieldname="serial_no", fieldtype="Link", label="Serial No", options="Serial No", fetch_from="installed_equipment.serial_no", in_list_view=1, in_standard_filter=1),
			field(fieldname="item_code", fieldtype="Link", label="Item", options="Item", fetch_from="installed_equipment.item_code", read_only=1),
			field(fieldname="column_break_sc_2", fieldtype="Column Break"),
			field(fieldname="customer", fieldtype="Link", label="Customer", options="Customer", fetch_from="installed_equipment.customer", read_only=1, in_list_view=1),
			field(fieldname="project", fieldtype="Link", label="Project", options="Project", fetch_from="installed_equipment.project", read_only=1),
			field(fieldname="service_contract", fieldtype="Link", label="Service Contract", options="Service Contract", fetch_from="installed_equipment.current_service_contract"),
			field(fieldname="warranty_status", fieldtype="Data", label="Warranty Status", read_only=1),
			field(fieldname="complaint_section", fieldtype="Section Break", label="Complaint"),
			field(fieldname="complainant", fieldtype="Data", label="Complainant", in_list_view=1),
			field(fieldname="complainant_phone", fieldtype="Data", label="Complainant Phone"),
			field(fieldname="column_break_sc_3", fieldtype="Column Break"),
			field(fieldname="received_by", fieldtype="Link", label="Received By", options="User", default="__user"),
			field(fieldname="complaint", fieldtype="Small Text", label="Complaint", reqd=1),
			field(fieldname="problem_codes", fieldtype="Table", label="Problem Codes", options="Service Call Problem Code"),
			field(fieldname="assignment_section", fieldtype="Section Break", label="Assignment & Action"),
			field(fieldname="service_personnel", fieldtype="Table", label="Service Personnel", options="Service Personnel"),
			field(fieldname="action_taken", fieldtype="Text Editor", label="Action Taken"),
			field(fieldname="resolution_summary", fieldtype="Small Text", label="Resolution Summary"),
			field(fieldname="links_section", fieldtype="Section Break", label="Linked Documents"),
			field(fieldname="maintenance_visit", fieldtype="Link", label="Maintenance Visit", options="Maintenance Visit"),
			field(fieldname="service_report", fieldtype="Link", label="Service Report", options="Service Report", read_only=1),
			field(fieldname="column_break_sc_4", fieldtype="Column Break"),
			field(fieldname="sla_due", fieldtype="Datetime", label="SLA Due"),
			field(fieldname="resolved_on", fieldtype="Datetime", label="Resolved On"),
		],
	)

	write_doctype(
		"Service Report",
		{
			"autoname": "naming_series:",
			"naming_rule": 'By "Naming Series" field',
			"is_submittable": 1,
			"search_fields": "service_call,serial_no,customer,status",
		},
		[
			field(fieldname="naming_series", fieldtype="Select", label="Series", options="SR-.YYYY.-.#####", default="SR-.YYYY.-.#####", reqd=1),
			field(fieldname="amended_from", fieldtype="Link", label="Amended From", options="Service Report", read_only=1, no_copy=1),
			field(fieldname="service_call", fieldtype="Link", label="Service Call", options="Service Call", reqd=1, in_list_view=1),
			field(fieldname="maintenance_visit", fieldtype="Link", label="Maintenance Visit", options="Maintenance Visit"),
			field(fieldname="column_break_sr_1", fieldtype="Column Break"),
			field(fieldname="company", fieldtype="Link", label="Company", options="Company"),
			field(fieldname="report_datetime", fieldtype="Datetime", label="Report Date/Time", default="Now", reqd=1),
			field(
				fieldname="service_type",
				fieldtype="Select",
				label="Service Type",
				options="\nWarranty\nAMC\nCAMC\nPMC\nBillable",
			),
			field(fieldname="equipment_section", fieldtype="Section Break", label="Equipment"),
			field(fieldname="installed_equipment", fieldtype="Link", label="Installed Equipment", options="Installed Equipment", fetch_from="service_call.installed_equipment", reqd=1),
			field(fieldname="serial_no", fieldtype="Link", label="Serial No", options="Serial No", fetch_from="installed_equipment.serial_no", read_only=1),
			field(fieldname="item_code", fieldtype="Link", label="Item", options="Item", fetch_from="installed_equipment.item_code", read_only=1),
			field(fieldname="column_break_sr_2", fieldtype="Column Break"),
			field(fieldname="customer", fieldtype="Link", label="Customer", options="Customer", fetch_from="installed_equipment.customer", read_only=1),
			field(fieldname="activity_start", fieldtype="Datetime", label="Activity Start"),
			field(fieldname="activity_end", fieldtype="Datetime", label="Activity End"),
			field(fieldname="problem_section", fieldtype="Section Break", label="Problem & Resolution"),
			field(fieldname="problem_description", fieldtype="Text Editor", label="Problem Description"),
			field(fieldname="problem_codes", fieldtype="Table", label="Problem Codes", options="Service Call Problem Code"),
			field(fieldname="root_cause", fieldtype="Text Editor", label="Root Cause"),
			field(fieldname="corrective_action", fieldtype="Text Editor", label="Corrective Action"),
			field(fieldname="parts_section", fieldtype="Section Break", label="Parts Replaced"),
			field(fieldname="parts_replaced", fieldtype="Table", label="Parts Replaced", options="Service Report Part"),
			field(fieldname="personnel_section", fieldtype="Section Break", label="Personnel & Feedback"),
			field(fieldname="service_personnel", fieldtype="Table", label="Service Personnel", options="Service Personnel"),
			field(fieldname="customer_feedback", fieldtype="Small Text", label="Customer Feedback"),
			field(fieldname="column_break_sr_3", fieldtype="Column Break"),
			field(fieldname="satisfaction_rating", fieldtype="Select", label="Satisfaction Rating", options="\n1\n2\n3\n4\n5"),
			field(fieldname="promote_to_problem_record", fieldtype="Check", label="Promote to Problem Record on Submit"),
		],
	)

	write_doctype(
		"Service Contract",
		{
			"autoname": "naming_series:",
			"naming_rule": 'By "Naming Series" field',
			"is_submittable": 1,
			"search_fields": "installed_equipment,customer,contract_type,status",
		},
		[
			field(fieldname="naming_series", fieldtype="Select", label="Series", options="SC-.YYYY.-.#####", default="SC-.YYYY.-.#####", reqd=1),
			field(fieldname="amended_from", fieldtype="Link", label="Amended From", options="Service Contract", read_only=1, no_copy=1),
			field(fieldname="contract_type", fieldtype="Select", label="Contract Type", options="AMC\nCAMC\nPMC\nExtended Warranty", reqd=1, in_list_view=1),
			field(fieldname="status", fieldtype="Select", label="Status", options="Draft\nActive\nExpired\nCancelled", default="Draft", in_list_view=1),
			field(fieldname="column_break_scon_1", fieldtype="Column Break"),
			field(fieldname="company", fieldtype="Link", label="Company", options="Company", reqd=1),
			field(fieldname="start_date", fieldtype="Date", label="Start Date", reqd=1),
			field(fieldname="end_date", fieldtype="Date", label="End Date", reqd=1, in_list_view=1),
			field(fieldname="equipment_section", fieldtype="Section Break", label="Equipment"),
			field(fieldname="installed_equipment", fieldtype="Link", label="Installed Equipment", options="Installed Equipment", reqd=1, in_list_view=1),
			field(fieldname="serial_no", fieldtype="Link", label="Serial No", options="Serial No", fetch_from="installed_equipment.serial_no", read_only=1),
			field(fieldname="item_code", fieldtype="Link", label="Item", options="Item", fetch_from="installed_equipment.item_code", read_only=1),
			field(fieldname="column_break_scon_2", fieldtype="Column Break"),
			field(fieldname="customer", fieldtype="Link", label="Customer", options="Customer", fetch_from="installed_equipment.customer", read_only=1),
			field(fieldname="quotation", fieldtype="Link", label="Quotation", options="Quotation"),
			field(fieldname="sales_order", fieldtype="Link", label="Sales Order", options="Sales Order"),
			field(fieldname="entitlement_section", fieldtype="Section Break", label="Entitlements"),
			field(fieldname="included_pm_visits", fieldtype="Int", label="Included PM Visits", default=0),
			field(fieldname="included_emergency_visits", fieldtype="Int", label="Included Emergency Visits", default=0),
			field(fieldname="column_break_scon_3", fieldtype="Column Break"),
			field(fieldname="response_time_hours", fieldtype="Float", label="Response Time (Hours)"),
			field(fieldname="coverage_notes", fieldtype="Text Editor", label="Coverage Notes"),
		],
	)

	write_doctype(
		"Problem Record",
		{
			"autoname": "naming_series:",
			"naming_rule": 'By "Naming Series" field',
			"title_field": "title",
			"search_fields": "title,symptom,root_cause,solution,item_code,serial_no",
		},
		[
			field(fieldname="naming_series", fieldtype="Select", label="Series", options="PR-.YYYY.-.#####", default="PR-.YYYY.-.#####", reqd=1),
			field(fieldname="title", fieldtype="Data", label="Title", reqd=1, in_list_view=1),
			field(fieldname="is_active", fieldtype="Check", label="Is Active", default=1),
			field(fieldname="column_break_pr_1", fieldtype="Column Break"),
			field(fieldname="item_code", fieldtype="Link", label="Item / Model", options="Item", in_standard_filter=1),
			field(fieldname="product_family", fieldtype="Data", label="Product Family"),
			field(fieldname="installed_equipment", fieldtype="Link", label="Installed Equipment", options="Installed Equipment"),
			field(fieldname="serial_no", fieldtype="Link", label="Serial No", options="Serial No"),
			field(fieldname="source_section", fieldtype="Section Break", label="Source"),
			field(fieldname="source_service_call", fieldtype="Link", label="Source Service Call", options="Service Call"),
			field(fieldname="source_service_report", fieldtype="Link", label="Source Service Report", options="Service Report"),
			field(fieldname="column_break_pr_2", fieldtype="Column Break"),
			field(fieldname="resolved_by", fieldtype="Link", label="Resolved By", options="User"),
			field(fieldname="resolved_on", fieldtype="Date", label="Resolved On"),
			field(fieldname="content_section", fieldtype="Section Break", label="Problem Knowledge"),
			field(fieldname="problem_codes", fieldtype="Table", label="Problem Codes", options="Service Call Problem Code"),
			field(fieldname="symptom", fieldtype="Text Editor", label="Symptom"),
			field(fieldname="root_cause", fieldtype="Text Editor", label="Root Cause"),
			field(fieldname="solution", fieldtype="Text Editor", label="Solution"),
			field(fieldname="searchable_text", fieldtype="Long Text", label="Searchable Text", read_only=1),
		],
	)

	write_doctype(
		"Checklist Template",
		{
			"autoname": "field:template_name",
			"naming_rule": "By fieldname",
			"title_field": "template_name",
		},
		[
			field(fieldname="template_name", fieldtype="Data", label="Template Name", reqd=1, unique=1),
			field(
				fieldname="purpose",
				fieldtype="Select",
				label="Purpose",
				options="Pre-Install\nInstallation\nCommissioning\nPM\nOther",
				reqd=1,
			),
			field(fieldname="column_break_ct_1", fieldtype="Column Break"),
			field(fieldname="item_group", fieldtype="Link", label="Item Group", options="Item Group"),
			field(fieldname="product_family", fieldtype="Data", label="Product Family"),
			field(fieldname="version", fieldtype="Data", label="Version", default="1.0"),
			field(fieldname="is_active", fieldtype="Check", label="Is Active", default=1),
			field(fieldname="items", fieldtype="Table", label="Items", options="Checklist Template Item", reqd=1),
		],
	)

	write_doctype(
		"Checklist Response",
		{
			"autoname": "naming_series:",
			"naming_rule": 'By "Naming Series" field',
			"is_submittable": 1,
		},
		[
			field(fieldname="naming_series", fieldtype="Select", label="Series", options="CLR-.YYYY.-.#####", default="CLR-.YYYY.-.#####", reqd=1),
			field(fieldname="amended_from", fieldtype="Link", label="Amended From", options="Checklist Response", read_only=1, no_copy=1),
			field(fieldname="checklist_template", fieldtype="Link", label="Checklist Template", options="Checklist Template", reqd=1),
			field(fieldname="purpose", fieldtype="Data", label="Purpose", fetch_from="checklist_template.purpose", read_only=1),
			field(fieldname="column_break_clr_1", fieldtype="Column Break"),
			field(fieldname="installed_equipment", fieldtype="Link", label="Installed Equipment", options="Installed Equipment", reqd=1),
			field(fieldname="service_call", fieldtype="Link", label="Service Call", options="Service Call"),
			field(fieldname="maintenance_visit", fieldtype="Link", label="Maintenance Visit", options="Maintenance Visit"),
			field(fieldname="status", fieldtype="Select", label="Status", options="Draft\nIn Progress\nCompleted", default="Draft"),
			field(fieldname="responses", fieldtype="Table", label="Responses", options="Checklist Response Item"),
		],
	)

	print("core doctypes done")


if __name__ == "__main__":
	main()
