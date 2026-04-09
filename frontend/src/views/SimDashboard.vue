<template>
  <div class="sim-dashboard">
    <el-row :gutter="20">
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <template #header>
            <div class="card-header">
              <span>总资产</span>
              <el-icon color="#67c23a"><Wallet /></el-icon>
            </div>
          </template>
          <div class="stat-value sim">¥{{ stats.total_value?.toLocaleString() }}</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <template #header>
            <div class="card-header">
              <span>可用现金</span>
              <el-icon color="#409EFF"><Money /></el-icon>
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
              <el-icon color="#e6a23c"><List /></el-icon>
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
              <el-icon color="#f56c6c"><Star /></el-icon>
            </div>
          </template>
          <div class="stat-value">{{ stats.watchlist_count }} 只</div>
        </el-card>
      </el-col>
    </el-row>
    
    <el-card style="margin-top: 20px">
      <template #header>
        <div class="card-header">
          <span>📈 模拟盘概况</span>
          <el-button type="success" size="small" @click="refreshData">刷新</el-button>
        </div>
      </template>
      <el-descriptions :column="2" border>
        <el-descriptions-item label="初始资金">¥{{ stats.total_capital?.toLocaleString() }}</el-descriptions-item>
        <el-descriptions-item label="当前仓位">{{ getCipherRate }}%</el-descriptions-item>
        <el-descriptions-item label="持仓市值">¥{{ getMarketValue }}</el-descriptions-item>
        <el-descriptions-item label="累计成本">¥{{ stats.total_cost_paid?.toLocaleString() }}</el-descriptions-item>
      </el-descriptions>
      
      <el-alert
        title="模拟盘说明"
        type="info"
        :closable="false"
        style="margin-top: 20px"
        show-icon
      >
        <p>• 模拟盘基于 v5 策略自动交易，每日 14:40 检查</p>
        <p>• 交易成本：佣金 0.03% + 印花税 0.05%</p>
        <p>• 止损策略：移动止损 -10%</p>
      </el-alert>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { sim } from '../api'
import { ElMessage } from 'element-plus'

const stats = ref({ total_value: 0, cash: 0, position_count: 0, watchlist_count: 0, total_capital: 0, total_cost_paid: 0 })

const getCipherRate = computed(() => {
  if (!stats.value.total_capital) return '0.0'
  return (((stats.value.total_value - stats.value.cash) / stats.value.total_capital) * 100).toFixed(1)
})

const getMarketValue = computed(() => {
  return (stats.value.total_value - stats.value.cash)?.toLocaleString()
})

const refreshData = async () => {
  try {
    const res = await sim.getStats()
    if (res.data.success) {
      stats.value = res.data.data
      ElMessage.success('数据已刷新')
    }
  } catch (e) {
    ElMessage.error('加载数据失败')
  }
}

onMounted(async () => {
  await refreshData()
})
</script>

<style scoped>
.sim-dashboard {
  padding: 10px;
}

.stat-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.stat-value {
  font-size: 28px;
  font-weight: bold;
  color: #67c23a;
  text-align: center;
  padding: 20px 0;
}
</style>
