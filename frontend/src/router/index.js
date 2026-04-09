import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  { path: '/login', name: 'Login', component: () => import('../views/Login.vue') },
  { path: '/', name: 'Dashboard', component: () => import('../views/Dashboard.vue'), meta: { requiresAuth: true } },
  { path: '/positions', name: 'Positions', component: () => import('../views/Positions.vue'), meta: { requiresAuth: true } },
  { path: '/watchlist', name: 'Watchlist', component: () => import('../views/Watchlist.vue'), meta: { requiresAuth: true } },
  { path: '/stats', name: 'Stats', component: () => import('../views/Stats.vue'), meta: { requiresAuth: true } }
]

const router = createRouter({ history: createWebHistory(), routes })

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  if (to.meta.requiresAuth && !token) next('/login')
  else next()
})

export default router
