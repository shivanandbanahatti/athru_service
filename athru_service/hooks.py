app_name = "athru_service"
app_title = "Athru Service"
app_publisher = "Athru"
app_description = "Brand-neutral field service framework for ETO/MTO equipment companies"
app_email = "support@athrutec.com"
app_license = "mit"
app_version = "0.1.0"

required_apps = ["erpnext"]

add_to_apps_screen = [
	{
		"name": "athru_service",
		"logo": "/assets/athru_service/images/athru_service.svg",
		"title": "Athru Service",
		"route": "/app/athru-service",
	}
]

app_include_css = "/assets/athru_service/css/athru_service.css"
app_include_js = "/assets/athru_service/js/athru_service.js"

doctype_js = {
	"Installed Equipment": "public/js/installed_equipment.js",
	"Service Call": "public/js/service_call.js",
	"Service Report": "public/js/service_report.js",
	"Maintenance Visit": "public/js/maintenance_visit.js",
	"Delivery Note": "public/js/delivery_note.js",
	"Serial No": "public/js/serial_no.js",
	"Quotation": "public/js/quotation.js",
	"Sales Order": "public/js/sales_order.js",
}

doc_events = {
	"Service Call": {
		"before_insert": "athru_service.athru_service.doctype.service_call.service_call.before_insert",
		"validate": "athru_service.athru_service.doctype.service_call.service_call.validate",
		"on_update": "athru_service.athru_service.doctype.service_call.service_call.on_update",
		"after_insert": "athru_service.notifications.notify_service_call_created",
	},
	"Service Report": {
		"on_submit": "athru_service.athru_service.doctype.service_report.service_report.on_submit",
		"on_cancel": "athru_service.athru_service.doctype.service_report.service_report.on_cancel",
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
	"Installed Equipment": {
		"validate": "athru_service.athru_service.doctype.installed_equipment.installed_equipment.validate",
		"on_update": "athru_service.athru_service.doctype.installed_equipment.installed_equipment.on_update",
	},
	"Equipment Activity": {
		"on_update": "athru_service.athru_service.doctype.equipment_activity.equipment_activity.on_update",
		"after_insert": "athru_service.athru_service.doctype.equipment_activity.equipment_activity.after_insert",
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
}

scheduler_events = {
	"daily": [
		"athru_service.athru_service.doctype.installed_equipment.installed_equipment.refresh_warranty_status",
		"athru_service.athru_service.doctype.service_contract.service_contract.create_renewal_followups",
	],
}

permission_query_conditions = {
	"Service Call": "athru_service.permissions.get_permission_query_conditions_for_service_call",
	"Maintenance Visit": "athru_service.permissions.get_permission_query_conditions_for_maintenance_visit",
}

has_permission = {
	"Service Call": "athru_service.permissions.has_permission_service_call",
}

after_install = "athru_service.setup.install.after_install"
after_migrate = "athru_service.setup.install.after_migrate"

fixtures = []
