# Frontend (Athru Service SPA)

Vue 3 source under `src/` (Vite + Tailwind). Same stack family as Helpdesk/CRM.

**Shipped runtime:** `../public/frontend/athru_service.js` is a CDN Vue module that works without Node.
Prefer rebuilding when Node is available:

```bash
cd athru_service/frontend
yarn
yarn build
# outputs to ../public/frontend/
```

Website route: `/athru-service`.
