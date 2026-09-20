<template>
  <div class="space-y-6">
    <EntityHeader
      eyebrow="Knowledge"
      title="Find similar problems"
      subtitle="Search closed service requests and service reports by symptom text."
    />
    <form class="athru-card p-4 flex flex-wrap gap-3" @submit.prevent="search">
      <input
        v-model="q"
        placeholder="Describe the symptom or fault…"
        class="flex-1 min-w-[220px] border border-athru-line rounded-lg px-3 py-2"
      />
      <input
        v-model="item"
        placeholder="Item code (optional)"
        class="w-48 border border-athru-line rounded-lg px-3 py-2"
      />
      <button class="athru-btn-primary" type="submit" :disabled="loading">Search</button>
    </form>

    <div class="space-y-3">
      <article v-for="hit in results" :key="hit.name + hit.doctype" class="athru-card p-4">
        <div class="flex items-center gap-2 text-xs uppercase tracking-wide text-athru-accent">
          {{ hit.doctype }}
          <StatusBadge :status="hit.status" />
        </div>
          <div class="font-medium mt-1">{{ hit.title || hit.subject || hit.name }}</div>
        <p class="text-sm text-athru-muted mt-1">{{ hit.solution || hit.root_cause || hit.snippet }}</p>
        <a
          v-if="hit.doctype && hit.name"
          :href="deskUrl(hit.doctype, hit.name)"
          class="text-xs text-athru-accent mt-2 inline-block"
          target="_blank"
        >
          Open →
        </a>
      </article>
      <p v-if="searched && !results.length" class="text-sm text-athru-muted text-center py-8">
        No similar records found.
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue";
import EntityHeader from "../components/EntityHeader.vue";
import StatusBadge from "../components/StatusBadge.vue";
import { call, deskUrl } from "../lib/api";

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
</script>
