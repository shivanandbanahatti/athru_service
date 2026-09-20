/**
 * Athru Service SPA (CDN Vue build — no bundler required).
 * Prefer rebuilding from ../frontend with `yarn build` when Node is available.
 */
import { createApp, computed, onMounted, reactive, ref, watch } from "https://unpkg.com/vue@3.4.21/dist/vue.esm-browser.prod.js";
import { createRouter, createWebHistory, RouterLink, RouterView } from "https://unpkg.com/vue-router@4.3.0/dist/vue-router.esm-browser.js";

async function call(method, args = {}) {
  if (window.frappe?.call) {
    const r = await window.frappe.call({ method, args });
    return r.message;
  }
  const res = await fetch("/api/method/" + method, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-Frappe-CSRF-Token": window.csrf_token || "",
    },
    body: JSON.stringify(args),
    credentials: "include",
  });
  const data = await res.json();
  if (data.exc) throw new Error(data._server_messages || data.exc);
  return data.message;
}

function deskUrl(doctype, name) {
  const slug = doctype.toLowerCase().replace(/ /g, "-");
  return name ? `/app/${slug}/${encodeURIComponent(name)}` : `/app/${slug}`;
}

function statusClass(status) {
  const s = (status || "").toLowerCase();
  if (["open", "planned", "draft", "to visit"].some((x) => s.includes(x))) return "badge amber";
  if (["progress", "working", "replied"].some((x) => s.includes(x))) return "badge sky";
  if (["closed", "completed", "resolved", "commissioned", "active"].some((x) => s.includes(x)))
    return "badge green";
  return "badge gray";
}

const StatusBadge = {
  props: ["status"],
  template: `<span :class="cls">{{ status || "—" }}</span>`,
  setup(props) {
    return { cls: computed(() => statusClass(props.status)) };
  },
};

const Home = {
  components: { StatusBadge },
  template: `
  <div>
    <header class="entity">
      <div class="eyebrow">Operations</div>
      <h1>Ops dashboard</h1>
      <p class="muted">Open requests, visits today, expiring contracts, and your tasks.</p>
    </header>
    <div v-if="loading" class="muted">Loading…</div>
    <div v-else class="grid4">
      <section class="card" v-for="panel in panels" :key="panel.title">
        <div class="eyebrow">{{ panel.title }}</div>
        <div class="stat">{{ panel.count }}</div>
        <ul class="list">
          <li v-for="(row,i) in panel.rows" :key="i">{{ row }}</li>
        </ul>
      </section>
    </div>
  </div>`,
  setup() {
    const loading = ref(true);
    const data = ref({});
    onMounted(async () => {
      try {
        data.value = (await call("athru_service.api.spa.get_ops_dashboard")) || {};
      } finally {
        loading.value = false;
      }
    });
    const panels = computed(() => {
      const d = data.value || {};
      return [
        {
          title: "Open service requests",
          count: (d.open_requests || []).length,
          rows: (d.open_requests || []).slice(0, 5).map((r) => `${r.subject || r.name} · ${r.status}`),
        },
        {
          title: "Visits today",
          count: (d.visits_today || []).length,
          rows: (d.visits_today || []).slice(0, 5).map((v) => v.customer || v.name),
        },
        {
          title: "Contracts expiring",
          count: (d.contracts_expiring || []).length,
          rows: (d.contracts_expiring || []).slice(0, 5).map((c) => `${c.customer || c.name} · ${c.end_date}`),
        },
        {
          title: "My open tasks",
          count: (d.my_tasks || []).length,
          rows: (d.my_tasks || []).slice(0, 5).map((t) => t.subject),
        },
      ];
    });
    return { loading, panels };
  },
};

