<template>
  <span
    class="inline-flex items-center rounded-md px-2 py-0.5 text-xs font-medium"
    :class="toneClass"
  >
    {{ status || "—" }}
  </span>
</template>

<script setup>
import { computed } from "vue";
const props = defineProps({ status: String });
const toneClass = computed(() => {
  const s = (props.status || "").toLowerCase();
  if (["open", "planned", "draft", "to visit"].some((x) => s.includes(x)))
    return "bg-amber-50 text-amber-800";
  if (["progress", "working", "replied"].some((x) => s.includes(x)))
    return "bg-sky-50 text-sky-800";
  if (["closed", "completed", "resolved", "commissioned"].some((x) => s.includes(x)))
    return "bg-emerald-50 text-emerald-800";
  return "bg-slate-100 text-slate-700";
});
</script>
