# Athru Service

Brand-neutral field service framework for ETO/MTO equipment companies on **ERPNext v16** + **Helpdesk**.

## What it does

- **Athru Service SPA** (`/athru-service`) — primary operator UX (frappe-ui / Vue)
- **Machine Installation** — lifetime hub per Serial No (+ optional Project)
- **HD Ticket** — Service Request (Installation / Breakdown / PMC / …)
- **Maintenance Visit + Tasks** — field execution with day-wise work log
- **Installation Report / Service Report** — commissioning sign-off vs support RCA
- **Service Contract** — AMC / CAMC / PMC / Extended Warranty
- **Problem Code / Problem Record** — searchable knowledge
- **Checklist Template / Response** — org-built install & PM forms
- **Expense Claim** chain — Visit → Ticket → Machine Installation

`Service Call` remains in the app as a **deprecated** DocType (read-only migration path).

## Install

```bash
cd /path/to/frappe-bench
bench get-app <git-url-or-path>
bench --site <site> install-app athru_service
bench --site <site> migrate
# Frontend SPA
cd apps/athru_service/athru_service/frontend && yarn && yarn build
bench build --app athru_service
```

Requires `erpnext` and `helpdesk`.

## Configure (any company)

1. Open **Athru Service Settings** — intake mode, `YYMMDD-##` display numbers, renewal lead days.
2. Seed / extend **HD Ticket Types**, **Equipment Activity Types**, **Problem Codes**, **Checklist Templates**.
3. Assign roles: Service Manager, Service Desk Agent, Service Engineer, Service Read Only.
4. Open `/athru-service` for the SPA happy path.

Optional demo data (development only):

```bash
bench --site <site> execute athru_service.setup.demo.load_demo_seed
```

## Branding rules

This repository must not contain customer or OEM brand names. Prints use the ERPNext **Company** master. Run:

```bash
python scripts/brand_lint.py
```

## Docs

See [docs/admin_guide.md](docs/admin_guide.md) and [docs/uat_checklist.md](docs/uat_checklist.md).

## License

MIT — Athru
