<template>
  <div class="space-y-6">
    <div v-if="loading" class="text-sm text-athru-muted">Loading hub…</div>
    <template v-else-if="hub">
      <EntityHeader
        eyebrow="Machine installation"
        :title="hub.machine?.equipment_name || hub.machine?.name"
        :subtitle="hub.machine?.customer"
      >
        <template #actions>
          <button class="athru-btn-primary" @click="openRequest = true">New service request</button>
          <a :href="deskUrl('Machine Installation', hub.machine?.name)" class="athru-btn-ghost" target="_blank">
            Open in Desk
          </a>
        </template>
        <template #meta>
          <span>Serial: {{ hub.machine?.serial_no || "—" }}</span>
          <span>Item: {{ hub.machine?.item_code || "—" }}</span>
          <StatusBadge :status="hub.machine?.status" />
        </template>
      </EntityHeader>

      <div class="grid gap-6 lg:grid-cols-[1fr_320px]">
        <section>
          <h2 class="text-sm font-semibold mb-3">Lifetime timeline</h2>
          <Timeline :items="hub.timeline" />
        </section>
        <aside class="space-y-4">
          <div class="athru-card p-4">
            <h3 class="text-sm font-semibold">Quick actions</h3>
            <div class="mt-3 flex flex-col gap-2">
              <button class="athru-btn-ghost justify-start" @click="openRequest = true">Log service request</button>
              <RouterLink to="/knowledge" class="athru-btn-ghost justify-start">Find similar problems</RouterLink>
            </div>
          </div>
          <div class="athru-card p-4">
            <h3 class="text-sm font-semibold">Open requests</h3>
            <ul class="mt-2 space-y-2 text-sm">
              <li v-for="t in hub.tickets" :key="t.name">
                {{ t.subject || t.name }} · {{ t.status }}
              </li>
              <li v-if="!hub.tickets?.length" class="text-athru-muted">None</li>
            </ul>
          </div>
        </aside>
      </div>

      <div
        v-if="openRequest"
        class="fixed inset-0 z-40 bg-slate-900/40 flex items-end sm:items-center justify-center p-4"
        @click.self="openRequest = false"
      >
        <form class="athru-card w-full max-w-lg p-5 space-y-3" @submit.prevent="createRequest">
          <h3 class="font-semibold text-lg">New service request</h3>
          <label class="block text-sm">
            <span class="text-athru-muted">Subject</span>
            <input v-model="req.subject" required class="mt-1 w-full border border-athru-line rounded-lg px-3 py-2" />
          </label>
          <label class="block text-sm">
            <span class="text-athru-muted">Ticket type</span>
            <select v-model="req.ticket_type" class="mt-1 w-full border border-athru-line rounded-lg px-3 py-2">
              <option>Breakdown</option>
              <option>Installation</option>
              <option>PMC</option>
              <option>Contract</option>
              <option>Billable</option>
            </select>
          </label>
          <label class="block text-sm">
            <span class="text-athru-muted">Description</span>
            <textarea v-model="req.description" rows="4" class="mt-1 w-full border border-athru-line rounded-lg px-3 py-2" />
          </label>
          <div class="flex justify-end gap-2 pt-2">
            <button type="button" class="athru-btn-ghost" @click="openRequest = false">Cancel</button>
            <button type="submit" class="athru-btn-primary" :disabled="saving">Create</button>
          </div>
        </form>
      </div>
    </template>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref, watch } from "vue";
import EntityHeader from "../components/EntityHeader.vue";
import StatusBadge from "../components/StatusBadge.vue";
import Timeline from "../components/Timeline.vue";
import { call, deskUrl } from "../lib/api";

const props = defineProps({ name: String });
const hub = ref(null);
const loading = ref(true);
const openRequest = ref(false);
const saving = ref(false);
const req = reactive({ subject: "", ticket_type: "Breakdown", description: "" });

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
</script>
