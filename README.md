# Athru Service

Brand-neutral field service framework for ETO/MTO equipment companies on **ERPNext v16**.

## What it does

- **Installed Equipment** — lifetime hub per Serial No (+ optional Project)
- **Equipment Activity** — day-wise dispatch → install → acceptance diary with attachments
- **Service Call** — field intake with configurable `YYMMDD-##` numbering (not a ticket system)
- **Service Report** — problem, root cause, corrective action, parts
- **Service Contract** — AMC / CAMC / PMC / Extended Warranty
- **Problem Code / Problem Record** — searchable knowledge (by machine and by problem)
- **Checklist Template / Response** — configurable install & PM forms

## Install

```bash
cd /path/to/frappe-bench
bench get-app /path/to/athru_service
# or: bench get-app <git-url>
bench --site <site> install-app athru_service
bench --site <site> migrate
bench build --app athru_service
```

Requires `erpnext` (v16+).

## Configure (any company)

1. Open **Athru Service Settings** — call intake mode, naming, renewal lead days.
2. Review seeded **Equipment Activity Type**, **Service Call Type**, **Problem Code** (edit/add freely).
3. Create **Checklist Templates** for your product families.
4. Assign roles: Service Manager, Service Desk Agent, Service Engineer, Service Read Only.

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
