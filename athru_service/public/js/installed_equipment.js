frappe.ui.form.on("Installed Equipment", {
	refresh(frm) {
		frm.add_custom_button(__("Log Activity"), () => {
			frappe.new_doc("Equipment Activity", {
				installed_equipment: frm.doc.name,
			});
		}, __("Create"));

		frm.add_custom_button(__("New Service Call"), () => {
			frappe.new_doc("Service Call", {
				installed_equipment: frm.doc.name,
			});
		}, __("Create"));

		frm.add_custom_button(__("Find Similar Problems"), () => {
			frappe.call({
				method: "athru_service.api.knowledge.find_similar",
				args: {
					item_code: frm.doc.item_code,
					installed_equipment: frm.doc.name,
					free_text: "",
				},
				callback(r) {
					show_similar_dialog(r.message || []);
				},
			});
		});

		if (!frm.is_new()) {
			render_lifetime_history(frm);
		}
	},
});

function render_lifetime_history(frm) {
	frappe.call({
		method: "athru_service.athru_service.doctype.installed_equipment.installed_equipment.get_lifetime_history",
		args: { installed_equipment: frm.doc.name },
		callback(r) {
			const data = r.message || {};
			let html = `<div class="athru-lifetime-history">`;
			html += section("Activities", data.activities, (row) =>
				`<li><a href="/app/equipment-activity/${row.name}">${frappe.datetime.str_to_user(row.activity_date) || ""} — <b>${row.activity_type || ""}</b></a></li>`
			);
			html += section("Service Calls", data.service_calls, (row) =>
				`<li><a href="/app/service-call/${row.name}"><b>${row.service_call_number || row.name}</b></a> — ${row.status || ""} — ${(row.complaint || "").substring(0, 80)}</li>`
			);
			html += section("Service Reports", data.service_reports, (row) =>
				`<li><a href="/app/service-report/${row.name}">${row.name}</a> — ${row.service_type || ""}</li>`
			);
			html += section("Service Contracts", data.service_contracts, (row) =>
				`<li><a href="/app/service-contract/${row.name}">${row.name}</a> — ${row.contract_type || ""} (${row.start_date || ""} → ${row.end_date || ""})</li>`
			);
			html += `</div>`;
			frm.fields_dict.lifetime_history_html.$wrapper.html(html);
		},
	});
}

function section(title, rows, renderer) {
	if (!rows || !rows.length) {
		return `<h5>${title}</h5><p class="text-muted">${__("None")}</p>`;
	}
	return `<h5>${title}</h5><ul>${rows.map(renderer).join("")}</ul>`;
}

function show_similar_dialog(rows) {
	if (!rows.length) {
		frappe.msgprint(__("No similar problems found"));
		return;
	}
	let html = `<table class="table table-bordered"><thead><tr>
		<th>${__("Type")}</th><th>${__("Title")}</th><th>${__("Score")}</th><th>${__("Solution")}</th>
	</tr></thead><tbody>`;
	rows.forEach((row) => {
		html += `<tr>
			<td>${row.doctype}</td>
			<td><a href="/app/${frappe.router.slug(row.doctype)}/${row.name}">${row.title || row.name}</a></td>
			<td>${row.score}</td>
			<td>${frappe.utils.escape_html(row.solution || "")}</td>
		</tr>`;
	});
	html += `</tbody></table>`;
	frappe.msgprint({ title: __("Similar Problems"), message: html, wide: true });
}
