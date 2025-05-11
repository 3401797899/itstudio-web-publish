import { createRouter, createWebHistory } from 'vue-router'
import { useAuth } from '../store/auth'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/login/index.vue'),
    meta: { requiresAuth: false }
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

// 添加一个标志来防止重复检查
let isCheckingAuth = false

router.beforeEach(async (to, from, next) => {
  // 如果正在检查认证状态，直接放行
  if (isCheckingAuth) {
    return next()
  }

  // 如果目标路由不需要认证，直接放行
  if (!to.meta.requiresAuth) {
    return next()
  }

  try {
    isCheckingAuth = true
    const { checkAuth } = useAuth()
    const isAuthenticated = await checkAuth()

    if (!isAuthenticated) {
      next('/login')
    } else {
      next()
    }
  } catch (error) {
    console.error('Auth check failed:', error)
    next('/login')
  } finally {
    isCheckingAuth = false
  }
})

export default router