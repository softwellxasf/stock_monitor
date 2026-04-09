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
        >
          <!-- 公共功能 -->
          <el-menu-item index="/sim">
            <el-icon><Home /></el-icon>
            <template #title>模拟概览</template>
          </el-menu-item>
          
          <el-menu-item index="/sim/positions">
            <el-icon><List /></el-icon>
            <template #title>模拟持仓</template>
          </el-menu-item>
          
          <el-menu-item index="/real/positions">
            <el-icon><Briefcase /></el-icon>
            <template #title>实盘持仓</template>
          </el-menu-item>
          
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
    '/real/trades': '交易记录',
    '/real/analysis': '收益分析',
    '/watchlist': '自选列表',
    '/stats': '统计分析'
  }
  return titles[route.path] || ''
})

const toggleCollapse = () => {
  isCollapse.value = !isCollapse.value
}

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
    } catch {
      // 取消退出
    }
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
.main-layout {
  min-height: 100vh;
}

.el-container {
  height: 100vh;
}

.sidebar {
  background: #304156;
  transition: width 0.3s;
  position: relative;
  overflow: hidden;
}

.logo {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 18px;
  font-weight: bold;
  background: #263445;
}

.sidebar-menu {
  border-right: none;
  background: #304156;
}

.sidebar-menu:not(.el-menu--collapse) {
  width: 220px;
}

/* 菜单项默认样式 */
.sidebar-menu .el-menu-item {
  color: #bfcbd9;
  background: transparent;
}

.sidebar-menu .el-menu-item:hover {
  background: #263445;
  color: #fff;
}

.sidebar-menu .el-menu-item.is-active {
  background: #409EFF;
  color: #fff;
}

.collapse-btn {
  position: absolute;
  bottom: 20px;
  left: 50%;
  transform: translateX(-50%);
  width: 40px;
  height: 40px;
  background: #263445;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  cursor: pointer;
  transition: background 0.3s;
}

.collapse-btn:hover {
  background: #409EFF;
}

.header {
  background: #fff;
  border-bottom: 1px solid #e4e7ed;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 20px;
  height: 60px;
}

.header-left {
  flex: 1;
}

.header-right {
  display: flex;
  align-items: center;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
}

.username {
  color: #606266;
  font-size: 14px;
}

.main-content {
  background: #f5f7fa;
  padding: 20px;
  overflow-y: auto;
}
</style>
