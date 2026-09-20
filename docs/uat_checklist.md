# Athru Service — UAT Checklist

Use the customer's Company / Item / Serial data on their site. Do not commit OEM names into the app.

## Setup

- [ ] App installed on ERPNext v16 site; migrate + build succeeded
- [ ] Roles assigned; Athru Service workspace visible
- [ ] Brand lint clean in app repo (`python scripts/brand_lint.py`)

## Dispatch → Commission

- [ ] Create Installed Equipment with Serial No (+ Project if used)
- [ ] Log Dispatched activity with invoice attachment
- [ ] Log Received / Goods Inward with attachment
- [ ] Log User Manual Sent; file retrievable from activity and equipment
- [ ] Log day-wise Installation Progress with service personnel
- [ ] Log Installation Acceptance with signed certificate; status = Commissioned

## Service Call

- [ ] Register Service Call via list dialog; number is `YYMMDD-##`
- [ ] Serial / Installed Equipment typeahead works
- [ ] Call appears on Installed Equipment lifetime history
- [ ] Create Maintenance Visit from call; create Service Report from visit/call

## Knowledge

- [ ] Submit Service Report with problem codes, root cause, corrective action
- [ ] Problem Record created (promote)
- [ ] Find Similar Problems returns the prior solution on another unit / same model

## Contracts

- [ ] Service Quotation creates Service Contract draft
- [ ] Submitted contract sets current contract on Installed Equipment
- [ ] Renewal followup appears when end date is within lead days (or simulate date)

## Configuration

- [ ] Fresh site can run using only after_install defaults + user-created masters
- [ ] Checklist Template loads into Checklist Response
- [ ] Central Desk Only blocks non-desk roles from creating calls
