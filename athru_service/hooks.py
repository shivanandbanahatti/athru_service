app_name = "athru_service"
app_title = "Athru Service"
app_publisher = "Athru"
app_description = "Brand-neutral field service framework for ETO/MTO equipment companies"
app_email = "support@athrutec.com"
app_license = "mit"
app_version = "0.2.0"

required_apps = ["erpnext", "helpdesk"]

add_to_apps_screen = [
	{
		"name": "athru_service",
		"logo": "/assets/athru_service/images/athru_service.svg",
		"title": "Athru Service",
		"route": "/athru-service",
	}
]

app_include_css = "/assets/athru_service/css/athru_service.css"
app_include_js = "/assets/athru_service/js/athru_service.js"

website_route_rules = [
	{"from_route": "/athru-service/<path:app_path>", "to_route": "athru-service"},
	{"from_route": "/athru-service", "to_route": "athru-service"},
]

doctype_js = {
	"Machine Installation": "public/js/machine_installation.js",
	"Service Report": "public/js/service_report.js",
	"Installation Report": "public/js/installation_report.js",
	"Maintenance Visit": "public/js/maintenance_visit.js",
	"HD Ticket": "public/js/hd_ticket.js",
	"Delivery Note": "public/js/delivery_note.js",
	"Serial No": "public/js/serial_no.js",
	"Quotation": "public/js/quotation.js",
	"Sales Order": "public/js/sales_order.js",
	"Expense Claim": "public/js/expense_claim.js",
	"Task": "public/js/task.js",
	"Service Call": "public/js/service_call.js",
}

doc_events = {
	"HD Ticket": {
		"before_insert": "athru_service.athru_service.utils.hd_ticket.before_insert",
		"validate": "athru_service.athru_service.utils.hd_ticket.validate",
		"on_update": "athru_service.athru_service.utils.hd_ticket.on_update",
	},
	"Service Report": {
		"on_submit": "athru_service.athru_service.doctype.service_report.service_report.on_submit",
		"on_cancel": "athru_service.athru_service.doctype.service_report.service_report.on_cancel",
	},
	"Installation Report": {
		"on_submit": "athru_service.athru_service.doctype.installation_report.installation_report.on_submit",
		"on_cancel": "athru_service.athru_service.doctype.installation_report.installation_report.on_cancel",
	},
	"Service Contract": {
		"validate": "athru_service.athru_service.doctype.service_contract.service_contract.validate",
		"on_submit": "athru_service.athru_service.doctype.service_contract.service_contract.on_submit",
		"on_cancel": "athru_service.athru_service.doctype.service_contract.service_contract.on_cancel",
	},
	"Checklist Response": {
		"before_insert": "athru_service.athru_service.doctype.checklist_response.checklist_response.before_insert_load_template",
		"validate": "athru_service.athru_service.doctype.checklist_response.checklist_response.validate_doc",
	},
	"Machine Installation": {
		"validate": "athru_service.athru_service.doctype.machine_installation.machine_installation.validate",
		"on_update": "athru_service.athru_service.doctype.machine_installation.machine_installation.on_update",
	},
	"Equipment Activity": {
		"on_update": "athru_service.athru_service.doctype.equipment_activity.equipment_activity.on_update",
		"after_insert": "athru_service.athru_service.doctype.equipment_activity.equipment_activity.after_insert",
	},
	"Maintenance Visit": {
		"before_insert": "athru_service.athru_service.utils.maintenance_visit.before_insert",
		"on_submit": "athru_service.athru_service.utils.maintenance_visit.on_submit",
		"on_cancel": "athru_service.athru_service.utils.maintenance_visit.on_cancel",
	},
	"Quotation": {
		"on_submit": "athru_service.overrides.quotation.on_submit",
	},
	"Sales Order": {
		"on_submit": "athru_service.overrides.sales_order.on_submit",
	},
	"Delivery Note": {
		"on_submit": "athru_service.overrides.delivery_note.on_submit",
	},
	"Expense Claim": {
		"validate": "athru_service.overrides.expense_claim.validate",
	},
}

scheduler_events = {
	"daily": [
		"athru_service.athru_service.doctype.machine_installation.machine_installation.refresh_warranty_status",
		"athru_service.athru_service.doctype.service_contract.service_contract.create_renewal_followups",
	],
}

permission_query_conditions = {
	"HD Ticket": "athru_service.permissions.get_permission_query_conditions_for_hd_ticket",
	"Maintenance Visit": "athru_service.permissions.get_permission_query_conditions_for_maintenance_visit",
}

has_permission = {
	"HD Ticket": "athru_service.permissions.has_permission_hd_ticket",
}

after_install = "athru_service.setup.install.after_install"
after_migrate = "athru_service.setup.install.after_migrate"

fixtures = []
