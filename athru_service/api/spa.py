"""SPA-facing APIs for Athru Service."""

from __future__ import annotations

import frappe
from frappe import _
from frappe.utils import add_days, nowdate, today


@frappe.whitelist()
def get_ops_dashboard():
	"""Ops home — alias used by SPA."""
	return get_dashboard()


@frappe.whitelist()
def get_dashboard():
	"""Ops home counters and lists."""
	open_tickets = []
	if frappe.db.exists("DocType", "HD Ticket"):
		open_tickets = frappe.get_all(
			"HD Ticket",
			filters={"status": ["not in", ["Closed", "Resolved"]]},
			fields=[
				"name",
				"subject",
				"status",
				"ticket_type",
				"custom_service_request_number",
				"custom_machine_installation",
				"custom_serial_no",
				"customer",
				"modified",
			],
			order_by="modified desc",
			limit_page_length=20,
		)
	my_tasks = frappe.get_all(
		"Task",
		filters={
			"status": ["not in", ["Completed", "Cancelled"]],
			"_assign": ["like", f"%{frappe.session.user}%"],
		},
		fields=[
			"name",
			"subject",
			"status",
			"exp_end_date",
			"custom_maintenance_visit",
			"custom_hd_ticket",
			"custom_work_date",
		],
		order_by="exp_end_date asc",
		limit_page_length=20,
	)
	visits_today = frappe.get_all(
		"Maintenance Visit",
		filters={"mntc_date": today(), "docstatus": ["<", 2]},
		fields=[
			"name",
			"customer",
			"custom_hd_ticket",
			"custom_machine_installation",
			"completion_status",
		],
		limit_page_length=20,
	)
	expiring = frappe.get_all(
		"Service Contract",
		filters={
			"docstatus": 1,
			"status": "Active",
			"end_date": ["between", [nowdate(), add_days(nowdate(), 60)]],
		},
		fields=["name", "machine_installation", "contract_type", "end_date", "customer"],
		order_by="end_date asc",
		limit_page_length=10,
	)
	return {
		"open_service_requests": open_tickets,
		"open_requests": open_tickets,
		"my_tasks": my_tasks,
		"visits_today": visits_today,
		"contracts_expiring": expiring,
	}


@frappe.whitelist()
def list_machine_installations(search: str | None = None, status: str | None = None, limit: int = 50):
	filters = {}
	if status:
		filters["status"] = status
	or_filters = None
	if search:
		or_filters = [
			["serial_no", "like", f"%{search}%"],
			["name", "like", f"%{search}%"],
			["customer", "like", f"%{search}%"],
			["item_code", "like", f"%{search}%"],
			["item_name", "like", f"%{search}%"],
		]
	rows = frappe.get_all(
		"Machine Installation",
		filters=filters,
		or_filters=or_filters,
		fields=[
			"name",
			"status",
			"customer",
			"customer_name",
			"item_code",
			"item_name",
			"serial_no",
			"project",
			"dispatch_date",
			"commissioning_date",
			"maintenance_status",
		],
		order_by="modified desc",
		limit_page_length=int(limit or 50),
	)
	for row in rows:
		row["equipment_name"] = row.get("item_name") or row.get("item_code") or row.get("name")
	return rows


@frappe.whitelist()
def get_machine_hub(name: str | None = None, machine_installation: str | None = None):
	machine_installation = machine_installation or name
	if not machine_installation:
		frappe.throw(_("Machine Installation is required"))

	from athru_service.athru_service.doctype.machine_installation.machine_installation import (
		get_lifetime_history,
	)

	doc = frappe.get_doc("Machine Installation", machine_installation)
	history = get_lifetime_history(machine_installation)
	timeline = _flatten_timeline(history)
	tickets = history.get("service_requests") or []
	tasks = frappe.get_all(
		"Task",
		filters={"custom_machine_installation": machine_installation},
		fields=[
			"name",
			"subject",
			"status",
			"exp_start_date",
			"exp_end_date",
			"custom_maintenance_visit",
			"custom_work_date",
		],
		order_by="creation desc",
		limit_page_length=50,
	)
	expenses = []
	if frappe.db.exists("DocType", "Expense Claim"):
		expenses = frappe.get_all(
			"Expense Claim",
			filters={"custom_machine_installation": machine_installation},
			fields=["name", "employee", "total_claimed_amount", "status", "posting_date", "approval_status"],
			order_by="posting_date desc",
			limit_page_length=20,
		)
	machine = doc.as_dict()
	machine["equipment_name"] = doc.item_name or doc.item_code or doc.name
	return {
		"doc": machine,
		"machine": machine,
		"history": history,
		"timeline": timeline,
		"tickets": tickets,
		"tasks": tasks,
		"expenses": expenses,
	}


