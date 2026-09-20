<template>
  <div class="athru-card p-5">
    <div class="flex flex-wrap items-start justify-between gap-4">
      <div>
        <div class="text-xs uppercase tracking-wide text-athru-muted">{{ eyebrow }}</div>
        <h1 class="text-2xl font-semibold text-athru-ink mt-1">{{ title }}</h1>
        <p v-if="subtitle" class="text-sm text-athru-muted mt-1">{{ subtitle }}</p>
      </div>
      <div class="flex flex-wrap gap-2">
        <slot name="actions" />
      </div>
    </div>
    <div v-if="$slots.meta" class="mt-4 flex flex-wrap gap-3 text-sm text-slate-600">
      <slot name="meta" />
    </div>
  </div>
</template>

<script setup>
defineProps({
  eyebrow: { type: String, default: "" },
  title: { type: String, required: true },
  subtitle: { type: String, default: "" },
});
</script>
