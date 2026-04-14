import type { RouteRecordRaw } from 'vue-router';

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    component: () => import('layouts/MainLayout.vue'),
    children: [
      { path: '', component: () => import('pages/MonitoringPage.vue') },
      { path: 'workflow', component: () => import('pages/WorkflowPage.vue') },
      { path: 'experiment', component: () => import('pages/ExperimentPage.vue') }
    ],
  },

  {
    path: '/:catchAll(.*)*',
    component: () => import('pages/ErrorNotFound.vue'),
  },
];

export default routes;