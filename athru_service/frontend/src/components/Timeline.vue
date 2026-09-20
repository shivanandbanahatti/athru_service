<template>
  <ol class="space-y-3">
    <li
      v-for="(item, idx) in items"
      :key="idx"
      class="athru-card p-4 flex gap-4"
    >
      <div class="w-24 shrink-0 text-xs text-athru-muted pt-0.5">
        {{ formatDate(item.date) }}
      </div>
      <div class="min-w-0 flex-1">
        <div class="flex items-center gap-2">
          <span class="text-[11px] uppercase tracking-wide text-athru-accent font-medium">
            {{ item.kind }}
          </span>
          <StatusBadge :status="item.status" />
        </div>
        <div class="font-medium text-athru-ink mt-1">{{ item.title }}</div>
        <p v-if="item.detail" class="text-sm text-athru-muted mt-0.5">{{ item.detail }}</p>
        <a
          v-if="item.doctype && item.name"
          :href="deskUrl(item.doctype, item.name)"
          class="text-xs text-athru-accent mt-2 inline-block"
          target="_blank"
        >
          Open in Desk →
        </a>
      </div>
    </li>
    <li v-if="!items?.length" class="text-sm text-athru-muted py-8 text-center">
      No timeline events yet.
    </li>
  </ol>
</template>

<script setup>
import StatusBadge from "./StatusBadge.vue";
import { deskUrl } from "../lib/api";

defineProps({
  items: { type: Array, default: () => [] },
});

function formatDate(d) {
  if (!d) return "—";
  try {
    return new Date(d).toLocaleDateString(undefined, {
      day: "2-digit",
      month: "short",
      year: "numeric",
    });
  } catch {
    return d;
  }
}
</script>
