<template>
  <div class="dashboard">
    <el-container>
      <el-header>
        <div class="header-content">
          <h2>📊 stockMonitor</h2>
          <el-button type="danger" size="small" @click="handleLogout">退出</el-button>
        </div>
      </el-header>
      <el-container>
        <el-aside width="200px">
          <el-menu router default-active="/">
            <el-menu-item index="/"><el-icon><Home /></el-icon><span>首页</span></el-menu-item>
            <el-menu-item index="/positions"><el-icon><List /></el-icon><span>持仓</span></el-menu-item>
            <el-menu-item index="/watchlist"><el-icon><Star /></el-icon><span>自选</span></el-menu-item>
            <el-menu-item index="/stats"><el-icon><DataAnalysis /></el-icon><span>统计</span></el-menu-item>
          </el-menu>
        </el-aside>
        <el-main>
          <el-row :gutter="20">
            <el-col :span="6">
              <el-card shadow="hover">
                <template #header><span>总资产</span></template>
                <div class="stat-value">¥{{ stats.total_value?.toLocaleString() }}</div>
              </el-card>
            </el-col>
            <el-col :span="6">
              <el-card shadow="hover">
                <template #header><span>可用现金</span></template>
                <div class="stat-value">¥{{ stats.cash?.toLocaleString() }}</div>
              </el-card>
            </el-col>
            <el-col :span="6">
              <el-card shadow="hover">
                <template #header><span>持仓数量</span></template>
                <div class="stat-value">{{ stats.position_count }} 只</div>
              </el-card>
            </el-col>
            <el-col :span="6">
              <el-card shadow="hover">
                <template #header><span>自选标的</span></template>
                <div class="stat-value">{{ stats.watchlist_count }} 只</div>
              </el-card>
            </el-col>
          </el-row>
          
          <el-card style="margin-top: 20px">
            <template #header><span>模拟盘概况</span></template>
            <p>初始资金：¥{{ stats.total_capital?.toLocaleString() }}</p>
            <p>当前仓位：{{ ((stats.total_value - stats.cash) / stats.total_capital * 100).toFixed(1) }}%</p>
          </el-card>
        </el-main>
      </el-container>
    </el-container>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { sim } from '../api'

const router = useRouter()
const stats = ref({ total_value: 0, cash: 0, position_count: 0, watchlist_count: 0, total_capital: 0 })

onMounted(async () => {
  try {
    const res = await sim.getStats()
    if (res.data.success) stats.value = res.data.data
  } catch (e) {
    ElMessage.error('加载数据失败')
  }
})

const handleLogout = () => {
  localStorage.removeItem('token')
  router.push('/login')
}
</script>

<style scoped>
.dashboard { min-height: 100vh; }
.el-header { background: #fff; border-bottom: 1px solid #e4e7ed; padding: 0 20px; }
.header-content { display: flex; justify-content: space-between; align-items: center; height: 60px; }
.el-aside { background: #fff; border-right: 1px solid #e4e7ed; }
.el-main { background: #f5f7fa; padding: 20px; }
.stat-value { font-size: 24px; font-weight: bold; color: #409EFF; }
</style>
