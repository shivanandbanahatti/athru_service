import { createRouter, createWebHistory } from "vue-router";
import Home from "./views/Home.vue";
import Machines from "./views/Machines.vue";
import MachineHub from "./views/MachineHub.vue";
import ServiceRequests from "./views/ServiceRequests.vue";
import VisitConsole from "./views/VisitConsole.vue";
import Knowledge from "./views/Knowledge.vue";
import Contracts from "./views/Contracts.vue";
import Expenses from "./views/Expenses.vue";

const routes = [
  { path: "/", name: "home", component: Home },
  { path: "/machines", name: "machines", component: Machines },
  { path: "/machines/:name", name: "machine-hub", component: MachineHub, props: true },
  { path: "/service-requests", name: "service-requests", component: ServiceRequests },
  { path: "/visits/:name", name: "visit-console", component: VisitConsole, props: true },
  { path: "/contracts", name: "contracts", component: Contracts },
  { path: "/expenses", name: "expenses", component: Expenses },
  { path: "/knowledge", name: "knowledge", component: Knowledge },
];

const router = createRouter({
  history: createWebHistory("/athru-service"),
  routes,
});

export default router;
