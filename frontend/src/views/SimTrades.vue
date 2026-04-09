<template>
  <div class="sim-trades">
    <el-card shadow="never">
      <template #header>
        <div class="card-header">
          <span>📝 模拟交易记录</span>
          <el-tag type="success" size="small">模拟盘</el-tag>
        </div>
      </template>

      <!-- 搜索过滤 -->
      <div class="search-bar">
        <el-input
          v-model="filters.keyword"
          placeholder="搜索股票代码/备注"
          clearable
          style="width: 200px"
          @keyup.enter="handleSearch"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        <el-select
          v-model="filters.direction"
          placeholder="交易方向"
          clearable
          style="width: 120px"
          @change="handleSearch"
        >
          <el-option label="买入" value="BUY" />
          <el-option label="卖出" value="SELL" />
        </el-select>
        <el-date-picker
          v-model="filters.dateRange"
          type="daterange"
          range-separator="至"
          start-placeholder="开始日期"
          end-placeholder="结束日期"
          value-format="YYYY-MM-DD"
          style="width: 240px"
          @change="handleSearch"
        />
        <el-button type="primary" @click="handleSearch">搜索</el-button>
        <el-button @click="resetSearch">重置</el-button>
      </div>

      <!-- 交易记录表格 -->
      <el-table :data="trades" stripe style="width: 100%" v-loading="loading">
        <el-table-column prop="trade_date" label="交易时间" width="160" />
        <el-table-column prop="stock_code" label="代码" width="120" />
        <el-table-column prop="stock_name" label="名称" width="100" />
        <el-table-column prop="direction" label="方向" width="80">
          <template #default="{ row }">
            <el-tag :type="row.direction === 'BUY' ? 'success' : 'danger'">
              {{ row.direction === 'BUY' ? '买入' : '卖出' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="price" label="成交价" width="100">
          <template #default="{ row }">¥{{ row.price?.toFixed(4) }}</template>
        </el-table-column>
        <el-table-column prop="quantity" label="数量" width="100" />
        <el-table-column prop="amount" label="成交金额" width="120">
          <template #default="{ row }">¥{{ row.amount?.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2}) }}</template>
        </el-table-column>
        <el-table-column prop="fee" label="手续费" width="100">
          <template #default="{ row }">¥{{ row.fee?.toFixed(2) }}</template>
        </el-table-column>
        <el-table-column prop="profit_loss" label="盈亏" width="100">
          <template #default="{ row }">
            <span :class="row.profit_loss >= 0 ? 'profit' : 'loss'">
              {{ row.profit_loss >= 0 ? '+' : '' }}¥{{ row.profit_loss?.toFixed(2) }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="profit_loss_pct" label="盈亏%" width="80">
          <template #default="{ row }">
            <span :class="row.profit_loss_pct >= 0 ? 'profit' : 'loss'">
              {{ row.profit_loss_pct >= 0 ? '+' : '' }}{{ row.profit_loss_pct?.toFixed(2) }}%
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="strategy" label="策略" width="100" />
        <el-table-column prop="remark" label="备注" min-width="150" show-overflow-tooltip />
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
import { sim } from '../api'

const trades = ref([])
const loading = ref(false)

const pagination = reactive({
  page: 1,
  pageSize: 20,
  total: 0
})

const filters = reactive({
  keyword: '',
  direction: '',
  dateRange: []
})

const loadTrades = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.pageSize
    }

    if (filters.keyword) {
      params.keyword = filters.keyword
    }
    if (filters.direction) {
      params.direction = filters.direction
    }
    if (filters.dateRange && filters.dateRange.length === 2) {
      params.start_date = filters.dateRange[0]
      params.end_date = filters.dateRange[1]
    }

    const res = await sim.getTrades(params)
    if (res.data.success) {
      trades.value = res.data.data
      pagination.total = res.data.total
      pagination.page = res.data.page
      pagination.pageSize = res.data.page_size
    }
  } catch (error) {
    console.error('加载交易记录失败:', error)
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  pagination.page = 1
  loadTrades()
}

const resetSearch = () => {
  filters.keyword = ''
  filters.direction = ''
  filters.dateRange = []
  pagination.page = 1
  loadTrades()
}

const handleSizeChange = () => {
  pagination.page = 1
  loadTrades()
}

const handlePageChange = () => {
  loadTrades()
}

onMounted(() => {
  loadTrades()
})
</script>

<style scoped>
.sim-trades {
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
