"""Post-install and migrate hooks for Athru Service."""

from __future__ import annotations

import json
from pathlib import Path

import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

from athru_service.setup.defaults import ensure_defaults


def after_install():
	sync_custom_fields()
	ensure_defaults()
	frappe.clear_cache()


def after_migrate():
	sync_custom_fields()
	ensure_defaults()


def sync_custom_fields():
	path = Path(__file__).resolve().parents[1] / "athru_service" / "custom" / "custom_fields.json"
	if not path.exists():
		return
	rows = json.loads(path.read_text(encoding="utf-8"))
	grouped: dict[str, list] = {}
	for row in rows:
		row = dict(row)
		dt = row.pop("dt")
		row.pop("doctype", None)
		grouped.setdefault(dt, []).append(row)
	create_custom_fields(grouped, update=True)
