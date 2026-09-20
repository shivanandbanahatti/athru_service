<template>
  <div class="space-y-6">
    <EntityHeader
      eyebrow="Field expenses"
      title="Expense claims"
      subtitle="Claims linked Visit → Service Request → Machine Installation."
    />
    <div class="athru-card overflow-hidden">
      <table class="w-full text-sm">
        <thead class="bg-slate-50 text-left text-athru-muted">
          <tr>
            <th class="px-4 py-3">Claim</th>
            <th class="px-4 py-3">Visit</th>
            <th class="px-4 py-3">Ticket</th>
            <th class="px-4 py-3">Machine</th>
            <th class="px-4 py-3">Amount</th>
            <th class="px-4 py-3">Status</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="e in expenses" :key="e.name" class="border-t border-athru-line">
            <td class="px-4 py-3">
              <a :href="deskUrl('Expense Claim', e.name)" class="text-athru-accent" target="_blank">
                {{ e.name }}
              </a>
            </td>
            <td class="px-4 py-3">
              <RouterLink
                v-if="e.custom_maintenance_visit"
                :to="`/visits/${encodeURIComponent(e.custom_maintenance_visit)}`"
                class="text-athru-accent"
              >
                {{ e.custom_maintenance_visit }}
              </RouterLink>
              <span v-else>—</span>
            </td>
            <td class="px-4 py-3">{{ e.custom_hd_ticket || "—" }}</td>
            <td class="px-4 py-3">{{ e.custom_machine_installation || "—" }}</td>
            <td class="px-4 py-3">{{ e.total_claimed_amount || 0 }}</td>
            <td class="px-4 py-3"><StatusBadge :status="e.approval_status || e.status" /></td>
          </tr>
        </tbody>
      </table>
      <p v-if="!loading && !expenses.length" class="p-8 text-center text-sm text-athru-muted">
        No linked expense claims yet.
      </p>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from "vue";
import EntityHeader from "../components/EntityHeader.vue";
import StatusBadge from "../components/StatusBadge.vue";
import { call, deskUrl } from "../lib/api";

const expenses = ref([]);
const loading = ref(true);

onMounted(async () => {
  try {
    expenses.value = (await call("athru_service.api.spa.list_expenses")) || [];
  } finally {
    loading.value = false;
  }
});
</script>
