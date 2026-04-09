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
      // 实盘页面
      {
        path: 'real/positions',
        name: 'RealPositions',
        component: () => import('../views/RealPositions.vue'),
        meta: { requiresAuth: true, title: '实盘持仓', mode: 'real' }
      },
      {
        path: 'real/trades',
        name: 'RealTrades',
        component: () => import('../views/RealTrades.vue'),
        meta: { requiresAuth: true, title: '交易记录', mode: 'real' }
      },
      {
        path: 'real/analysis',
        name: 'RealAnalysis',
        component: () => import('../views/RealAnalysis.vue'),
        meta: { requiresAuth: true, title: '收益分析', mode: 'real' }
      },
      // 模拟页面
      {
        path: 'sim',
        name: 'SimDashboard',
        component: () => import('../views/SimDashboard.vue'),
        meta: { requiresAuth: true, title: '模拟概览', mode: 'sim' }
      },
      {
        path: 'sim/positions',
        name: 'SimPositions',
        component: () => import('../views/SimPositions.vue'),
        meta: { requiresAuth: true, title: '模拟持仓', mode: 'sim' }
      },
      {
        path: 'watchlist',
        name: 'Watchlist',
        component: () => import('../views/Watchlist.vue'),
        meta: { requiresAuth: true, title: '自选列表', mode: 'sim' }
      },
      // 公共页面
      {
        path: 'stats',
        name: 'Stats',
        component: () => import('../views/Stats.vue'),
        meta: { requiresAuth: true, title: '统计分析', mode: 'public' }
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
