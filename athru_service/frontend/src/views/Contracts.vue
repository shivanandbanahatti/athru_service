<template>
  <div class="space-y-6">
    <EntityHeader
      eyebrow="Commercial"
      title="Service contracts"
      subtitle="AMC / CAMC / PMC / Extended Warranty linked to machine installations."
    />
    <div class="athru-card overflow-hidden">
      <table class="w-full text-sm">
        <thead class="bg-slate-50 text-left text-athru-muted">
          <tr>
            <th class="px-4 py-3">Contract</th>
            <th class="px-4 py-3">Customer</th>
            <th class="px-4 py-3">Machine</th>
            <th class="px-4 py-3">Type</th>
            <th class="px-4 py-3">Ends</th>
            <th class="px-4 py-3">Status</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="c in contracts" :key="c.name" class="border-t border-athru-line">
            <td class="px-4 py-3">
              <a :href="deskUrl('Service Contract', c.name)" class="text-athru-accent" target="_blank">
                {{ c.name }}
              </a>
            </td>
            <td class="px-4 py-3">{{ c.customer || "—" }}</td>
            <td class="px-4 py-3">
              <RouterLink
                v-if="c.machine_installation"
                :to="`/machines/${encodeURIComponent(c.machine_installation)}`"
                class="text-athru-accent"
              >
                {{ c.machine_installation }}
              </RouterLink>
              <span v-else>—</span>
            </td>
            <td class="px-4 py-3">{{ c.contract_type || "—" }}</td>
            <td class="px-4 py-3">{{ c.end_date || "—" }}</td>
            <td class="px-4 py-3"><StatusBadge :status="c.status" /></td>
          </tr>
        </tbody>
      </table>
      <p v-if="!loading && !contracts.length" class="p-8 text-center text-sm text-athru-muted">
        No active contracts.
      </p>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from "vue";
import EntityHeader from "../components/EntityHeader.vue";
import StatusBadge from "../components/StatusBadge.vue";
import { call, deskUrl } from "../lib/api";

const contracts = ref([]);
const loading = ref(true);

onMounted(async () => {
  try {
    contracts.value = (await call("athru_service.api.spa.list_service_contracts")) || [];
  } finally {
    loading.value = false;
  }
});
</script>
