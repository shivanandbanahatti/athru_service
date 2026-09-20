<template>
  <div class="space-y-6">
    <EntityHeader
      eyebrow="Service desk"
      title="Service requests"
      subtitle="HD Ticket backlog presented in equipment context."
    >
      <template #actions>
        <div class="flex rounded-lg border border-athru-line overflow-hidden text-sm">
          <button
            class="px-3 py-2"
            :class="view === 'board' ? 'bg-athru-accentSoft text-athru-accent' : 'bg-white'"
            @click="view = 'board'"
          >
            Board
          </button>
          <button
            class="px-3 py-2 border-l border-athru-line"
            :class="view === 'list' ? 'bg-athru-accentSoft text-athru-accent' : 'bg-white'"
            @click="view = 'list'"
          >
            List
          </button>
        </div>
      </template>
    </EntityHeader>

    <div v-if="view === 'board'" class="grid gap-4 md:grid-cols-3 xl:grid-cols-4">
      <section v-for="col in columns" :key="col" class="athru-card p-3 min-h-[240px]">
        <div class="text-xs font-semibold uppercase tracking-wide text-athru-muted px-1 mb-3">
          {{ col }}
        </div>
        <div class="space-y-2">
          <article
            v-for="t in byStatus[col] || []"
            :key="t.name"
            class="rounded-lg border border-athru-line bg-white p-3 shadow-sm"
          >
            <div class="font-medium text-sm">{{ t.subject || t.name }}</div>
            <div class="text-xs text-athru-muted mt-1">
              {{ t.ticket_type || "—" }} · {{ t.custom_machine_installation || t.customer || "—" }}
            </div>
            <a
              :href="deskUrl('HD Ticket', t.name)"
              class="text-xs text-athru-accent mt-2 inline-block"
              target="_blank"
            >
              Open ticket
            </a>
          </article>
        </div>
      </section>
    </div>

    <div v-else class="athru-card overflow-hidden">
      <table class="w-full text-sm">
        <thead class="bg-slate-50 text-left text-athru-muted">
          <tr>
            <th class="px-4 py-3">Subject</th>
            <th class="px-4 py-3">Type</th>
            <th class="px-4 py-3">Machine</th>
            <th class="px-4 py-3">Status</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="t in tickets" :key="t.name" class="border-t border-athru-line">
            <td class="px-4 py-3">
              <a :href="deskUrl('HD Ticket', t.name)" class="text-athru-accent" target="_blank">
                {{ t.subject || t.name }}
              </a>
            </td>
            <td class="px-4 py-3">{{ t.ticket_type || "—" }}</td>
            <td class="px-4 py-3">{{ t.custom_machine_installation || "—" }}</td>
            <td class="px-4 py-3"><StatusBadge :status="t.status" /></td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from "vue";
import EntityHeader from "../components/EntityHeader.vue";
import StatusBadge from "../components/StatusBadge.vue";
import { call, deskUrl } from "../lib/api";

const tickets = ref([]);
const view = ref("board");
const columns = ["Open", "Replied", "Resolved", "Closed"];

const byStatus = computed(() => {
  const map = {};
  for (const t of tickets.value) {
    const key = columns.find((c) => (t.status || "").toLowerCase().includes(c.toLowerCase())) || "Open";
    if (!map[key]) map[key] = [];
    map[key].push(t);
  }
  return map;
});

onMounted(async () => {
  tickets.value = (await call("athru_service.api.spa.list_service_requests")) || [];
});
</script>