const Machines = {
  components: { StatusBadge, RouterLink },
  template: `
  <div>
    <header class="entity">
      <div class="eyebrow">Fleet</div>
      <h1>Machine installations</h1>
    </header>
    <div class="card table-wrap">
      <table>
        <thead><tr><th>Machine</th><th>Customer</th><th>Serial</th><th>Status</th></tr></thead>
        <tbody>
          <tr v-for="m in machines" :key="m.name" @click="$router.push('/machines/'+encodeURIComponent(m.name))">
            <td><b>{{ m.equipment_name || m.name }}</b></td>
            <td>{{ m.customer }}</td>
            <td>{{ m.serial_no || "—" }}</td>
            <td><StatusBadge :status="m.status" /></td>
          </tr>
        </tbody>
      </table>
      <p v-if="!loading && !machines.length" class="empty">No machine installations yet.</p>
    </div>
  </div>`,
  setup() {
    const machines = ref([]);
    const loading = ref(true);
    onMounted(async () => {
      try {
        machines.value = (await call("athru_service.api.spa.list_machine_installations")) || [];
      } finally {
        loading.value = false;
      }
    });
    return { machines, loading };
  },
};

const MachineHub = {
  components: { StatusBadge },
  props: ["name"],
  template: `
  <div>
    <div v-if="loading" class="muted">Loading hub…</div>
    <template v-else-if="hub">
      <header class="entity row">
        <div>
          <div class="eyebrow">Machine installation</div>
          <h1>{{ hub.machine?.equipment_name || hub.machine?.name }}</h1>
          <p class="muted">{{ hub.machine?.customer }} · Serial {{ hub.machine?.serial_no || "—" }}</p>
          <StatusBadge :status="hub.machine?.status" />
        </div>
        <div class="actions">
          <button class="btn primary" @click="openRequest=true">New service request</button>
          <a class="btn ghost" :href="desk" target="_blank">Open in Desk</a>
        </div>
      </header>
      <div class="split">
        <section>
          <h2>Lifetime timeline</h2>
          <ol class="timeline">
            <li v-for="(item,idx) in hub.timeline || []" :key="idx" class="card">
              <div class="muted small">{{ item.date || "—" }}</div>
              <div class="eyebrow accent">{{ item.kind }}</div>
              <div><b>{{ item.title }}</b> <StatusBadge :status="item.status" /></div>
              <p class="muted" v-if="item.detail">{{ item.detail }}</p>
            </li>
            <li v-if="!(hub.timeline||[]).length" class="empty">No timeline events yet.</li>
          </ol>
        </section>
        <aside class="card">
          <h3>Open requests</h3>
          <ul class="list">
            <li v-for="t in hub.tickets || []" :key="t.name">{{ t.subject || t.name }} · {{ t.status }}</li>
            <li v-if="!(hub.tickets||[]).length" class="muted">None</li>
          </ul>
        </aside>
      </div>
      <div v-if="openRequest" class="modal" @click.self="openRequest=false">
        <form class="card modal-card" @submit.prevent="createRequest">
          <h3>New service request</h3>
          <label>Subject<input v-model="req.subject" required /></label>
          <label>Ticket type
            <select v-model="req.ticket_type">
              <option>Breakdown</option><option>Installation</option><option>PMC</option>
              <option>Contract</option><option>Billable</option>
            </select>
          </label>
          <label>Description<textarea v-model="req.description" rows="4"></textarea></label>
          <div class="actions">
            <button type="button" class="btn ghost" @click="openRequest=false">Cancel</button>
            <button class="btn primary" :disabled="saving">Create</button>
          </div>
        </form>
      </div>
    </template>
  </div>`,
  setup(props) {
    const hub = ref(null);
    const loading = ref(true);
    const openRequest = ref(false);
    const saving = ref(false);
    const req = reactive({ subject: "", ticket_type: "Breakdown", description: "" });
    const desk = computed(() => deskUrl("Machine Installation", props.name));
    async function load() {
      loading.value = true;
      try {
        hub.value = await call("athru_service.api.spa.get_machine_hub", { name: props.name });
      } finally {
        loading.value = false;
      }
    }
    async function createRequest() {
      saving.value = true;
      try {
        await call("athru_service.api.spa.create_service_request", {
          machine_installation: props.name,
          subject: req.subject,
          ticket_type: req.ticket_type,
          description: req.description,
        });
        openRequest.value = false;
        req.subject = "";
        req.description = "";
        await load();
      } finally {
        saving.value = false;
      }
    }
    onMounted(load);
    watch(() => props.name, load);
    return { hub, loading, openRequest, saving, req, desk, createRequest };
  },
};

