"""Knowledge search and promote helpers (HD Ticket + Service Report)."""

from __future__ import annotations

import frappe
from frappe.utils import nowdate, strip_html


@frappe.whitelist()
def find_similar(
	free_text: str | None = None,
	query: str | None = None,
	problem_codes: str | list | None = None,
	item_code: str | None = None,
	machine_installation: str | None = None,
	exclude_ticket: str | None = None,
	limit: int = 20,
) -> list[dict]:
	free_text = free_text or query
	limit = min(int(limit or 20), 50)
	if isinstance(problem_codes, str):
		problem_codes = [c.strip() for c in problem_codes.split(",") if c.strip()]
	problem_codes = problem_codes or []
	results: list[dict] = []

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
			"machine_installation",
			"symptom",
			"root_cause",
			"solution",
			"searchable_text",
			"source_service_call",
			"source_service_report",
		],
		limit_page_length=200,
	)
	# tolerate old field name source_service_call storing ticket name
	for rec in records:
		score = _score(
			rec,
			free_text=free_text,
			problem_codes=problem_codes,
			item_code=item_code,
			machine_installation=machine_installation,
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
			}
		)

	# Submitted service reports
	report_filters = {"docstatus": 1}
	reports = frappe.get_all(
		"Service Report",
		filters=report_filters,
		fields=[
			"name",
			"machine_installation",
			"item_code",
			"serial_no",
			"problem_description",
			"root_cause",
			"corrective_action",
			"hd_ticket",
		],
		limit_page_length=200,
		order_by="creation desc",
	)
	for report in reports:
		if exclude_ticket and report.hd_ticket == exclude_ticket:
			continue
		blob = " ".join(
			[
				strip_html(report.problem_description or ""),
				strip_html(report.root_cause or ""),
				strip_html(report.corrective_action or ""),
			]
		)
		proxy = {
			"machine_installation": report.machine_installation,
			"item_code": report.item_code,
			"searchable_text": blob,
			"name": report.name,
		}
		score = _score(
			proxy,
			free_text=free_text,
			problem_codes=problem_codes,
			item_code=item_code,
			machine_installation=machine_installation,
		)
		if score <= 0:
			continue
		results.append(
			{
				"doctype": "Service Report",
				"name": report.name,
				"title": report.name,
				"score": score,
				"item_code": report.item_code,
				"serial_no": report.serial_no,
				"root_cause": strip_html(report.root_cause or "")[:300],
				"solution": strip_html(report.corrective_action or "")[:300],
			}
		)

	results.sort(key=lambda r: r["score"], reverse=True)

	# Closed / resolved HD Tickets (Service Requests)
	if frappe.db.exists("DocType", "HD Ticket") and free_text:
		tickets = frappe.get_all(
			"HD Ticket",
			filters={"status": ["in", ["Resolved", "Closed"]]},
			fields=[
				"name",
				"subject",
				"status",
				"description",
				"custom_machine_installation",
				"custom_item_code",
				"custom_serial_no",
				"custom_service_request_number",
			],
			limit_page_length=100,
			order_by="modified desc",
		)
		for t in tickets:
			if exclude_ticket and t.name == exclude_ticket:
				continue
			proxy = {
				"machine_installation": t.custom_machine_installation,
				"item_code": t.custom_item_code,
				"searchable_text": " ".join(
					[t.subject or "", strip_html(t.description or ""), t.custom_service_request_number or ""]
				),
				"name": t.name,
			}
			score = _score(
				proxy,
				free_text=free_text,
				problem_codes=problem_codes,
				item_code=item_code,
				machine_installation=machine_installation,
			)
			if score <= 0:
				continue
			results.append(
				{
					"doctype": "HD Ticket",
					"name": t.name,
					"title": t.subject or t.custom_service_request_number or t.name,
					"subject": t.subject,
					"status": t.status,
					"score": score,
					"item_code": t.custom_item_code,
					"serial_no": t.custom_serial_no,
					"snippet": strip_html(t.description or "")[:300],
					"root_cause": "",
					"solution": strip_html(t.description or "")[:300],
				}
			)
		results.sort(key=lambda r: r["score"], reverse=True)

	return results[:limit]


def _score(rec, *, free_text, problem_codes, item_code, machine_installation, extra_codes=None) -> int:
	score = 0
	if machine_installation and rec.get("machine_installation") == machine_installation:
		score += 50
	if item_code and rec.get("item_code") == item_code:
		score += 25
	codes = set(extra_codes or [])
	if rec.get("name") and frappe.db.exists("Problem Record", rec.get("name")):
		codes.update(
			frappe.get_all(
				"Service Call Problem Code",
				filters={"parent": rec["name"], "parenttype": "Problem Record"},
				pluck="problem_code",
			)
		)
	score += 10 * len(codes.intersection(set(problem_codes or [])))
	if free_text:
		hay = (rec.get("searchable_text") or "").lower()
		tokens = [t for t in free_text.lower().split() if len(t) > 2]
		score += sum(1 for t in tokens if t in hay) * 3
	return score


@frappe.whitelist()
def promote_from_service_report(service_report: str) -> str:
	report = frappe.get_doc("Service Report", service_report)
	title = (strip_html(report.problem_description or "") or report.name)[:140]
	existing = frappe.db.get_value(
		"Problem Record", {"source_service_report": report.name}, "name"
	)
	payload = {
		"doctype": "Problem Record",
		"title": title,
		"item_code": report.item_code,
		"machine_installation": report.machine_installation,
		"serial_no": report.serial_no,
		"source_service_call": report.hd_ticket,
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
def promote_from_ticket(hd_ticket: str) -> str:
	ticket = frappe.get_doc("HD Ticket", hd_ticket)
	title = (ticket.subject or ticket.name)[:140]
	doc = frappe.get_doc(
		{
			"doctype": "Problem Record",
			"title": title,
			"item_code": ticket.get("custom_item_code"),
			"machine_installation": ticket.get("custom_machine_installation"),
			"serial_no": ticket.get("custom_serial_no"),
			"source_service_call": ticket.name,
			"symptom": ticket.description or ticket.subject,
			"solution": "",
			"resolved_by": frappe.session.user,
			"resolved_on": nowdate(),
			"is_active": 1,
		}
	)
	doc.insert(ignore_permissions=True)
	return doc.name
