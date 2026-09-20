<template>
  <div class="min-h-full flex bg-athru-surface">
    <aside class="w-60 shrink-0 border-r border-athru-line bg-white flex flex-col">
      <div class="px-5 py-5 border-b border-athru-line">
        <div class="text-xs uppercase tracking-[0.16em] text-athru-muted">Athru</div>
        <div class="text-lg font-semibold text-athru-ink">Service</div>
      </div>
      <nav class="p-3 space-y-1 flex-1">
        <RouterLink
          v-for="item in nav"
          :key="item.to"
          :to="item.to"
          class="block rounded-lg px-3 py-2.5 text-sm text-slate-600 hover:bg-slate-50"
          active-class="!bg-athru-accentSoft !text-athru-accent font-medium"
        >
          {{ item.label }}
        </RouterLink>
      </nav>
      <div class="p-4 border-t border-athru-line text-xs text-athru-muted">
        Desk forms available for admin escape hatch.
      </div>
    </aside>
    <main class="flex-1 min-w-0">
      <header class="h-14 border-b border-athru-line bg-white/80 backdrop-blur px-6 flex items-center justify-between">
        <div class="text-sm text-athru-muted">Equipment field service</div>
        <a href="/app" class="athru-btn-ghost text-xs">Open Desk</a>
      </header>
      <div class="p-6">
        <RouterView />
      </div>
    </main>
  </div>
</template>

<script setup>
const nav = [
  { to: "/", label: "Ops dashboard" },
  { to: "/machines", label: "Machine installations" },
  { to: "/service-requests", label: "Service requests" },
  { to: "/contracts", label: "Contracts" },
  { to: "/expenses", label: "Expenses" },
  { to: "/knowledge", label: "Knowledge search" },
];
</script>
