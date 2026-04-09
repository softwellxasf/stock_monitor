<template>
  <div class="sim-positions">
    <el-card shadow="never">
      <template #header>
        <div class="card-header">
          <span>📈 模拟持仓</span>
          <el-tag type="success" size="small">模拟盘</el-tag>
        </div>
      </template>

      <!-- 搜索过滤 -->
      <div class="search-bar">
        <el-input
          v-model="filters.keyword"
          placeholder="搜索股票代码/名称"
          clearable
          style="width: 200px"
          @keyup.enter="handleSearch"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        <el-button type="primary" @click="handleSearch">搜索</el-button>
        <el-button @click="resetSearch">重置</el-button>
      </div>

      <!-- 持仓表格 -->
      <el-table :data="positions" stripe style="width: 100%" v-loading="loading">
        <el-table-column prop="stock_code" label="代码" width="120" />
        <el-table-column prop="stock_name" label="名称" width="120" />
        <el-table-column prop="quantity" label="数量" width="100" />
        <el-table-column prop="cost_price" label="成本价" width="100">
          <template #default="{ row }">¥{{ row.cost_price?.toFixed(2) }}</template>
        </el-table-column>
        <el-table-column prop="highest_price" label="最高价" width="100">
          <template #default="{ row }">¥{{ row.highest_price?.toFixed(2) }}</template>
        </el-table-column>
        <el-table-column prop="buy_date" label="买入日期" width="120" />
        <el-table-column label="盈亏比例" width="120">
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

      <!-- 分页 -->
      <div class="pagination-container">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="pagination.total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handlePageChange"
        />
      </div>

      <p v-if="positions.length === 0 && !loading" class="empty-text">暂无模拟持仓</p>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { sim } from '../api'
import { ElMessage } from 'element-plus'

const positions = ref([])
const loading = ref(false)

const filters = reactive({
  keyword: ''
})

const pagination = reactive({
  page: 1,
  pageSize: 20,
  total: 0
})

const loadPositions = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.pageSize
    }
    if (filters.keyword) params.keyword = filters.keyword

    const res = await sim.getPositions(params)
    if (res.data.success) {
      positions.value = res.data.data
      pagination.total = res.data.total || 0
    }
  } catch (error) {
    console.error('加载模拟持仓失败:', error)
    ElMessage.error('加载数据失败')
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  pagination.page = 1
  loadPositions()
}

const resetSearch = () => {
  filters.keyword = ''
  pagination.page = 1
  loadPositions()
}

const handleSizeChange = () => {
  pagination.page = 1
  loadPositions()
}

const handlePageChange = () => {
  loadPositions()
}

onMounted(() => {
  loadPositions()
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

.search-bar {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
  flex-wrap: wrap;
}

.pagination-container {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #ebeef5;
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