const ServiceRequests = {
  components: { StatusBadge },
  template: `
  <div>
    <header class="entity row">
      <div>
        <div class="eyebrow">Service desk</div>
        <h1>Service requests</h1>
      </div>
      <div class="seg">
        <button :class="{on: view==='board'}" @click="view='board'">Board</button>
        <button :class="{on: view==='list'}" @click="view='list'">List</button>
      </div>
    </header>
    <div v-if="view==='board'" class="board">
      <section v-for="col in columns" :key="col" class="card">
        <div class="eyebrow">{{ col }}</div>
        <article v-for="t in byStatus[col] || []" :key="t.name" class="ticket">
          <b>{{ t.subject || t.name }}</b>
          <div class="muted small">{{ t.ticket_type || "—" }} · {{ t.custom_machine_installation || "—" }}</div>
          <a :href="deskUrl('HD Ticket', t.name)" target="_blank">Open ticket</a>
        </article>
      </section>
    </div>
    <div v-else class="card table-wrap">
      <table>
        <thead><tr><th>Subject</th><th>Type</th><th>Machine</th><th>Status</th></tr></thead>
        <tbody>
          <tr v-for="t in tickets" :key="t.name">
            <td><a :href="deskUrl('HD Ticket', t.name)" target="_blank">{{ t.subject || t.name }}</a></td>
            <td>{{ t.ticket_type || "—" }}</td>
            <td>{{ t.custom_machine_installation || "—" }}</td>
            <td><StatusBadge :status="t.status" /></td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>`,
  setup() {
    const tickets = ref([]);
    const view = ref("board");
    const columns = ["Open", "Replied", "Resolved", "Closed"];
    const byStatus = computed(() => {
      const map = {};
      for (const t of tickets.value) {
        const key =
          columns.find((c) => (t.status || "").toLowerCase().includes(c.toLowerCase())) || "Open";
        (map[key] ||= []).push(t);
      }
      return map;
    });
    onMounted(async () => {
      tickets.value = (await call("athru_service.api.spa.list_service_requests")) || [];
    });
    return { tickets, view, columns, byStatus, deskUrl };
  },
};

const VisitConsole = {
  components: { StatusBadge, RouterLink },
  props: ["name"],
  template: `
  <div>
    <div v-if="loading" class="muted">Loading visit…</div>
    <template v-else-if="data">
      <header class="entity row">
        <div>
          <div class="eyebrow">Visit console</div>
          <h1>{{ data.visit?.customer || data.visit?.name }}</h1>
          <p class="muted">Ticket {{ data.visit?.custom_hd_ticket || "—" }} · Machine {{ data.visit?.custom_machine_installation || "—" }}</p>
          <StatusBadge :status="data.visit?.completion_status" />
        </div>
        <div class="actions">
          <button class="btn primary" @click="createExpense">Add expense</button>
          <button class="btn ghost" @click="showTask=!showTask">Add task</button>
        </div>
      </header>
      <form v-if="showTask" class="card form" @submit.prevent="submitTask">
        <label>Subject<input v-model="task.subject" required /></label>
        <label>Work date<input type="date" v-model="task.work_date" /></label>
        <label>Description<textarea v-model="task.description" rows="3"></textarea></label>
        <button class="btn primary">Save task</button>
      </form>
      <div class="split">
        <section>
          <h2>Day-wise tasks</h2>
          <div v-for="g in grouped" :key="g.date" class="day">
            <div class="eyebrow">{{ g.date || "Unscheduled" }}</div>
            <div v-for="t in g.tasks" :key="t.name" class="card row">
              <div><b>{{ t.subject }}</b><div class="muted">{{ t.description || t.status }}</div></div>
              <StatusBadge :status="t.status" />
            </div>
          </div>
          <p v-if="!(data.tasks||[]).length" class="empty">No tasks logged.</p>
        </section>
        <aside>
          <div class="card">
            <h3>Reports</h3>
            <ul class="list">
              <li v-for="r in data.installation_reports || []" :key="r.name">Installation · {{ r.name }}</li>
              <li v-for="r in data.service_reports || []" :key="'s'+r.name">Service · {{ r.name }}</li>
            </ul>
          </div>
          <div class="card" style="margin-top:1rem">
            <h3>Expenses</h3>
            <ul class="list">
              <li v-for="e in data.expenses || []" :key="e.name">{{ e.name }} · {{ e.total_claimed_amount || 0 }}</li>
              <li v-if="!(data.expenses||[]).length" class="muted">None</li>
            </ul>
          </div>
        </aside>
      </div>
    </template>
  </div>`,
  setup(props) {
    const data = ref(null);
    const loading = ref(true);
    const showTask = ref(false);
    const task = reactive({
      subject: "",
      work_date: new Date().toISOString().slice(0, 10),
      description: "",
    });
    async function reload() {
      loading.value = true;
      try {
        data.value = await call("athru_service.api.spa.get_visit_console", { name: props.name });
      } finally {
        loading.value = false;
      }
    }
    const grouped = computed(() => {
      const map = {};
      for (const t of data.value?.tasks || []) {
        const d = t.custom_work_date || "Unscheduled";
        (map[d] ||= []).push(t);
      }
      return Object.keys(map)
        .sort()
        .reverse()
        .map((date) => ({ date, tasks: map[date] }));
    });
    async function submitTask() {
      await call("athru_service.api.spa.create_visit_task", {
        visit: props.name,
        subject: task.subject,
        work_date: task.work_date,
        description: task.description,
      });
      task.subject = "";
      task.description = "";
      showTask.value = false;
      await reload();
    }
    async function createExpense() {
      const name = await call("athru_service.api.spa.create_expense_for_visit", { visit: props.name });
      if (name) window.open(deskUrl("Expense Claim", name), "_blank");
      await reload();
    }
    onMounted(reload);
    watch(() => props.name, reload);
    return { data, loading, showTask, task, grouped, submitTask, createExpense };
  },
};

