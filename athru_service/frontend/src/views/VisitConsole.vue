<template>
  <div class="space-y-6">
    <div v-if="loading" class="text-sm text-athru-muted">Loading visit…</div>
    <template v-else-if="data">
      <EntityHeader
        eyebrow="Visit console"
        :title="data.visit?.customer || data.visit?.name"
        :subtitle="data.visit?.purpose || 'Field visit'"
      >
        <template #actions>
          <button class="athru-btn-primary" @click="createExpense">Add expense</button>
          <a :href="deskUrl('Maintenance Visit', data.visit?.name)" class="athru-btn-ghost" target="_blank">
            Open in Desk
          </a>
        </template>
        <template #meta>
          <span>Ticket: {{ data.visit?.custom_hd_ticket || "—" }}</span>
          <span>Machine: {{ data.visit?.custom_machine_installation || "—" }}</span>
          <StatusBadge :status="data.visit?.completion_status" />
        </template>
      </EntityHeader>

      <div class="grid gap-6 lg:grid-cols-2">
        <DayTaskList :visit="name" :tasks="data.tasks" @created="reload" />
        <section class="space-y-4">
          <div class="athru-card p-4">
            <h3 class="text-sm font-semibold">Reports</h3>
            <ul class="mt-2 space-y-2 text-sm">
              <li v-for="r in data.installation_reports" :key="r.name">
                Installation Report · {{ r.name }} · {{ r.status }}
              </li>
              <li v-for="r in data.service_reports" :key="r.name">
                Service Report · {{ r.name }} · {{ r.docstatus === 1 ? "Submitted" : "Draft" }}
              </li>
              <li
                v-if="!data.installation_reports?.length && !data.service_reports?.length"
                class="text-athru-muted"
              >
                No reports yet.
              </li>
            </ul>
          </div>
          <div class="athru-card p-4">
            <h3 class="text-sm font-semibold">Expenses</h3>
            <ul class="mt-2 space-y-2 text-sm">
              <li v-for="e in data.expenses" :key="e.name">
                {{ e.name }} · {{ e.total_claimed_amount || 0 }} · {{ e.approval_status || e.status }}
              </li>
              <li v-if="!data.expenses?.length" class="text-athru-muted">No expense claims linked.</li>
            </ul>
          </div>
        </section>
      </div>
    </template>
  </div>
</template>

<script setup>
import { onMounted, ref, watch } from "vue";
import EntityHeader from "../components/EntityHeader.vue";
import StatusBadge from "../components/StatusBadge.vue";
import DayTaskList from "../components/DayTaskList.vue";
import { call, deskUrl } from "../lib/api";

const props = defineProps({ name: String });
const data = ref(null);
const loading = ref(true);

async function reload() {
  loading.value = true;
  try {
    data.value = await call("athru_service.api.spa.get_visit_console", { name: props.name });
  } finally {
    loading.value = false;
  }
}

async function createExpense() {
  const name = await call("athru_service.api.spa.create_expense_for_visit", {
    visit: props.name,
  });
  if (name) window.open(deskUrl("Expense Claim", name), "_blank");
  await reload();
}

onMounted(reload);
watch(() => props.name, reload);
</script>
