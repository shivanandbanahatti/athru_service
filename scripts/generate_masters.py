"""Generate Athru Service DocType JSON + stub controllers (run once during scaffold)."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "athru_service" / "athru_service" / "doctype"


def field(**kwargs):
	return kwargs


def write_doctype(name: str, meta: dict, fields: list, python_extra: str = ""):
	slug = name.lower().replace(" ", "_")
	folder = ROOT / slug
	folder.mkdir(parents=True, exist_ok=True)

	doc = {
		"actions": [],
		"allow_rename": meta.get("allow_rename", 1),
		"autoname": meta.get("autoname"),
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
		"naming_rule": meta.get("naming_rule"),
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
	if meta.get("title_field"):
		doc["title_field"] = meta["title_field"]
	if meta.get("search_fields"):
		doc["search_fields"] = meta["search_fields"]
	if not doc["autoname"]:
		doc.pop("autoname")
	if not doc.get("naming_rule"):
		doc.pop("naming_rule", None)

	(folder / f"{slug}.json").write_text(json.dumps(doc, indent=1) + "\n", encoding="utf-8")

	class_name = "".join(p.title() for p in slug.split("_"))
	py = f'''# Copyright (c) 2026, Athru and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class {class_name}(Document):
	pass
{python_extra}
'''
	(folder / f"{slug}.py").write_text(py, encoding="utf-8")
	(folder / f"{slug}.js").write_text(
		f'// Copyright (c) 2026, Athru and contributors\n\nfrappe.ui.form.on("{name}", {{\n\trefresh(frm) {{\n\t}}\n}});\n',
		encoding="utf-8",
	)
	(folder / "__init__.py").write_text("", encoding="utf-8")
	print(f"wrote {name}")


def std_perms_master():
	return [
		{"role": "System Manager", "read": 1, "write": 1, "create": 1, "delete": 1},
		{"role": "Service Manager", "read": 1, "write": 1, "create": 1, "delete": 1},
		{"role": "Service Desk Agent", "read": 1, "write": 1, "create": 1},
		{"role": "Service Engineer", "read": 1},
		{"role": "Service Read Only", "read": 1},
	]


def main():
	# --- Athru Service Settings (Single) ---
	write_doctype(
		"Athru Service Settings",
		{"issingle": 1, "allow_rename": 0, "permissions": std_perms_master()},
		[
			field(fieldname="call_section", fieldtype="Section Break", label="Service Call"),
			field(
				fieldname="call_intake_mode",
				fieldtype="Select",
				label="Call Intake Mode",
				options="Any Service User\nCentral Desk Only",
				default="Any Service User",
			),
			field(
				fieldname="service_call_naming",
				fieldtype="Data",
				label="Service Call Naming",
				default="YYMMDD-##",
				description="Use YYMMDD-## for daily reverse-date numbering",
			),
			field(fieldname="column_break_settings_1", fieldtype="Column Break"),
			field(
				fieldname="central_desk_role",
				fieldtype="Link",
				label="Central Desk Role",
				options="Role",
				default="Service Desk Agent",
			),
			field(
				fieldname="renewal_lead_days",
				fieldtype="Int",
				label="Contract Renewal Lead Days",
				default=30,
			),
			field(fieldname="defaults_section", fieldtype="Section Break", label="Defaults"),
			field(fieldname="default_company", fieldtype="Link", label="Default Company", options="Company"),
		],
	)

	# --- Equipment Activity Type ---
	write_doctype(
		"Equipment Activity Type",
		{
			"autoname": "field:activity_type",
			"naming_rule": "By fieldname",
			"title_field": "activity_type",
			"permissions": std_perms_master(),
		},
		[
			field(fieldname="activity_type", fieldtype="Data", label="Activity Type", reqd=1, unique=1),
			field(fieldname="description", fieldtype="Small Text", label="Description"),
			field(fieldname="is_active", fieldtype="Check", label="Is Active", default=1),
			field(
				fieldname="updates_equipment_status",
				fieldtype="Select",
				label="Updates Equipment Status",
				options="\nDispatched\nDelivered\nInstallation In Progress\nCommissioned\nActive\nDecommissioned",
			),
		],
	)

	# --- Service Call Type ---
	write_doctype(
		"Service Call Type",
		{
			"autoname": "field:call_type",
			"naming_rule": "By fieldname",
			"title_field": "call_type",
			"permissions": std_perms_master(),
		},
		[
			field(fieldname="call_type", fieldtype="Data", label="Call Type", reqd=1, unique=1),
			field(fieldname="description", fieldtype="Small Text", label="Description"),
			field(fieldname="is_active", fieldtype="Check", label="Is Active", default=1),
		],
	)

	# --- Problem Code ---
	write_doctype(
		"Problem Code",
		{
			"autoname": "field:code",
			"naming_rule": "By fieldname",
			"title_field": "title",
			"search_fields": "code,title,keywords",
			"permissions": std_perms_master(),
		},
		[
			field(fieldname="code", fieldtype="Data", label="Code", reqd=1, unique=1),
			field(fieldname="title", fieldtype="Data", label="Title", reqd=1),
			field(
				fieldname="category",
				fieldtype="Select",
				label="Category",
				options="Symptom\nFailure\nRoot Cause\nResolution",
				reqd=1,
			),
			field(fieldname="column_break_pc_1", fieldtype="Column Break"),
			field(fieldname="item_group", fieldtype="Link", label="Item Group", options="Item Group"),
			field(fieldname="product_family", fieldtype="Data", label="Product Family"),
			field(fieldname="is_active", fieldtype="Check", label="Is Active", default=1),
			field(fieldname="keywords", fieldtype="Small Text", label="Keywords"),
		],
	)

	# --- Service Personnel (child) ---
	write_doctype(
		"Service Personnel",
		{"istable": 1, "allow_rename": 0, "permissions": []},
		[
			field(fieldname="employee", fieldtype="Link", label="Employee", options="Employee", reqd=1, in_list_view=1),
			field(fieldname="employee_name", fieldtype="Data", label="Employee Name", fetch_from="employee.employee_name", read_only=1, in_list_view=1),
			field(fieldname="role", fieldtype="Data", label="Role", in_list_view=1),
			field(fieldname="user_id", fieldtype="Link", label="User", options="User", fetch_from="employee.user_id", read_only=1),
		],
	)

	# --- Service Call Problem Code (child) ---
	write_doctype(
		"Service Call Problem Code",
		{"istable": 1, "allow_rename": 0, "permissions": []},
		[
			field(fieldname="problem_code", fieldtype="Link", label="Problem Code", options="Problem Code", reqd=1, in_list_view=1),
			field(fieldname="title", fieldtype="Data", label="Title", fetch_from="problem_code.title", read_only=1, in_list_view=1),
			field(fieldname="category", fieldtype="Data", label="Category", fetch_from="problem_code.category", read_only=1, in_list_view=1),
		],
	)

	# --- Service Report Part (child) ---
	write_doctype(
		"Service Report Part",
		{"istable": 1, "allow_rename": 0, "permissions": []},
		[
			field(fieldname="item_code", fieldtype="Link", label="Item", options="Item", reqd=1, in_list_view=1),
			field(fieldname="item_name", fieldtype="Data", label="Item Name", fetch_from="item_code.item_name", read_only=1, in_list_view=1),
			field(fieldname="qty", fieldtype="Float", label="Qty", default=1, in_list_view=1),
			field(fieldname="serial_no", fieldtype="Link", label="Serial No", options="Serial No", in_list_view=1),
			field(fieldname="uom", fieldtype="Link", label="UOM", options="UOM", fetch_from="item_code.stock_uom"),
		],
	)

	# --- Checklist Template Item (child) ---
	write_doctype(
		"Checklist Template Item",
		{"istable": 1, "allow_rename": 0, "permissions": []},
		[
			field(fieldname="section", fieldtype="Data", label="Section", in_list_view=1),
			field(fieldname="question", fieldtype="Small Text", label="Question", reqd=1, in_list_view=1),
			field(
				fieldname="field_type",
				fieldtype="Select",
				label="Field Type",
				options="Check\nData\nSelect\nFloat\nAttach",
				default="Check",
				in_list_view=1,
			),
			field(fieldname="options", fieldtype="Small Text", label="Options"),
			field(fieldname="is_required", fieldtype="Check", label="Required", in_list_view=1),
		],
	)

	# --- Checklist Response Item (child) ---
	write_doctype(
		"Checklist Response Item",
		{"istable": 1, "allow_rename": 0, "permissions": []},
		[
			field(fieldname="section", fieldtype="Data", label="Section", in_list_view=1, read_only=1),
			field(fieldname="question", fieldtype="Small Text", label="Question", in_list_view=1, read_only=1),
			field(fieldname="field_type", fieldtype="Data", label="Field Type", read_only=1),
			field(fieldname="response", fieldtype="Small Text", label="Response", in_list_view=1),
			field(fieldname="attachment", fieldtype="Attach", label="Attachment"),
			field(fieldname="is_required", fieldtype="Check", label="Required", read_only=1),
		],
	)

	# --- Contract Renewal Followup ---
	write_doctype(
		"Contract Renewal Followup",
		{
			"autoname": "naming_series:",
			"naming_rule": "By \"Naming Series\" field",
			"search_fields": "service_contract,installed_equipment,customer",
		},
		[
			field(fieldname="naming_series", fieldtype="Select", label="Series", options="CRF-.YYYY.-.#####", default="CRF-.YYYY.-.#####", reqd=1),
			field(fieldname="service_contract", fieldtype="Link", label="Service Contract", options="Service Contract", reqd=1),
			field(fieldname="installed_equipment", fieldtype="Link", label="Installed Equipment", options="Installed Equipment", fetch_from="service_contract.installed_equipment"),
			field(fieldname="customer", fieldtype="Link", label="Customer", options="Customer", fetch_from="service_contract.customer"),
			field(fieldname="column_break_crf_1", fieldtype="Column Break"),
			field(fieldname="contract_end_date", fieldtype="Date", label="Contract End Date", fetch_from="service_contract.end_date"),
			field(fieldname="status", fieldtype="Select", label="Status", options="Open\nContacted\nRenewed\nClosed Lost\nCancelled", default="Open"),
			field(fieldname="followup_date", fieldtype="Date", label="Follow-up Date", reqd=1),
			field(fieldname="notes", fieldtype="Text Editor", label="Notes"),
		],
	)

	print("masters done")


if __name__ == "__main__":
	main()
