"""Knowledge search and promote helpers."""

from __future__ import annotations

import frappe
from frappe import _
from frappe.utils import nowdate, strip_html


@frappe.whitelist()
def find_similar(
	free_text: str | None = None,
	problem_codes: str | list | None = None,
	item_code: str | None = None,
	installed_equipment: str | None = None,
	exclude_service_call: str | None = None,
	limit: int = 20,
) -> list[dict]:
	"""Search Problem Records and past Service Calls/Reports by equipment and/or problem."""
	limit = min(int(limit or 20), 50)
	if isinstance(problem_codes, str):
		problem_codes = [c.strip() for c in problem_codes.split(",") if c.strip()]
	problem_codes = problem_codes or []

	results: list[dict] = []

	# Problem Records
	filters: dict = {"is_active": 1}
	if item_code:
		filters["item_code"] = item_code
	records = frappe.get_all(
		"Problem Record",
		filters=filters,
		fields=[
			"name",
			"title",
			"item_code",
			"serial_no",
			"installed_equipment",
			"symptom",
			"root_cause",
			"solution",
			"searchable_text",
			"resolved_on",
			"source_service_call",
		],
		limit_page_length=200,
	)
	for rec in records:
		score = _score(
			rec,
			free_text=free_text,
			problem_codes=problem_codes,
			item_code=item_code,
			installed_equipment=installed_equipment,
			text_field="searchable_text",
		)
		if score <= 0:
			continue
		results.append(
			{
				"doctype": "Problem Record",
				"name": rec.name,
				"title": rec.title,
				"score": score,
				"item_code": rec.item_code,
				"serial_no": rec.serial_no,
				"root_cause": strip_html(rec.root_cause or "")[:300],
				"solution": strip_html(rec.solution or "")[:300],
				"source_service_call": rec.source_service_call,
			}
		)

	# Past service calls with resolution
	call_filters: dict = {"status": ["in", ["Resolved", "Closed"]]}
	if installed_equipment:
		# Prefer same equipment first via scoring, but also search same model
		pass
	if exclude_service_call:
		call_filters["name"] = ["!=", exclude_service_call]
	calls = frappe.get_all(
		"Service Call",
		filters=call_filters,
		fields=[
			"name",
			"service_call_number",
			"complaint",
			"action_taken",
			"resolution_summary",
			"item_code",
			"serial_no",
			"installed_equipment",
			"call_date",
		],
		limit_page_length=200,
		order_by="call_date desc",
	)
	for call in calls:
		blob = " ".join(
			[
				call.complaint or "",
				strip_html(call.action_taken or ""),
				call.resolution_summary or "",
			]
		)
		proxy = {
			"installed_equipment": call.installed_equipment,
			"item_code": call.item_code,
			"searchable_text": blob,
			"name": call.name,
		}
		# attach problem codes
		codes = frappe.get_all(
			"Service Call Problem Code",
			filters={"parent": call.name, "parenttype": "Service Call"},
			pluck="problem_code",
		)
		score = _score(
			proxy,
			free_text=free_text,
			problem_codes=problem_codes,
			item_code=item_code,
			installed_equipment=installed_equipment,
			extra_codes=codes,
			text_field="searchable_text",
		)
		if score <= 0:
			continue
		results.append(
			{
				"doctype": "Service Call",
				"name": call.name,
				"title": call.service_call_number or call.name,
				"score": score,
				"item_code": call.item_code,
				"serial_no": call.serial_no,
				"root_cause": "",
				"solution": (call.resolution_summary or strip_html(call.action_taken or ""))[:300],
				"source_service_call": call.name,
			}
		)

	results.sort(key=lambda r: r["score"], reverse=True)
	return results[:limit]


def _score(
	rec,
	*,
	free_text,
	problem_codes,
	item_code,
	installed_equipment,
	text_field="searchable_text",
	extra_codes=None,
) -> int:
	score = 0
	if installed_equipment and rec.get("installed_equipment") == installed_equipment:
		score += 50
	if item_code and rec.get("item_code") == item_code:
		score += 25
	codes = set(extra_codes or [])
	# child codes on Problem Record
	if rec.get("name") and frappe.db.exists("Problem Record", rec.get("name")):
		codes.update(
			frappe.get_all(
				"Service Call Problem Code",
				filters={"parent": rec["name"], "parenttype": "Problem Record"},
				pluck="problem_code",
			)
		)
	overlap = codes.intersection(set(problem_codes or []))
	score += 10 * len(overlap)
	if free_text:
		hay = (rec.get(text_field) or "").lower()
		tokens = [t for t in free_text.lower().split() if len(t) > 2]
		hits = sum(1 for t in tokens if t in hay)
		score += hits * 3
	return score


@frappe.whitelist()
def promote_from_service_report(service_report: str) -> str:
	"""Create or update a Problem Record from a submitted Service Report."""
	report = frappe.get_doc("Service Report", service_report)
	title = (strip_html(report.problem_description or "") or report.name)[:140]
	existing = frappe.db.get_value(
		"Problem Record",
		{"source_service_report": report.name},
		"name",
	)
	payload = {
		"doctype": "Problem Record",
		"title": title,
		"item_code": report.item_code,
		"installed_equipment": report.installed_equipment,
		"serial_no": report.serial_no,
		"source_service_call": report.service_call,
		"source_service_report": report.name,
		"symptom": report.problem_description,
		"root_cause": report.root_cause,
		"solution": report.corrective_action,
		"resolved_by": frappe.session.user,
		"resolved_on": nowdate(),
		"is_active": 1,
	}
	if existing:
		doc = frappe.get_doc("Problem Record", existing)
		doc.update(payload)
		doc.problem_codes = []
		for row in report.problem_codes or []:
			doc.append("problem_codes", {"problem_code": row.problem_code})
		doc.save(ignore_permissions=True)
		return doc.name

	doc = frappe.get_doc(payload)
	for row in report.problem_codes or []:
		doc.append("problem_codes", {"problem_code": row.problem_code})
	doc.insert(ignore_permissions=True)
	return doc.name


@frappe.whitelist()
def promote_from_service_call(service_call: str) -> str:
	call = frappe.get_doc("Service Call", service_call)
	title = (call.complaint or call.service_call_number or call.name)[:140]
	doc = frappe.get_doc(
		{
			"doctype": "Problem Record",
			"title": title,
			"item_code": call.item_code,
			"installed_equipment": call.installed_equipment,
			"serial_no": call.serial_no,
			"source_service_call": call.name,
			"symptom": call.complaint,
			"root_cause": "",
			"solution": call.resolution_summary or call.action_taken,
			"resolved_by": frappe.session.user,
			"resolved_on": nowdate(),
			"is_active": 1,
		}
	)
	for row in call.problem_codes or []:
		doc.append("problem_codes", {"problem_code": row.problem_code})
	doc.insert(ignore_permissions=True)
	return doc.name
