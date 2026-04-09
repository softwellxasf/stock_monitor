<template>
  <div class="real-positions">
    <el-card shadow="never">
      <template #header>
        <div class="card-header">
          <span>💼 实盘持仓</span>
          <el-tag type="warning" size="small">实盘</el-tag>
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
        <el-input
          v-model="filters.industry"
          placeholder="行业"
          clearable
          style="width: 150px"
          @keyup.enter="handleSearch"
        />
        <el-button type="primary" @click="handleSearch">搜索</el-button>
        <el-button @click="resetSearch">重置</el-button>
      </div>

      <!-- 持仓表格 -->
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
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { actual } from '../api'

const positions = ref([])
const loading = ref(false)

const filters = reactive({
  keyword: '',
  industry: ''
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
    if (filters.industry) params.industry = filters.industry

    const res = await actual.getPositions(params)
    if (res.data.success) {
      positions.value = res.data.data
      pagination.total = res.data.total || 0
    }
  } catch (error) {
    console.error('加载实盘持仓失败:', error)
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
  filters.industry = ''
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
.real-positions {
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

.profit {
  color: #f56c6c;
  font-weight: bold;
}

.loss {
  color: #67c23a;
  font-weight: bold;
}
</style>
