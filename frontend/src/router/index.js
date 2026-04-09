import { createRouter, createWebHistory } from 'vue-router'
import MainLayout from '../layouts/MainLayout.vue'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/Login.vue')
  },
  {
    path: '/',
    component: MainLayout,
    redirect: '/sim',
    children: [
      {
        path: 'sim',
        name: 'SimDashboard',
        component: () => import('../views/SimDashboard.vue'),
        meta: { requiresAuth: true, title: '模拟概览' }
      },
      {
        path: 'sim/positions',
        name: 'SimPositions',
        component: () => import('../views/SimPositions.vue'),
        meta: { requiresAuth: true, title: '模拟持仓' }
      },
      {
        path: 'real/positions',
        name: 'RealPositions',
        component: () => import('../views/RealPositions.vue'),
        meta: { requiresAuth: true, title: '实盘持仓' }
      },
      {
        path: 'watchlist',
        name: 'Watchlist',
        component: () => import('../views/Watchlist.vue'),
        meta: { requiresAuth: true, title: '自选列表' }
      },
      {
        path: 'stats',
        name: 'Stats',
        component: () => import('../views/Stats.vue'),
        meta: { requiresAuth: true, title: '统计分析' }
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  if (to.meta.requiresAuth && !token) {
    next('/login')
  } else {
    next()
  }
})

export default router