const Knowledge = {
  components: { StatusBadge },
  template: `
  <div>
    <header class="entity">
      <div class="eyebrow">Knowledge</div>
      <h1>Find similar problems</h1>
    </header>
    <form class="card form row" @submit.prevent="search">
      <input v-model="q" placeholder="Describe the symptom…" style="flex:1" />
      <input v-model="item" placeholder="Item code" style="width:10rem" />
      <button class="btn primary" :disabled="loading">Search</button>
    </form>
    <article v-for="hit in results" :key="hit.name+hit.doctype" class="card" style="margin-top:.75rem">
      <div class="eyebrow accent">{{ hit.doctype }} <StatusBadge :status="hit.status" /></div>
      <b>{{ hit.title || hit.subject || hit.name }}</b>
      <p class="muted">{{ hit.solution || hit.root_cause || hit.snippet }}</p>
      <a v-if="hit.name" :href="deskUrl(hit.doctype, hit.name)" target="_blank">Open →</a>
    </article>
    <p v-if="searched && !results.length" class="empty">No similar records found.</p>
  </div>`,
  setup() {
    const q = ref("");
    const item = ref("");
    const results = ref([]);
    const loading = ref(false);
    const searched = ref(false);
    async function search() {
      loading.value = true;
      searched.value = true;
      try {
        results.value =
          (await call("athru_service.api.knowledge.find_similar", {
            query: q.value,
            item_code: item.value || undefined,
          })) || [];
      } finally {
        loading.value = false;
      }
    }
    return { q, item, results, loading, searched, search, deskUrl };
  },
};

const Contracts = {
  components: { StatusBadge, RouterLink },
  template: `
  <div>
    <header class="entity"><div class="eyebrow">Commercial</div><h1>Service contracts</h1></header>
    <div class="card table-wrap">
      <table>
        <thead><tr><th>Contract</th><th>Customer</th><th>Machine</th><th>Type</th><th>Ends</th><th>Status</th></tr></thead>
        <tbody>
          <tr v-for="c in rows" :key="c.name">
            <td><a :href="deskUrl('Service Contract', c.name)" target="_blank">{{ c.name }}</a></td>
            <td>{{ c.customer || "—" }}</td>
            <td>
              <RouterLink v-if="c.machine_installation" :to="'/machines/'+encodeURIComponent(c.machine_installation)">{{ c.machine_installation }}</RouterLink>
              <span v-else>—</span>
            </td>
            <td>{{ c.contract_type || "—" }}</td>
            <td>{{ c.end_date || "—" }}</td>
            <td><StatusBadge :status="c.status" /></td>
          </tr>
        </tbody>
      </table>
      <p v-if="!loading && !rows.length" class="empty">No contracts.</p>
    </div>
  </div>`,
  setup() {
    const rows = ref([]);
    const loading = ref(true);
    onMounted(async () => {
      try {
        rows.value = (await call("athru_service.api.spa.list_service_contracts")) || [];
      } finally {
        loading.value = false;
      }
    });
    return { rows, loading, deskUrl };
  },
};