def _flatten_timeline(history: dict) -> list[dict]:
	items: list[dict] = []
	for a in history.get("activities") or []:
		items.append(
			{
				"kind": "Activity",
				"date": a.get("activity_date"),
				"title": a.get("activity_type") or a.get("name"),
				"detail": a.get("description"),
				"status": None,
				"doctype": "Equipment Activity",
				"name": a.get("name"),
			}
		)
	for t in history.get("service_requests") or []:
		items.append(
			{
				"kind": "Service Request",
				"date": t.get("creation"),
				"title": t.get("subject") or t.get("custom_service_request_number") or t.get("name"),
				"detail": t.get("ticket_type"),
				"status": t.get("status"),
				"doctype": "HD Ticket",
				"name": t.get("name"),
			}
		)
	for r in history.get("service_reports") or []:
		items.append(
			{
				"kind": "Service Report",
				"date": r.get("report_datetime"),
				"title": r.get("name"),
				"detail": r.get("root_cause"),
				"status": "Submitted",
				"doctype": "Service Report",
				"name": r.get("name"),
			}
		)
	for r in history.get("installation_reports") or []:
		items.append(
			{
				"kind": "Installation Report",
				"date": r.get("report_date"),
				"title": r.get("name"),
				"detail": None,
				"status": r.get("status"),
				"doctype": "Installation Report",
				"name": r.get("name"),
			}
		)
	for c in history.get("service_contracts") or []:
		items.append(
			{
				"kind": "Contract",
				"date": c.get("end_date") or c.get("start_date"),
				"title": f"{c.get('contract_type') or 'Contract'} · {c.get('name')}",
				"detail": None,
				"status": c.get("status"),
				"doctype": "Service Contract",
				"name": c.get("name"),
			}
		)
	items.sort(key=lambda x: str(x.get("date") or ""), reverse=True)
	return items


@frappe.whitelist()
def list_service_requests(status: str | None = None, limit: int = 100):
	if not frappe.db.exists("DocType", "HD Ticket"):
		return []
	filters = {}
	if status:
		filters["status"] = status
	return frappe.get_all(
		"HD Ticket",
		filters=filters,
		fields=[
			"name",
			"subject",
			"status",
			"ticket_type",
			"custom_service_request_number",
			"custom_machine_installation",
			"custom_serial_no",
			"customer",
			"modified",
		],
		order_by="modified desc",
		limit_page_length=int(limit or 100),
	)


@frappe.whitelist()
def create_service_request(
	machine_installation: str,
	subject: str,
	ticket_type: str | None = None,
	description: str | None = None,
	visit_category: str | None = None,
):
	if not frappe.db.exists("DocType", "HD Ticket"):
		frappe.throw(_("Helpdesk (HD Ticket) is required."))
	from athru_service.athru_service.utils.hd_ticket import ensure_ticket_types, make_service_request_number

	ensure_ticket_types()
	mi = frappe.get_doc("Machine Installation", machine_installation)
	ticket = frappe.new_doc("HD Ticket")
	ticket.subject = subject
	if hasattr(ticket, "ticket_type"):
		ticket.ticket_type = ticket_type or "Breakdown"
	ticket.description = description or subject
	ticket.custom_machine_installation = mi.name
	ticket.custom_visit_category = visit_category or ticket_type or "Breakdown"
	ticket.custom_service_request_number = make_service_request_number()
	ticket.insert()
	return ticket.name


@frappe.whitelist()
def create_visit_from_ticket(hd_ticket: str, visit_category: str | None = None):
	ticket = frappe.get_doc("HD Ticket", hd_ticket)
	visit = frappe.new_doc("Maintenance Visit")
	visit.customer = ticket.get("custom_erp_customer") or frappe.db.get_value(
		"Machine Installation", ticket.custom_machine_installation, "customer"
	)
	visit.mntc_date = nowdate()
	visit.custom_hd_ticket = ticket.name
	visit.custom_machine_installation = ticket.custom_machine_installation
	visit.custom_visit_category = visit_category or ticket.custom_visit_category or "Breakdown"
	for row in ticket.get("custom_service_personnel") or []:
		visit.append(
			"custom_service_personnel",
			{"employee": row.employee, "role": row.role, "employee_name": row.employee_name},
		)
	visit.insert()
	return visit.name


@frappe.whitelist()
def create_visit_task(
	visit: str | None = None,
	maintenance_visit: str | None = None,
	subject: str | None = None,
	work_date: str | None = None,
	description: str | None = None,
	work_log: str | None = None,
	exp_start_date: str | None = None,
	exp_end_date: str | None = None,
):
	"""SPA-friendly task create (day-wise work log)."""
	return create_task_for_visit(
		maintenance_visit=maintenance_visit or visit,
		subject=subject,
		work_log=work_log or description,
		exp_start_date=work_date or exp_start_date,
		exp_end_date=work_date or exp_end_date,
		work_date=work_date,
	)


