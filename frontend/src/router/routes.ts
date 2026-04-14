import type { RouteRecordRaw } from 'vue-router';

const routes: RouteRecordRaw[] = [
  {
    path: '/login',
    component: () => import('pages/LoginPage.vue'),
    meta: { public: true },
  },
  {
    path: '/',
    component: () => import('layouts/MainLayout.vue'),
    children: [
      { path: '', component: () => import('pages/MonitoringPage.vue') },
      { path: 'workflow', component: () => import('pages/WorkflowPage.vue') },
      { path: 'experiment', component: () => import('pages/ExperimentPage.vue') },
      { path: 'logs', component: () => import('pages/LogPage.vue') },
      { path: 'results', component: () => import('pages/ResultsPage.vue') },
      { path: 'admin', component: () => import('pages/AdminPage.vue'), meta: { adminOnly: true } },
    ],
  },

  {
    path: '/:catchAll(.*)*',
    component: () => import('pages/ErrorNotFound.vue'),
  },
];

export default routes;
