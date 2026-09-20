# Athru Service — Admin Guide

## Audience

ERPNext administrators configuring Athru Service for an ETO/MTO equipment manufacturer.

## After install

1. **Athru Service Settings**
   - `Call Intake Mode`: `Any Service User` (default) or `Central Desk Only`
   - `Service Call Naming`: `YYMMDD-##` (daily reverse-date sequence)
   - `Contract Renewal Lead Days`: default 30
2. **Roles** — assign to users:
   - Service Manager — full control
   - Service Desk Agent — register and manage calls
   - Service Engineer — field execution / reports
   - Service Read Only — history viewing
3. **Masters** — customise without code:
   - Equipment Activity Type
   - Service Call Type
   - Problem Code
   - Checklist Template

## Recommended process

### Dispatch handoff

1. Issue Serial No on finished goods.
2. On Delivery Note submit (or via **Create Installed Equipment**), create Installed Equipment + Dispatched activity.
3. Attach invoice / DN PDF on the activity.

### Installation diary

Log Equipment Activities day-wise (who went, problems faced). On completion, log **Installation Acceptance** and attach the signed certificate. Status becomes **Commissioned**.

### Field calls

Use **Register Service Call** (list button). Prefer a published support number; set **Central Desk Only** when ready. Select equipment by serial, enter complaint, complainant, action.

### Knowledge reuse

On Service Report submit, enable **Promote to Problem Record**, or use **Promote** / **Find Similar Problems** on Service Call. Search by symptom text, problem codes, model, or equipment.

### Contracts

Mark Quotation / Sales Order as **Is Service Contract**, set type and Installed Equipment. On submit, a draft Service Contract is created. Submit the contract to activate entitlements.

## Custom fields on ERPNext

Synced on install/migrate (see `athru_service/custom/custom_fields.json`): Serial No, Item, Maintenance Visit/Schedule, Quotation, Sales Order, Delivery Note.

## Branding

Do not hardcode customer legal names in the app. Use Company letterhead in print formats. Keep customer-specific codes/templates on the site (or a private data package).
