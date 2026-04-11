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
        path: 'real',
        name: 'ActualDashboard',
        component: () => import('../views/ActualDashboard.vue'),
        meta: { requiresAuth: true, title: '实盘概览' }
      },
      {
        path: 'sim/positions',
        name: 'SimPositions',
        component: () => import('../views/SimPositions.vue'),
        meta: { requiresAuth: true, title: '模拟持仓' }
      },
      {
        path: 'sim/trades',
        name: 'SimTrades',
        component: () => import('../views/SimTrades.vue'),
        meta: { requiresAuth: true, title: '模拟交易记录' }
      },
      {
        path: 'sim/analysis',
        name: 'SimAnalysis',
        component: () => import('../views/SimAnalysis.vue'),
        meta: { requiresAuth: true, title: '模拟收益分析' }
      },
      {
        path: 'kline',
        name: 'KlineChart',
        component: () => import('../views/KlineChart.vue'),
        meta: { requiresAuth: true, title: 'K 线图' }
      },
      {
        path: 'real/positions',
        name: 'RealPositions',
        component: () => import('../views/RealPositions.vue'),
        meta: { requiresAuth: true, title: '实盘持仓' }
      },
      {
        path: 'real/trades',
        name: 'RealTrades',
        component: () => import('../views/RealTrades.vue'),
        meta: { requiresAuth: true, title: '交易记录' }
      },
      {
        path: 'real/analysis',
        name: 'RealAnalysis',
        component: () => import('../views/RealAnalysis.vue'),
        meta: { requiresAuth: true, title: '收益分析' }
      },
      {
        path: 'watchlist',
        name: 'Watchlist',
        component: () => import('../views/Watchlist.vue'),
        meta: { requiresAuth: true, title: '自选列表' }
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

// 调试：监听 token 变化
if (typeof window !== 'undefined') {
  window.addEventListener('storage', (e) => {
    if (e.key === 'token') {
      console.log('Token changed:', e.newValue ? 'set' : 'cleared')
    }
  })
}

export default router