const Expenses = {
  components: { StatusBadge, RouterLink },
  template: `
  <div>
    <header class="entity"><div class="eyebrow">Field expenses</div><h1>Expense claims</h1></header>
    <div class="card table-wrap">
      <table>
        <thead><tr><th>Claim</th><th>Visit</th><th>Ticket</th><th>Machine</th><th>Amount</th><th>Status</th></tr></thead>
        <tbody>
          <tr v-for="e in rows" :key="e.name">
            <td><a :href="deskUrl('Expense Claim', e.name)" target="_blank">{{ e.name }}</a></td>
            <td>
              <RouterLink v-if="e.custom_maintenance_visit" :to="'/visits/'+encodeURIComponent(e.custom_maintenance_visit)">{{ e.custom_maintenance_visit }}</RouterLink>
              <span v-else>—</span>
            </td>
            <td>{{ e.custom_hd_ticket || "—" }}</td>
            <td>{{ e.custom_machine_installation || "—" }}</td>
            <td>{{ e.total_claimed_amount || 0 }}</td>
            <td><StatusBadge :status="e.approval_status || e.status" /></td>
          </tr>
        </tbody>
      </table>
      <p v-if="!loading && !rows.length" class="empty">No linked expenses.</p>
    </div>
  </div>`,
  setup() {
    const rows = ref([]);
    const loading = ref(true);
    onMounted(async () => {
      try {
        rows.value = (await call("athru_service.api.spa.list_expenses")) || [];
      } finally {
        loading.value = false;
      }
    });
    return { rows, loading, deskUrl };
  },
};

const App = {
  components: { RouterLink, RouterView },
  template: `
  <div class="shell">
    <aside>
      <div class="brand"><div class="eyebrow">Athru</div><div class="brand-title">Service</div></div>
      <nav>
        <RouterLink to="/">Ops dashboard</RouterLink>
        <RouterLink to="/machines">Machine installations</RouterLink>
        <RouterLink to="/service-requests">Service requests</RouterLink>
        <RouterLink to="/contracts">Contracts</RouterLink>
        <RouterLink to="/expenses">Expenses</RouterLink>
        <RouterLink to="/knowledge">Knowledge search</RouterLink>
      </nav>
      <div class="aside-foot muted small">Desk forms remain for admin escape hatch.</div>
    </aside>
    <main>
      <header class="top">
        <span class="muted">Equipment field service</span>
        <a class="btn ghost" href="/app">Open Desk</a>
      </header>
      <div class="content"><RouterView /></div>
    </main>
  </div>`,
};

const router = createRouter({
  history: createWebHistory("/athru-service"),
  routes: [
    { path: "/", component: Home },
    { path: "/machines", component: Machines },
    { path: "/machines/:name", component: MachineHub, props: true },
    { path: "/service-requests", component: ServiceRequests },
    { path: "/visits/:name", component: VisitConsole, props: true },
    { path: "/contracts", component: Contracts },
    { path: "/expenses", component: Expenses },
    { path: "/knowledge", component: Knowledge },
  ],
});

