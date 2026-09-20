frappe.ui.form.on("Service Call", {
	setup(frm) {
		frm.set_query("installed_equipment", () => ({
			filters: {
				status: ["not in", ["Decommissioned", "Draft"]],
			},
		}));
	},

	refresh(frm) {
		frm.add_custom_button(__("Find Similar Problems"), () => {
			const codes = (frm.doc.problem_codes || []).map((r) => r.problem_code).join(",");
			frappe.call({
				method: "athru_service.api.knowledge.find_similar",
				args: {
					free_text: frm.doc.complaint || "",
					problem_codes: codes,
					item_code: frm.doc.item_code,
					installed_equipment: frm.doc.installed_equipment,
					exclude_service_call: frm.doc.name,
				},
				callback(r) {
					const rows = r.message || [];
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
					frappe.msgprint({ title: __("Search by Problem"), message: html, wide: true });
				},
			});
		});

		if (!frm.is_new() && frm.doc.status !== "Cancelled") {
			frm.add_custom_button(__("Maintenance Visit"), () => {
				frappe.model.with_doctype("Maintenance Visit", () => {
					const visit = frappe.model.get_new_doc("Maintenance Visit");
					visit.customer = frm.doc.customer;
					visit.custom_service_call = frm.doc.name;
					visit.custom_installed_equipment = frm.doc.installed_equipment;
					frappe.set_route("Form", "Maintenance Visit", visit.name);
				});
			}, __("Create"));

			frm.add_custom_button(__("Service Report"), () => {
				frappe.new_doc("Service Report", {
					service_call: frm.doc.name,
					installed_equipment: frm.doc.installed_equipment,
					maintenance_visit: frm.doc.maintenance_visit,
				});
			}, __("Create"));

			frm.add_custom_button(__("Promote to Problem Record"), () => {
				frappe.call({
					method: "athru_service.api.knowledge.promote_from_service_call",
					args: { service_call: frm.doc.name },
					callback(r) {
						frappe.set_route("Form", "Problem Record", r.message);
					},
				});
			}, __("Create"));
		}
	},

	installed_equipment(frm) {
		if (!frm.doc.installed_equipment) return;
		frappe.db.get_doc("Installed Equipment", frm.doc.installed_equipment).then((ie) => {
			frm.set_value("company", ie.company);
		});
	},
});

// Quick register list view button
frappe.listview_settings["Service Call"] = {
	onload(listview) {
		listview.page.add_inner_button(__("Register Service Call"), () => {
			const d = new frappe.ui.Dialog({
				title: __("Register Service Call"),
				fields: [
					{
						fieldname: "installed_equipment",
						fieldtype: "Link",
						options: "Installed Equipment",
						label: __("Installed Equipment"),
						reqd: 1,
						get_query: () => ({ filters: { status: ["!=", "Decommissioned"] } }),
					},
					{ fieldname: "call_type", fieldtype: "Link", options: "Service Call Type", label: __("Call Type"), reqd: 1 },
					{ fieldname: "complainant", fieldtype: "Data", label: __("Complainant") },
					{ fieldname: "complainant_phone", fieldtype: "Data", label: __("Phone") },
					{ fieldname: "complaint", fieldtype: "Small Text", label: __("Complaint"), reqd: 1 },
					{ fieldname: "action_taken", fieldtype: "Small Text", label: __("Action Taken") },
				],
				primary_action_label: __("Register"),
				primary_action(values) {
					frappe.call({
						method: "athru_service.athru_service.doctype.service_call.service_call.register_service_call",
						args: values,
						freeze: true,
						callback(r) {
							d.hide();
							frappe.set_route("Form", "Service Call", r.message);
						},
					});
				},
			});
			d.show();
		});
	},
};
