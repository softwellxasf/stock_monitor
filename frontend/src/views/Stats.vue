<template>
  <div class="stats-page">
    <el-row :gutter="20">
      <el-col :span="12">
        <el-card shadow="never">
          <template #header>
            <div class="card-header">
              <span>账户统计</span>
              <el-icon color="#409EFF"><Wallet /></el-icon>
            </div>
          </template>
          <el-descriptions :column="1" border>
            <el-descriptions-item label="初始资金">¥{{ stats.total_capital?.toLocaleString() }}</el-descriptions-item>
            <el-descriptions-item label="总资产">¥{{ stats.total_value?.toLocaleString() }}</el-descriptions-item>
            <el-descriptions-item label="可用现金">¥{{ stats.cash?.toLocaleString() }}</el-descriptions-item>
            <el-descriptions-item label="持仓市值">¥{{ getMarketValue }}</el-descriptions-item>
          </el-descriptions>
        </el-card>
      </el-col>
      
      <el-col :span="12">
        <el-card shadow="never">
          <template #header>
            <div class="card-header">
              <span>持仓统计</span>
              <el-icon color="#67c23a"><DataAnalysis /></el-icon>
            </div>
          </template>
          <el-descriptions :column="1" border>
            <el-descriptions-item label="持仓数量">{{ stats.position_count }} 只</el-descriptions-item>
            <el-descriptions-item label="自选标的">{{ stats.watchlist_count }} 只</el-descriptions-item>
            <el-descriptions-item label="当前仓位">{{ getCipherRate }}%</el-descriptions-item>
            <el-descriptions-item label="累计成本">¥{{ stats.total_cost_paid?.toLocaleString() }}</el-descriptions-item>
          </el-descriptions>
        </el-card>
      </el-col>
    </el-row>
    
    <el-card style="margin-top: 20px" shadow="never">
      <template #header>
        <div class="card-header">
          <span>收益趋势</span>
          <el-tag type="success">近 5 年</el-tag>
        </div>
      </template>
      <div class="chart-placeholder">
        <el-empty description="收益图表开发中..." :image-size="100" />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { sim } from '../api'
import { ElMessage } from 'element-plus'

const stats = ref({})

const getCipherRate = computed(() => {
  if (!stats.value.total_capital) return '0.0'
  return (((stats.value.total_value - stats.value.cash) / stats.value.total_capital) * 100).toFixed(1)
})

const getMarketValue = computed(() => {
  return (stats.value.total_value - stats.value.cash)?.toLocaleString()
})

onMounted(async () => {
  try {
    const res = await sim.getStats()
    if (res.data.success) {
      stats.value = res.data.data
    }
  } catch (e) {
    ElMessage.error('加载数据失败')
  }
})
</script>

<style scoped>
.stats-page {
  padding: 10px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chart-placeholder {
  height: 300px;
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>