const style = document.createElement("style");
style.textContent = `
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600;700&display=swap');
:root{--ink:#0f172a;--muted:#64748b;--surface:#f8fafc;--accent:#0f766e;--line:#e2e8f0;--soft:#ccfbf1}
*{box-sizing:border-box}body{margin:0;font-family:'IBM Plex Sans',Segoe UI,system-ui,sans-serif;background:var(--surface);color:var(--ink)}
.shell{display:flex;min-height:100vh}aside{width:15rem;background:#fff;border-right:1px solid var(--line);display:flex;flex-direction:column}
.brand{padding:1.25rem;border-bottom:1px solid var(--line)}.brand-title{font-size:1.15rem;font-weight:600}
nav{padding:.75rem;display:flex;flex-direction:column;gap:.25rem;flex:1}
nav a{padding:.65rem .75rem;border-radius:.6rem;color:#475569;text-decoration:none;font-size:.9rem}
nav a.router-link-active{background:var(--soft);color:var(--accent);font-weight:500}
.aside-foot{padding:1rem;border-top:1px solid var(--line)}main{flex:1;min-width:0}
.top{height:3.5rem;display:flex;align-items:center;justify-content:space-between;padding:0 1.5rem;background:rgba(255,255,255,.85);border-bottom:1px solid var(--line);backdrop-filter:blur(6px)}
.content{padding:1.5rem}.entity{margin-bottom:1.25rem}.entity.row,.row{display:flex;justify-content:space-between;gap:1rem;align-items:flex-start;flex-wrap:wrap}
h1{margin:.2rem 0;font-size:1.6rem}h2,h3{margin:0 0 .75rem;font-size:1rem}.eyebrow{font-size:.7rem;text-transform:uppercase;letter-spacing:.08em;color:var(--muted)}.eyebrow.accent{color:var(--accent)}
.muted{color:var(--muted)}.small{font-size:.75rem}.card{background:#fff;border:1px solid var(--line);border-radius:.85rem;padding:1rem;box-shadow:0 1px 2px rgba(15,23,42,.05)}
.grid4{display:grid;gap:1rem;grid-template-columns:repeat(auto-fit,minmax(180px,1fr))}.stat{font-size:2rem;font-weight:600;margin:.35rem 0}
.list{margin:.5rem 0 0;padding-left:1rem;font-size:.875rem}.actions{display:flex;gap:.5rem;flex-wrap:wrap}
.btn{display:inline-flex;align-items:center;gap:.4rem;border-radius:.55rem;padding:.5rem .9rem;font-size:.875rem;font-weight:500;border:1px solid var(--line);background:#fff;color:var(--ink);cursor:pointer;text-decoration:none}
.btn.primary{background:var(--accent);border-color:var(--accent);color:#fff}.btn.ghost:hover{background:#f8fafc}
.badge{display:inline-flex;align-items:center;border-radius:.4rem;padding:.1rem .45rem;font-size:.7rem;font-weight:500}
.badge.amber{background:#fffbeb;color:#92400e}.badge.sky{background:#f0f9ff;color:#075985}.badge.green{background:#ecfdf5;color:#065f46}.badge.gray{background:#f1f5f9;color:#334155}
.table-wrap{padding:0;overflow:auto}table{width:100%;border-collapse:collapse;font-size:.875rem}th,td{padding:.75rem 1rem;text-align:left;border-top:1px solid var(--line)}
thead th{background:#f8fafc;color:var(--muted);font-weight:500;border-top:0}tbody tr{cursor:pointer}tbody tr:hover{background:#f8fafc}
.split{display:grid;gap:1.25rem;grid-template-columns:1fr}.split>aside{min-width:0}@media(min-width:960px){.split{grid-template-columns:1fr 18rem}}
.timeline{list-style:none;padding:0;margin:0;display:flex;flex-direction:column;gap:.75rem}.empty{text-align:center;color:var(--muted);padding:2rem;font-size:.875rem}
.modal{position:fixed;inset:0;background:rgba(15,23,42,.4);display:flex;align-items:center;justify-content:center;padding:1rem;z-index:40}
.modal-card{width:100%;max-width:28rem}.form label{display:block;font-size:.875rem;margin-bottom:.75rem}.form input,.form select,.form textarea{display:block;width:100%;margin-top:.35rem;border:1px solid var(--line);border-radius:.55rem;padding:.5rem .7rem;font:inherit}
.seg{display:flex;border:1px solid var(--line);border-radius:.55rem;overflow:hidden}.seg button{border:0;background:#fff;padding:.5rem .8rem;cursor:pointer}.seg button.on{background:var(--soft);color:var(--accent)}
.board{display:grid;gap:1rem;grid-template-columns:repeat(auto-fit,minmax(200px,1fr))}.ticket{border:1px solid var(--line);border-radius:.55rem;padding:.75rem;margin-top:.5rem;background:#fff}
.ticket a{font-size:.75rem;color:var(--accent)}.day{margin-bottom:1rem}a{color:var(--accent)}
`;
document.head.appendChild(style);

createApp(App).use(router).mount("#app");
