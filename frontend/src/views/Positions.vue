<template>
  <div class="positions">
    <el-container>
      <el-header><h2>📈 模拟持仓</h2><el-button @click="$router.push('/')">返回</el-button></el-header>
      <el-main>
        <el-table :data="positions" stripe style="width: 100%">
          <el-table-column prop="stock_code" label="代码" width="120" />
          <el-table-column prop="stock_name" label="名称" width="120" />
          <el-table-column prop="quantity" label="数量" width="100" />
          <el-table-column prop="cost_price" label="成本价" width="100" />
          <el-table-column prop="highest_price" label="最高价" width="100" />
          <el-table-column prop="buy_date" label="买入日期" width="120" />
          <el-table-column label="盈亏">
            <template #default="{ row }">
              <span :class="row.profit_pct >= 0 ? 'profit' : 'loss'">{{ row.profit_pct >= 0 ? '+' : '' }}{{ row.profit_pct.toFixed(2) }}%</span>
            </template>
          </el-table-column>
        </el-table>
        <p v-if="positions.length === 0" style="text-align: center; color: #999; margin-top: 50px">暂无持仓</p>
      </el-main>
    </el-container>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { sim } from '../api'

const positions = ref([])

onMounted(async () => {
  const res = await sim.getPositions()
  if (res.data.success) positions.value = res.data.data
})
</script>

<style scoped>
.positions { min-height: 100vh; background: #f5f7fa; }
.el-header { background: #fff; border-bottom: 1px solid #e4e7ed; padding: 0 20px; display: flex; justify-content: space-between; align-items: center; }
.el-main { padding: 20px; }
.profit { color: #f56c6c; }
.loss { color: #67c23a; }
</style>
