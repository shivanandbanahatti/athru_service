# Athru Service — Admin Guide

## Audience

ERPNext administrators configuring Athru Service for an ETO/MTO equipment manufacturer.

## After install

1. Ensure **Helpdesk** and **ERPNext** are installed (`required_apps`).
2. **Athru Service Settings**
   - Service Request Intake Mode: `Any Service User` or `Central Desk Only`
   - Service Request Number Format: `YYMMDD-##` (stored on HD Ticket)
   - Contract Renewal Lead Days: default 30
3. **Roles** — assign to users:
   - Service Manager — full control
   - Service Desk Agent — register and manage service requests
   - Service Engineer — field visits / tasks / reports
   - Service Read Only — history viewing
4. **Org masters** (site data — not OEM packs in the repo):
   - HD Ticket Types (Installation, Breakdown, Preventive, … seeded empty/generic)
   - Equipment Activity Type
   - Problem Code
   - Checklist Templates (Pre-Install, Installation, PM, Commissioning)
5. Build SPA assets (`frontend/` → `public/frontend/`) and open `/athru-service`.

## Canonical process

### Dispatch + installation request

1. Serial in finished-goods warehouse (manufacturing out of scope for Athru v1).
2. Submit Delivery Note with serialised items; leave **Create Machine Installation** / **Create Installation Service Request** checked.
3. System creates **Machine Installation** + **HD Ticket** (`ticket_type=Installation`) and optional engineer rows.

### On-site installation

1. Create **Maintenance Visit** from the Installation ticket (Desk button or SPA).
2. Log **day-wise Tasks** (process, issues) on the Visit console.
3. Complete **Installation Report** (dual sign-off / acceptance attach); commission machine; close ticket.

### Post-install support

1. New **HD Ticket** on the same Machine Installation (Breakdown / PMC / Contract / Billable).
2. **Maintenance Schedule** only when planned (AMC/PMC); otherwise Visit directly from ticket.
3. Capture RCA on Visit + formal **Service Report**; promote to **Problem Record** for knowledge search.

### Expenses

Expense Claims link **Visit → HD Ticket → Machine Installation** (auto-stamped from Visit).

## SPA vs Desk

| Path | Use |
|------|-----|
| `/athru-service` | Daily ops: dashboard, machine hub, service request board, visit+tasks, knowledge |
| Desk DocType forms | Settings, masters, print formats, edge edits (“Open in Desk”) |

## Custom fields

Synced on install/migrate from `athru_service/setup/custom_fields.json` via `create_custom_fields` (HD Ticket, Visit, Schedule, Task, Expense Claim, Quotation, Sales Order, Delivery Note, Serial No, Item).

## Branding

Do not hardcode customer legal names in the app. Use Company letterhead in print formats. Keep customer-specific codes/templates on the site only.
