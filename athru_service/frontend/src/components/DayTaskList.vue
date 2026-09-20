<template>
  <div class="space-y-4">
    <div class="flex items-center justify-between">
      <h2 class="text-sm font-semibold text-athru-ink">Day-wise tasks</h2>
      <button class="athru-btn-primary" @click="showForm = !showForm">
        {{ showForm ? "Cancel" : "Add task" }}
      </button>
    </div>

    <form v-if="showForm" class="athru-card p-4 grid gap-3 md:grid-cols-2" @submit.prevent="submit">
      <label class="text-sm">
        <span class="text-athru-muted">Subject</span>
        <input v-model="form.subject" required class="mt-1 w-full border border-athru-line rounded-lg px-3 py-2" />
      </label>
      <label class="text-sm">
        <span class="text-athru-muted">Work date</span>
        <input v-model="form.work_date" type="date" class="mt-1 w-full border border-athru-line rounded-lg px-3 py-2" />
      </label>
      <label class="text-sm md:col-span-2">
        <span class="text-athru-muted">Description</span>
        <textarea v-model="form.description" rows="3" class="mt-1 w-full border border-athru-line rounded-lg px-3 py-2" />
      </label>
      <div class="md:col-span-2">
        <button type="submit" class="athru-btn-primary" :disabled="saving">Save task</button>
      </div>
    </form>

    <div v-for="group in grouped" :key="group.date" class="space-y-2">
      <div class="text-xs font-semibold uppercase tracking-wide text-athru-muted">
        {{ group.date || "Unscheduled" }}
      </div>
      <div
        v-for="t in group.tasks"
        :key="t.name"
        class="athru-card p-3 flex items-start justify-between gap-3"
      >
        <div>
          <div class="font-medium">{{ t.subject }}</div>
          <div class="text-sm text-athru-muted mt-0.5">{{ t.description || t.status }}</div>
        </div>
        <StatusBadge :status="t.status" />
      </div>
    </div>
    <p v-if="!tasks?.length" class="text-sm text-athru-muted">No tasks logged for this visit.</p>
  </div>
</template>

<script setup>
import { computed, reactive, ref } from "vue";
import StatusBadge from "./StatusBadge.vue";
import { call } from "../lib/api";

const props = defineProps({
  visit: { type: String, required: true },
  tasks: { type: Array, default: () => [] },
});
const emit = defineEmits(["created"]);

const showForm = ref(false);
const saving = ref(false);
const form = reactive({
  subject: "",
  work_date: new Date().toISOString().slice(0, 10),
  description: "",
});

const grouped = computed(() => {
  const map = {};
  for (const t of props.tasks || []) {
    const d = t.custom_work_date || "Unscheduled";
    if (!map[d]) map[d] = [];
    map[d].push(t);
  }
  return Object.keys(map)
    .sort()
    .reverse()
    .map((date) => ({ date, tasks: map[date] }));
});

async function submit() {
  saving.value = true;
  try {
    await call("athru_service.api.spa.create_visit_task", {
      visit: props.visit,
      subject: form.subject,
      work_date: form.work_date,
      description: form.description,
    });
    form.subject = "";
    form.description = "";
    showForm.value = false;
    emit("created");
  } finally {
    saving.value = false;
  }
}
</script>
