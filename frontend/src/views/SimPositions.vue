<template>
  <div class="sim-positions">
    <el-card shadow="never">
      <template #header>
        <div class="card-header">
          <span>📈 模拟持仓</span>
          <el-tag type="success" size="small">模拟盘</el-tag>
        </div>
      </template>
      
      <el-table :data="positions" stripe style="width: 100%" v-loading="loading">
        <el-table-column prop="stock_code" label="代码" width="120" sortable />
        <el-table-column prop="stock_name" label="名称" width="120" />
        <el-table-column prop="quantity" label="数量" width="100" sortable />
        <el-table-column prop="cost_price" label="成本价" width="100" sortable>
          <template #default="{ row }">¥{{ row.cost_price?.toFixed(2) }}</template>
        </el-table-column>
        <el-table-column prop="highest_price" label="最高价" width="100">
          <template #default="{ row }">¥{{ row.highest_price?.toFixed(2) }}</template>
        </el-table-column>
        <el-table-column prop="buy_date" label="买入日期" width="120" />
        <el-table-column label="盈亏比例" width="120" sortable>
          <template #default="{ row }">
            <span :class="row.profit_pct >= 0 ? 'profit' : 'loss'">
              {{ row.profit_pct >= 0 ? '+' : '' }}{{ row.profit_pct.toFixed(2) }}%
            </span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150">
          <template #default="{ row }">
            <el-button type="primary" size="small" link>详情</el-button>
            <el-button type="danger" size="small" link>卖出</el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <p v-if="positions.length === 0" class="empty-text">暂无模拟持仓</p>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { sim } from '../api'
import { ElMessage } from 'element-plus'

const loading = ref(false)
const positions = ref([])

onMounted(async () => {
  loading.value = true
  try {
    const res = await sim.getPositions()
    if (res.data.success) {
      positions.value = res.data.data
    }
  } catch (e) {
    ElMessage.error('加载数据失败')
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.sim-positions {
  padding: 10px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.empty-text {
  text-align: center;
  color: #909399;
  margin: 50px 0;
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
