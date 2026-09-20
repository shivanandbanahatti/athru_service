# Copyright (c) 2026, Athru and contributors
# For license information, please see license.txt

from __future__ import annotations

import frappe
from frappe.model.document import Document
from frappe.utils import strip_html


class ProblemRecord(Document):
	def validate(self):
		parts = [
			self.title or "",
			strip_html(self.symptom or ""),
			strip_html(self.root_cause or ""),
			strip_html(self.solution or ""),
		]
		for row in self.problem_codes or []:
			parts.append(row.problem_code or "")
			parts.append(row.title or "")
		self.searchable_text = "\n".join(p for p in parts if p)
