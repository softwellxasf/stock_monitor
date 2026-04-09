<template>
  <div class="main-layout">
    <el-container>
      <!-- 侧边栏 -->
      <el-aside :width="isCollapse ? '64px' : '220px'" class="sidebar">
        <div class="logo">
          <span v-if="!isCollapse">📊 stockMonitor</span>
          <span v-else>📊</span>
        </div>
        
        <el-menu
          :default-active="activeMenu"
          :collapse="isCollapse"
          :collapse-transition="false"
          router
          class="sidebar-menu"
          background-color="transparent"
        >
          <!-- 模拟分类 -->
          <el-sub-menu index="sim">
            <template #title>
              <el-icon><TrendCharts /></el-icon>
              <span>模拟</span>
            </template>
            <el-menu-item index="/sim">
              <el-icon><Home /></el-icon>
              <template #title>模拟概览</template>
            </el-menu-item>
            <el-menu-item index="/sim/positions">
              <el-icon><List /></el-icon>
              <template #title>模拟持仓</template>
            </el-menu-item>
          </el-sub-menu>
          
          <!-- 实盘分类 -->
          <el-sub-menu index="real">
            <template #title>
              <el-icon><Briefcase /></el-icon>
              <span>实盘</span>
            </template>
            <el-menu-item index="/real/positions">
              <el-icon><Briefcase /></el-icon>
              <template #title>实盘持仓</template>
            </el-menu-item>
          </el-sub-menu>
          
          <!-- 公共功能 -->
          <el-menu-item index="/watchlist">
            <el-icon><Star /></el-icon>
            <template #title>自选列表</template>
          </el-menu-item>
          
          <el-menu-item index="/stats">
            <el-icon><DataAnalysis /></el-icon>
            <template #title>统计分析</template>
          </el-menu-item>
        </el-menu>
        
        <!-- 收缩按钮 -->
        <div class="collapse-btn" @click="toggleCollapse">
          <el-icon :size="20">
            <component :is="isCollapse ? 'Expand' : 'Fold'" />
          </el-icon>
        </div>
      </el-aside>
      
      <!-- 主内容区 -->
      <el-container>
        <!-- 顶部导航 -->
        <el-header class="header">
          <div class="header-left">
            <el-breadcrumb separator="/">
              <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
              <el-breadcrumb-item v-if="pageTitle">{{ pageTitle }}</el-breadcrumb-item>
            </el-breadcrumb>
          </div>
          <div class="header-right">
            <ThemeSwitcher />
            <el-dropdown @command="handleCommand">
              <span class="user-info">
                <el-avatar :size="32" icon="User" />
                <span class="username">{{ username }}</span>
              </span>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="logout">退出登录</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
        </el-header>
        
        <!-- 内容区 -->
        <el-main class="main-content">
          <router-view />
        </el-main>
      </el-container>
    </el-container>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import ThemeSwitcher from '../components/ThemeSwitcher.vue'

const route = useRoute()
const router = useRouter()
const isCollapse = ref(false)
const username = ref('admin')
const activeMenu = computed(() => route.path)

const pageTitle = computed(() => {
  const titles = {
    '/sim': '模拟概览',
    '/sim/positions': '模拟持仓',
    '/real/positions': '实盘持仓',
    '/watchlist': '自选列表',
    '/stats': '统计分析'
  }
  return titles[route.path] || ''
})

const toggleCollapse = () => { isCollapse.value = !isCollapse.value }

const handleCommand = async (command) => {
  if (command === 'logout') {
    try {
      await ElMessageBox.confirm('确定要退出登录吗？', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      })
      localStorage.removeItem('token')
      ElMessage.success('已退出登录')
      router.push('/login')
    } catch {}
  }
}

onMounted(() => {
  const token = localStorage.getItem('token')
  if (token) {
    try {
      const payload = JSON.parse(atob(token.split('.')[1]))
      username.value = payload.sub || 'admin'
    } catch {
      username.value = 'admin'
    }
  }
})
</script>

<style scoped>
.main-layout { min-height: 100vh; }
.el-container { height: 100vh; }

.sidebar {
  background: var(--theme-sidebar, #2d4a6b);
  transition: width 0.3s;
  position: relative;
  overflow: hidden;
}

.logo {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: rgba(255,255,255,0.9);
  font-size: 16px;
  font-weight: 500;
  background: rgba(0,0,0,0.08);
  border-bottom: 1px solid rgba(255,255,255,0.08);
}

/* 侧边栏菜单统一样式 */
.sidebar-menu {
  border-right: none;
  background: transparent;
}

.sidebar-menu:not(.el-menu--collapse) {
  width: 220px;
}

/* 一级菜单（子菜单标题）和二级菜单统一颜色 */
.sidebar-menu .el-menu-item,
.sidebar-menu .el-sub-menu__title {
  color: rgba(255, 255, 255, 0.85);
  font-size: 14px;
  background: transparent;
}

/* 悬停效果 - 一级和二级统一 */
.sidebar-menu .el-menu-item:hover,
.sidebar-menu .el-sub-menu__title:hover {
  background: rgba(255, 255, 255, 0.12);
  color: rgba(255, 255, 255, 1);
}

/* 选中状态 - 使用主题色 */
.sidebar-menu .el-menu-item.is-active {
  background: var(--theme-sidebar-active, #3d6bb3);
  color: rgba(255, 255, 255, 1);
}

/* 子菜单展开背景 - 轻微加深 */
.sidebar-menu .el-menu--inline {
  background: rgba(0, 0, 0, 0.12);
}

.sidebar-menu .el-menu--inline .el-menu-item {
  color: rgba(255, 255, 255, 0.8);
}

.sidebar-menu .el-menu--inline .el-menu-item:hover {
  background: rgba(255, 255, 255, 0.1);
  color: rgba(255, 255, 255, 1);
}

.sidebar-menu .el-menu--inline .el-menu-item.is-active {
  background: var(--theme-sidebar-active, #3d6bb3);
  color: rgba(255, 255, 255, 1);
}

/* 收缩按钮 */
.collapse-btn {
  position: absolute;
  bottom: 20px;
  left: 50%;
  transform: translateX(-50%);
  width: 40px;
  height: 40px;
  background: rgba(255,255,255,0.12);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: rgba(255,255,255,0.9);
  cursor: pointer;
  transition: background 0.3s;
}

.collapse-btn:hover {
  background: var(--theme-primary, #2B5B9E);
}

/* 顶部导航 */
.header {
  background: var(--theme-bg, #F7F8FA);
  border-bottom: 1px solid var(--theme-border, #E5E6EB);
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 20px;
  height: 60px;
}

.header-left { flex: 1; }
.header-right { display: flex; align-items: center; }
.user-info { display: flex; align-items: center; gap: 10px; cursor: pointer; }
.username { color: var(--theme-text, #333); font-size: 14px; }
.main-content { background: var(--theme-bg, #F7F8FA); padding: 20px; overflow-y: auto; }
</style>
