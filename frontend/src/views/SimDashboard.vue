<template>
  <div class="sim-dashboard" v-loading="loading">
    <el-row :gutter="20">
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <template #header>
            <div class="card-header">
              <span>总资产</span>
              <el-icon><Wallet /></el-icon>
            </div>
          </template>
          <div class="stat-value">¥{{ stats.total_value?.toLocaleString() }}</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <template #header>
            <div class="card-header">
              <span>可用现金</span>
              <el-icon><Money /></el-icon>
            </div>
          </template>
          <div class="stat-value">¥{{ stats.cash?.toLocaleString() }}</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <template #header>
            <div class="card-header">
              <span>持仓数量</span>
              <el-icon><List /></el-icon>
            </div>
          </template>
          <div class="stat-value">{{ stats.position_count }} 只</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <template #header>
            <div class="card-header">
              <span>自选标的</span>
              <el-icon><Star /></el-icon>
            </div>
          </template>
          <div class="stat-value">{{ stats.watchlist_count }} 只</div>
        </el-card>
      </el-col>
    </el-row>

    <el-card style="margin-top: 20px">
      <template #header><span>模拟盘概况</span></template>
      <p>初始资金：¥{{ stats.total_capital?.toLocaleString() }}</p>
      <p v-if="stats.total_capital > 0">当前仓位：{{ ((stats.total_value - stats.cash) / stats.total_capital * 100).toFixed(1) }}%</p>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { sim } from '../api'
import { ElMessage } from 'element-plus'

const stats = ref({
  total_value: 0,
  cash: 0,
  position_count: 0,
  watchlist_count: 0,
  total_capital: 0
})
const loading = ref(true)

onMounted(async () => {
  try {
    const res = await sim.getStats()
    if (res.data.success) {
      stats.value = res.data.data
    } else {
      ElMessage.error('加载数据失败')
    }
  } catch (error) {
    console.error('加载统计数据失败:', error)
    ElMessage.error('无法连接服务器')
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.sim-dashboard { padding: 10px; }
.stat-value { font-size: 24px; font-weight: bold; color: #409EFF; text-align: center; padding: 20px 0; }
</style>
