import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/login/index.vue')
  },
  {
    path: '/',
    name: 'Home',
    component: () => import('../views/home/index.vue'),
    meta: { requiresAuth: true },
    redirect: '/dashboard',
    children: [
      {
        path: 'global-config',
        name: 'GlobalConfig',
        component: () => import('../views/global-config/index.vue')
      },
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('../views/home/home.vue')
      },
      {
        path: 'domain-add',
        name: 'DomainAdd',
        component: () => import('../views/domain-add/index.vue')
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router