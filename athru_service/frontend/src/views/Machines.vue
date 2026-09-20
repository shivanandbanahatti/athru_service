<template>
  <div class="space-y-6">
    <EntityHeader
      eyebrow="Fleet"
      title="Machine installations"
      subtitle="Customer + serial hubs for lifetime service history."
    >
      <template #actions>
        <a :href="deskUrl('Machine Installation')" class="athru-btn-ghost" target="_blank">
          New in Desk
        </a>
      </template>
    </EntityHeader>

    <div class="athru-card overflow-hidden">
      <table class="w-full text-sm">
        <thead class="bg-slate-50 text-left text-athru-muted">
          <tr>
            <th class="px-4 py-3 font-medium">Machine</th>
            <th class="px-4 py-3 font-medium">Customer</th>
            <th class="px-4 py-3 font-medium">Serial</th>
            <th class="px-4 py-3 font-medium">Status</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="m in machines"
            :key="m.name"
            class="border-t border-athru-line hover:bg-slate-50 cursor-pointer"
            @click="$router.push(`/machines/${encodeURIComponent(m.name)}`)"
          >
            <td class="px-4 py-3 font-medium">{{ m.equipment_name || m.name }}</td>
            <td class="px-4 py-3">{{ m.customer }}</td>
            <td class="px-4 py-3">{{ m.serial_no || "—" }}</td>
            <td class="px-4 py-3"><StatusBadge :status="m.status" /></td>
          </tr>
        </tbody>
      </table>
      <p v-if="!loading && !machines.length" class="p-8 text-center text-athru-muted text-sm">
        No machine installations yet. Create one from a Delivery Note or Desk.
      </p>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from "vue";
import EntityHeader from "../components/EntityHeader.vue";
import StatusBadge from "../components/StatusBadge.vue";
import { call, deskUrl } from "../lib/api";

const machines = ref([]);
const loading = ref(true);

onMounted(async () => {
  try {
    machines.value = (await call("athru_service.api.spa.list_machine_installations")) || [];
  } finally {
    loading.value = false;
  }
});
</script>
