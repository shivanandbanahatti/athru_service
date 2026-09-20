<template>
  <div class="space-y-6">
    <EntityHeader
      eyebrow="Operations"
      title="Ops dashboard"
      subtitle="Open requests, visits today, expiring contracts, and your tasks."
    />
    <div v-if="loading" class="text-sm text-athru-muted">Loading…</div>
    <div v-else class="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
      <section class="athru-card p-4">
        <div class="text-xs uppercase text-athru-muted">Open service requests</div>
        <div class="text-3xl font-semibold mt-2">{{ data.open_requests?.length || 0 }}</div>
        <ul class="mt-3 space-y-2 text-sm">
          <li v-for="r in (data.open_requests || []).slice(0, 5)" :key="r.name">
            <span class="font-medium">{{ r.subject || r.name }}</span>
            <span class="text-athru-muted"> · {{ r.status }}</span>
          </li>
        </ul>
      </section>
      <section class="athru-card p-4">
        <div class="text-xs uppercase text-athru-muted">Visits today</div>
        <div class="text-3xl font-semibold mt-2">{{ data.visits_today?.length || 0 }}</div>
        <ul class="mt-3 space-y-2 text-sm">
          <li v-for="v in (data.visits_today || []).slice(0, 5)" :key="v.name">
            <RouterLink :to="`/visits/${encodeURIComponent(v.name)}`" class="text-athru-accent">
              {{ v.customer || v.name }}
            </RouterLink>
          </li>
        </ul>
      </section>
      <section class="athru-card p-4">
        <div class="text-xs uppercase text-athru-muted">Contracts expiring</div>
        <div class="text-3xl font-semibold mt-2">{{ data.contracts_expiring?.length || 0 }}</div>
        <ul class="mt-3 space-y-2 text-sm">
          <li v-for="c in (data.contracts_expiring || []).slice(0, 5)" :key="c.name">
            {{ c.customer || c.name }} · {{ c.end_date }}
          </li>
        </ul>
      </section>
      <section class="athru-card p-4">
        <div class="text-xs uppercase text-athru-muted">My open tasks</div>
        <div class="text-3xl font-semibold mt-2">{{ data.my_tasks?.length || 0 }}</div>
        <ul class="mt-3 space-y-2 text-sm">
          <li v-for="t in (data.my_tasks || []).slice(0, 5)" :key="t.name">
            {{ t.subject }}
          </li>
        </ul>
      </section>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from "vue";
import EntityHeader from "../components/EntityHeader.vue";
import { call } from "../lib/api";

const loading = ref(true);
const data = ref({});

onMounted(async () => {
  try {
    data.value = (await call("athru_service.api.spa.get_ops_dashboard")) || {};
  } finally {
    loading.value = false;
  }
});
</script>