@frappe.whitelist()
def create_task_for_visit(
	maintenance_visit: str,
	subject: str,
	work_log: str | None = None,
	exp_start_date: str | None = None,
	exp_end_date: str | None = None,
	work_date: str | None = None,
):
	visit = frappe.get_doc("Maintenance Visit", maintenance_visit)
	task = frappe.new_doc("Task")
	task.subject = subject
	task.description = work_log
	task.custom_work_log = work_log
	task.custom_maintenance_visit = visit.name
	task.custom_hd_ticket = visit.custom_hd_ticket
	task.custom_machine_installation = visit.custom_machine_installation
	day = work_date or exp_start_date or nowdate()
	task.exp_start_date = day
	task.exp_end_date = exp_end_date or day
	if frappe.db.has_column("Task", "custom_work_date"):
		task.custom_work_date = day
	mi = visit.custom_machine_installation
	if mi:
		project = frappe.db.get_value("Machine Installation", mi, "project")
		if project:
			task.project = project
	task.insert()
	return task.name


@frappe.whitelist()
def create_schedule_from_ticket(hd_ticket: str, periodicity: str = "Monthly"):
	ticket = frappe.get_doc("HD Ticket", hd_ticket)
	sched = frappe.new_doc("Maintenance Schedule")
	sched.customer = ticket.get("custom_erp_customer") or frappe.db.get_value(
		"Machine Installation", ticket.custom_machine_installation, "customer"
	)
	sched.custom_hd_ticket = ticket.name
	sched.custom_machine_installation = ticket.custom_machine_installation
	sched.custom_service_contract = ticket.custom_service_contract
	sched.insert()
	return sched.name


@frappe.whitelist()
def get_visit_console(name: str | None = None, maintenance_visit: str | None = None):
	maintenance_visit = maintenance_visit or name
	if not maintenance_visit:
		frappe.throw(_("Maintenance Visit is required"))
	visit = frappe.get_doc("Maintenance Visit", maintenance_visit)
	tasks = frappe.get_all(
		"Task",
		filters={"custom_maintenance_visit": maintenance_visit},
		fields=[
			"name",
			"subject",
			"status",
			"description",
			"exp_start_date",
			"exp_end_date",
			"custom_work_log",
			"custom_work_date",
			"_assign",
		],
		order_by="custom_work_date desc, exp_start_date desc",
	)
	installation_reports = frappe.get_all(
		"Installation Report",
		filters={"maintenance_visit": maintenance_visit},
		fields=["name", "status", "report_date", "docstatus"],
	)
	service_reports = frappe.get_all(
		"Service Report",
		filters={"maintenance_visit": maintenance_visit},
		fields=["name", "docstatus", "report_datetime", "service_type"],
	)
	expenses = []
	if frappe.db.exists("DocType", "Expense Claim"):
		expenses = frappe.get_all(
			"Expense Claim",
			filters={"custom_maintenance_visit": maintenance_visit},
			fields=["name", "total_claimed_amount", "status", "approval_status", "posting_date"],
		)
	payload = visit.as_dict()
	return {
		"doc": payload,
		"visit": payload,
		"tasks": tasks,
		"installation_reports": installation_reports,
		"service_reports": service_reports,
		"expenses": expenses,
	}


@frappe.whitelist()
def create_expense_for_visit(visit: str):
	"""Draft Expense Claim linked Visit → Ticket → Machine Installation."""
	if not frappe.db.exists("DocType", "Expense Claim"):
		frappe.throw(_("Expense Claim DocType not available"))
	mv = frappe.get_doc("Maintenance Visit", visit)
	employee = frappe.db.get_value("Employee", {"user_id": frappe.session.user}, "name")
	claim = frappe.new_doc("Expense Claim")
	if employee:
		claim.employee = employee
	claim.custom_maintenance_visit = mv.name
	claim.custom_hd_ticket = mv.custom_hd_ticket
	claim.custom_machine_installation = mv.custom_machine_installation
	claim.insert()
	return claim.name


@frappe.whitelist()
def list_service_contracts(limit: int = 50):
	return frappe.get_all(
		"Service Contract",
		filters={"docstatus": ["<", 2]},
		fields=[
			"name",
			"customer",
			"machine_installation",
			"contract_type",
			"start_date",
			"end_date",
			"status",
		],
		order_by="end_date asc",
		limit_page_length=int(limit or 50),
	)


@frappe.whitelist()
def list_expenses(limit: int = 50):
	if not frappe.db.exists("DocType", "Expense Claim"):
		return []
	return frappe.get_all(
		"Expense Claim",
		or_filters=[
			["custom_maintenance_visit", "!=", ""],
			["custom_machine_installation", "!=", ""],
		],
		fields=[
			"name",
			"employee",
			"total_claimed_amount",
			"status",
			"approval_status",
			"posting_date",
			"custom_maintenance_visit",
			"custom_hd_ticket",
			"custom_machine_installation",
		],
		order_by="posting_date desc",
		limit_page_length=int(limit or 50),
	)