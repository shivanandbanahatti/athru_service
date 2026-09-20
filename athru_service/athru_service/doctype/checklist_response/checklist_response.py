# Copyright (c) 2026, Athru and contributors
# For license information, please see license.txt

from __future__ import annotations

import frappe
from frappe.model.document import Document


class ChecklistResponse(Document):
	def validate(self):
		if self.checklist_template and not self.responses:
			self._load_from_template()

	def _load_from_template(self):
		template = frappe.get_doc("Checklist Template", self.checklist_template)
		for item in template.items:
			self.append(
				"responses",
				{
					"section": item.section,
					"question": item.question,
					"field_type": item.field_type,
					"is_required": item.is_required,
				},
			)


def validate_doc(doc, method=None):
	doc.validate()


def before_insert_load_template(doc, method=None):
	if doc.checklist_template and not doc.responses:
		doc._load_from_template()
