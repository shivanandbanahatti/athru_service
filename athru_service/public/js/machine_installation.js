frappe.ui.form.on("Machine Installation", {
	refresh(frm) {
		frm.add_custom_button(__("Open SPA Hub"), () => {
			window.open(`/athru-service/machines/${encodeURIComponent(frm.doc.name)}`, "_blank");
		});
		frm.add_custom_button(__("Service Request"), () => {
			frappe.new_doc("HD Ticket", {
				custom_machine_installation: frm.doc.name,
				subject: __("Support — {0}", [frm.doc.serial_no || frm.doc.name]),
			});
		}, __("Create"));
		frm.add_custom_button(__("Equipment Activity"), () => {
			frappe.new_doc("Equipment Activity", {
				machine_installation: frm.doc.name,
			});
		}, __("Create"));
		if (!frm.is_new()) {
			frappe.call({
				method: "athru_service.athru_service.doctype.machine_installation.machine_installation.get_lifetime_history",
				args: { machine_installation: frm.doc.name },
				callback(r) {
					if (!r.message || !frm.fields_dict.lifetime_history_html) return;
					const h = r.message;
					const parts = [];
					(h.activities || []).slice(0, 8).forEach((a) => {
						parts.push(`<li><b>${frappe.utils.escape_html(a.activity_type || "")}</b> — ${frappe.utils.escape_html(a.activity_date || "")}</li>`);
					});
					(h.service_requests || []).slice(0, 5).forEach((t) => {
						parts.push(`<li>SR: ${frappe.utils.escape_html(t.subject || t.name)} (${frappe.utils.escape_html(t.status || "")})</li>`);
					});
					frm.set_df_property(
						"lifetime_history_html",
						"options",
						`<div class="athru-lifetime"><ul>${parts.join("") || "<li>No history yet</li>"}</ul>
						<p><a href="/athru-service/machines/${encodeURIComponent(frm.doc.name)}" target="_blank">Open full hub →</a></p></div>`
					);
					frm.refresh_field("lifetime_history_html");
				},
			});
		}
	},
});
