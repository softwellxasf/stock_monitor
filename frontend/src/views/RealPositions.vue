<template>
  <div class="real-positions">
    <el-card shadow="never">
      <template #header>
        <div class="card-header">
          <span>💼 实盘持仓</span>
          <el-tag type="warning" size="small">实盘</el-tag>
        </div>
      </template>

      <el-table :data="positions" stripe style="width: 100%" v-loading="loading">
        <el-table-column prop="stock_code" label="代码" width="120" />
        <el-table-column prop="stock_name" label="名称" width="100" />
        <el-table-column prop="industry" label="行业" width="100" />
        <el-table-column prop="quantity" label="数量" width="100" />
        <el-table-column prop="cost_price" label="成本价" width="100">
          <template #default="{ row }">¥{{ row.cost_price?.toFixed(4) }}</template>
        </el-table-column>
        <el-table-column prop="current_price" label="现价" width="100">
          <template #default="{ row }">¥{{ row.current_price?.toFixed(4) }}</template>
        </el-table-column>
        <el-table-column prop="highest_price" label="最高价" width="100">
          <template #default="{ row }">¥{{ row.highest_price?.toFixed(4) }}</template>
        </el-table-column>
        <el-table-column prop="stop_loss_price" label="止损价" width="100">
          <template #default="{ row }">¥{{ row.stop_loss_price?.toFixed(4) }}</template>
        </el-table-column>
        <el-table-column label="盈亏比例" width="120">
          <template #default="{ row }">
            <span :class="row.profit_pct >= 0 ? 'profit' : 'loss'">
              {{ row.profit_pct >= 0 ? '+' : '' }}{{ row.profit_pct.toFixed(2) }}%
            </span>
          </template>
        </el-table-column>
        <el-table-column label="止损类型" width="100">
          <template #default="{ row }">
            <el-tag :type="row.stop_loss_type === 'trailing' ? 'warning' : 'info'" size="small">
              {{ row.stop_loss_type === 'trailing' ? '移动' : '固定' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="建仓时间" width="160" />
        <el-table-column prop="updated_at" label="更新时间" width="160" />
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { actual } from '../api'

const positions = ref([])
const loading = ref(false)

const loadPositions = async () => {
  loading.value = true
  try {
    const res = await actual.getPositions()
    if (res.data.success) {
      positions.value = res.data.data
    }
  } catch (error) {
    console.error('加载实盘持仓失败:', error)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadPositions()
})
</script>

<style scoped>
.real-positions {
  padding: 10px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.profit {
  color: #f56c6c;
  font-weight: bold;
}

.loss {
  color: #67c23a;
  font-weight: bold;
}
</style>
