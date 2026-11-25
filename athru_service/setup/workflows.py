"""Programmatic install of brand-neutral workflows and notifications.

Kept out of the ``fixtures`` hook on purpose (the app ships ``fixtures = []``)
so these records are created idempotently on install/migrate without exporting
site-specific data back into the repo.
"""

from __future__ import annotations

import frappe

# ---------------------------------------------------------------------------
# Shared workflow primitives
# ---------------------------------------------------------------------------

WORKFLOW_STATES = [
	("Pending", "Warning"),
	("Approved", "Success"),
	("Rejected", "Danger"),
]

WORKFLOW_ACTIONS = ["Approve", "Reject"]


def ensure_workflows():
	_ensure_states()
	_ensure_actions()
	_ensure_late_entry_workflow()
	_ensure_field_visit_workflow()


def _ensure_states():
	for state, style in WORKFLOW_STATES:
		if not frappe.db.exists("Workflow State", state):
			frappe.get_doc(
				{"doctype": "Workflow State", "workflow_state_name": state, "style": style}
			).insert(ignore_permissions=True)


def _ensure_actions():
	for action in WORKFLOW_ACTIONS:
		if not frappe.db.exists("Workflow Action Master", action):
			frappe.get_doc(
				{"doctype": "Workflow Action Master", "workflow_action_name": action}
			).insert(ignore_permissions=True)


def _ensure_late_entry_workflow():
	name = "Late Entry Request Approval"
	if frappe.db.exists("Workflow", name):
		return
	if not frappe.db.exists("DocType", "Late Entry Request"):
		return
	frappe.get_doc(
		{
			"doctype": "Workflow",
			"workflow_name": name,
			"document_type": "Late Entry Request",
			"is_active": 1,
			"send_email_alert": 0,
			"workflow_state_field": "workflow_state",
			"states": [
				{
					"state": "Pending",
					"doc_status": "0",
					"allow_edit": "Service Engineer",
				},
				{
					"state": "Approved",
					"doc_status": "1",
					"allow_edit": "Service Manager",
				},
				{
					"state": "Rejected",
					"doc_status": "0",
					"allow_edit": "Service Manager",
				},
			],
			"transitions": [
				{
					"state": "Pending",
					"action": "Approve",
					"next_state": "Approved",
					"allowed": "Service Manager",
					"allow_self_approval": 0,
				},
				{
					"state": "Pending",
					"action": "Reject",
					"next_state": "Rejected",
					"allowed": "Service Manager",
					"allow_self_approval": 1,
				},
			],
		}
	).insert(ignore_permissions=True)


def _ensure_field_visit_workflow():
	name = "Field Visit Approval"
	if frappe.db.exists("Workflow", name):
		return
	if not frappe.db.exists("DocType", "Field Visit"):
		return
	frappe.get_doc(
		{
			"doctype": "Workflow",
			"workflow_name": name,
			"document_type": "Field Visit",
			"is_active": 1,
			"send_email_alert": 0,
			"workflow_state_field": "workflow_state",
			"states": [
				{"state": "Pending", "doc_status": "0", "allow_edit": "Service Engineer"},
				{"state": "Approved", "doc_status": "1", "allow_edit": "Service Manager"},
				{"state": "Rejected", "doc_status": "0", "allow_edit": "Service Manager"},
			],
			"transitions": [
				{
					"state": "Pending",
					"action": "Approve",
					"next_state": "Approved",
					"allowed": "Service Manager",
					"allow_self_approval": 1,
				},
				{
					"state": "Pending",
					"action": "Reject",
					"next_state": "Rejected",
					"allowed": "Service Manager",
					"allow_self_approval": 1,
				},
			],
		}
	).insert(ignore_permissions=True)


# ---------------------------------------------------------------------------
# Notifications
# ---------------------------------------------------------------------------

NOTIFICATIONS = [
	{
		"name": "Late Entry Request Submitted",
		"document_type": "Late Entry Request",
		"event": "Submit",
		"subject": "Late Entry Request {{ doc.name }} approved",
		"recipients_field": "owner",
		"message": (
			"Your late entry request {{ doc.name }} for {{ doc.late_entry_date }} "
			"has been approved."
		),
	},
]


def ensure_notifications():
	for spec in NOTIFICATIONS:
		if frappe.db.exists("Notification", spec["name"]):
			continue
		if not frappe.db.exists("DocType", spec["document_type"]):
			continue
		frappe.get_doc(
			{
				"doctype": "Notification",
				"name": spec["name"],
				"subject": spec["subject"],
				"document_type": spec["document_type"],
				"event": spec["event"],
				"enabled": 1,
				"channel": "Email",
				"recipients": [{"receiver_by_document_field": spec["recipients_field"]}],
				"message": spec["message"],
			}
		).insert(ignore_permissions=True)
