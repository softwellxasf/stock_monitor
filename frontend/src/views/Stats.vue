<template>
  <div class="stats">
    <el-container>
      <el-header><h2>📊 统计分析</h2><el-button @click="$router.push('/')">返回</el-button></el-header>
      <el-main>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-card>
              <template #header><span>账户统计</span></template>
              <el-descriptions :column="1" border>
                <el-descriptions-item label="初始资金">¥{{ stats.total_capital?.toLocaleString() }}</el-descriptions-item>
                <el-descriptions-item label="总资产">¥{{ stats.total_value?.toLocaleString() }}</el-descriptions-item>
                <el-descriptions-item label="可用现金">¥{{ stats.cash?.toLocaleString() }}</el-descriptions-item>
                <el-descriptions-item label="持仓市值">¥{{ (stats.total_value - stats.cash)?.toLocaleString() }}</el-descriptions-item>
              </el-descriptions>
            </el-card>
          </el-col>
          <el-col :span="12">
            <el-card>
              <template #header><span>持仓统计</span></template>
              <el-descriptions :column="1" border>
                <el-descriptions-item label="持仓数量">{{ stats.position_count }} 只</el-descriptions-item>
                <el-descriptions-item label="自选标的">{{ stats.watchlist_count }} 只</el-descriptions-item>
                <el-descriptions-item label="仓位">{{ ((stats.total_value - stats.cash) / stats.total_capital * 100).toFixed(1) }}%</el-descriptions-item>
              </el-descriptions>
            </el-card>
          </el-col>
        </el-row>
      </el-main>
    </el-container>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { sim } from '../api'

const stats = ref({})

onMounted(async () => {
  const res = await sim.getStats()
  if (res.data.success) stats.value = res.data.data
})
</script>

<style scoped>
.stats { min-height: 100vh; background: #f5f7fa; }
.el-header { background: #fff; border-bottom: 1px solid #e4e7ed; padding: 0 20px; display: flex; justify-content: space-between; align-items: center; }
.el-main { padding: 20px; }
</style>
