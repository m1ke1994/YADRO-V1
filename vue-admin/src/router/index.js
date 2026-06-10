import { createRouter, createWebHistory } from 'vue-router'

import AdminLayout from '../layouts/AdminLayout.vue'
import DashboardView from '../views/DashboardView.vue'
import SiteOverviewView from '../views/SiteOverviewView.vue'
import AnalyticsView from '../views/AnalyticsView.vue'
import LoginView from '../views/LoginView.vue'
import LeadsView from '../views/LeadsView.vue'
import SectionEditView from '../views/SectionEditView.vue'
import SectionsView from '../views/SectionsView.vue'
import MiniLayoutView from '../views/mini/MiniLayoutView.vue'
import MiniOverviewView from '../views/mini/MiniOverviewView.vue'
import MiniLeadsView from '../views/mini/MiniLeadsView.vue'
import MiniSeoAuditView from '../views/mini/MiniSeoAuditView.vue'
import MiniReportsView from '../views/mini/MiniReportsView.vue'
import MiniSettingsView from '../views/mini/MiniSettingsView.vue'
import MiniIntegrationView from '../views/mini/MiniIntegrationView.vue'
import { applyRouteSeo } from '../config/seo'

const routes = [
  {
    path: '/login',
    name: 'login',
    component: LoginView,
    meta: { guestOnly: true, title: 'Вход' },
  },
  {
    path: '/',
    component: AdminLayout,
    meta: { requiresAuth: true },
    children: [
      { path: '', redirect: { name: 'dashboard' } },
      { path: 'dashboard', name: 'dashboard', component: DashboardView, meta: { title: 'Панель управления' } },
      { path: 'sites/:siteId/overview', name: 'site-overview', component: SiteOverviewView, props: true, meta: { title: 'Обзор сайта' } },
      { path: 'sites/:siteId/sections', name: 'sections', component: SectionsView, props: true, meta: { title: 'Разделы сайта' } },
      { path: 'sites/:siteId/analytics', name: 'analytics', component: AnalyticsView, props: true, meta: { title: 'Аналитика' } },
      { path: 'sites/:siteId/leads', name: 'leads', component: LeadsView, props: true, meta: { title: 'Лиды' } },
      { path: 'sites/:siteId/seo', name: 'site-seo', component: MiniSeoAuditView, props: true, meta: { title: 'SEO-аудит' } },
      { path: 'sites/:siteId/integration', name: 'site-integration', component: MiniIntegrationView, props: true, meta: { title: 'Интеграция' } },
      {
        path: 'mini',
        component: MiniLayoutView,
        children: [
          { path: '', name: 'mini-overview', component: MiniOverviewView, meta: { title: 'Обзор' } },
          { path: 'leads', name: 'mini-leads', component: MiniLeadsView, meta: { title: 'Лиды' } },
          { path: 'seo', name: 'mini-seo', component: MiniSeoAuditView, meta: { title: 'SEO-аудит' } },
          { path: 'reports', name: 'mini-reports', component: MiniReportsView, meta: { title: 'Отчёты' } },
          { path: 'settings', name: 'mini-settings', component: MiniSettingsView, meta: { title: 'Настройки' } },
          { path: 'integration', name: 'mini-integration', component: MiniIntegrationView, meta: { title: 'Интеграция' } },
        ],
      },
      {
        path: 'sites/:siteId/sections/:sectionId',
        name: 'section-edit',
        component: SectionEditView,
        props: true,
        meta: { title: 'Редактирование раздела' },
      },
    ],
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/dashboard',
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to) => {
  const token = localStorage.getItem('access_token')

  if (to.meta.requiresAuth && !token) {
    return { name: 'login' }
  }

  if (to.meta.guestOnly && token) {
    return { name: 'dashboard' }
  }

  return true
})

router.afterEach((to) => {
  applyRouteSeo(to)
})

export default router
