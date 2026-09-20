# Athru Service — UAT Checklist (SPA-first)

Use the customer's Company / Item / Serial data on their site. Do not commit OEM names into the app.

## Setup

- [ ] App installed on ERPNext v16 + Helpdesk; migrate + `yarn build` (frontend) + `bench build --app athru_service` succeeded
- [ ] Roles assigned; Athru Service workspace shows SPA shortcut
- [ ] Brand lint clean (`python scripts/brand_lint.py`)
- [ ] Org masters seeded/edited: HD Ticket Types, Activity Types, Problem Codes, Checklist Templates

## SPA shell

- [ ] `/athru-service` loads Ops dashboard (open requests, visits today, contracts, my tasks)
- [ ] Navigation: Machines, Service Requests, Knowledge
- [ ] “Open Desk” escape hatch works

## Dispatch → Commission

- [ ] Submit Delivery Note with serial → Machine Installation created
- [ ] Installation HD Ticket created with engineers when flagged
- [ ] SPA Machine Hub shows identity + timeline (activity + ticket)
- [ ] Visit from ticket; day-wise Tasks via Visit console
- [ ] Installation Report submitted with acceptance; machine status Commissioned

## Service Request (HD Ticket)

- [ ] Create support request from Machine Hub; `custom_service_request_number` is `YYMMDD-##`
- [ ] Board/list shows ticket by status; equipment panel fields present
- [ ] Planned PMC creates Maintenance Schedule; emergency creates Visit only
- [ ] Service Report from Visit/Ticket; promote to Problem Record

## Expenses

- [ ] Create Expense Claim from Visit console; Visit / Ticket / Machine stamped
- [ ] Desk Expense Claim form shows same links

## Knowledge

- [ ] Knowledge search UI finds prior Service Reports / Problem Records by symptom / item
- [ ] Find similar from Machine Hub / Knowledge page

## Contracts

- [ ] Service Quotation / SO creates Service Contract draft
- [ ] Submitted contract sets current contract on Machine Installation
- [ ] Renewal followup within lead days

## Deprecation

- [ ] Service Call form shows deprecated notice and links to SPA / HD Ticket
- [ ] Workspace does not promote Service Call as primary intake
