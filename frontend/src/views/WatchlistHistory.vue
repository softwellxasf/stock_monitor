<template>
  <div class="watchlist-history">
    <el-card shadow="never">
      <template #header>
        <div class="card-header">
          <span>📊 历史估值</span>
          <el-tag type="info">自选股估值记录</el-tag>
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

      <!-- 历史估值表格 -->
      <el-table :data="records" stripe style="width: 100%" v-loading="loading">
        <el-table-column prop="quarter_start" label="季度开始" width="120" />
        <el-table-column prop="quarter_end" label="季度结束" width="120" />
        <el-table-column prop="stock_code" label="代码" width="120" />
        <el-table-column prop="stock_name" label="名称" width="100" />
        <el-table-column prop="target_price" label="目标价" width="100">
          <template #default="{ row }">
            <span class="price-text">￥{{ row.target_price?.toFixed(2) }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="target_type" label="类型" width="80">
          <template #default="{ row }">
            <el-tag :type="row.target_type === 'high' ? 'danger' : 'success'" size="small">
              {{ row.target_type === 'high' ? '高估' : '低估' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="pe_ttm" label="PE(TTM)" width="90">
          <template #default="{ row }">
            <span :class="getValuationClass(row.pe_ttm)">{{ row.pe_ttm?.toFixed(2) || '-' }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="pb" label="PB" width="80">
          <template #default="{ row }">
            <span>{{ row.pb?.toFixed(2) || '-' }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="dividend_yield" label="股息率" width="90">
          <template #default="{ row }">
            <span>{{ row.dividend_yield?.toFixed(2) || '-' }}%</span>
          </template>
        </el-table-column>
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
import { watchlist } from '../api'

const records = ref([])
const loading = ref(false)

const pagination = reactive({
  page: 1,
  pageSize: 20,
  total: 0
})

const filters = reactive({
  keyword: '',
  dateRange: []
})

const loadRecords = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.pageSize
    }

    if (filters.keyword) {
      params.keyword = filters.keyword
    }
    if (filters.dateRange && filters.dateRange.length === 2) {
      params.start_date = filters.dateRange[0]
      params.end_date = filters.dateRange[1]
    }

    const res = await watchlist.getHistory(params)
    if (res.data.success) {
      records.value = res.data.data
      pagination.total = res.data.total
      pagination.page = res.data.page
      pagination.pageSize = res.data.page_size
    }
  } catch (error) {
    console.error('加载历史估值失败:', error)
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  pagination.page = 1
  loadRecords()
}

const resetSearch = () => {
  filters.keyword = ''
  filters.dateRange = []
  pagination.page = 1
  loadRecords()
}

const handleSizeChange = () => {
  pagination.page = 1
  loadRecords()
}

const handlePageChange = () => {
  loadRecords()
}

const getValuationClass = (value) => {
  if (!value) return ''
  if (value < 20) return 'undervalued'
  if (value > 50) return 'overvalued'
  return 'normal'
}

onMounted(() => {
  loadRecords()
})
</script>

<style scoped>
.watchlist-history {
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
}

.price-text {
  color: #ef5350;
  font-weight: 500;
}

.pe-text {
  font-weight: 500;
}

.undervalued {
  color: #26a69a;
}

.overvalued {
  color: #ef5350;
}

.normal {
  color: #d1d4dc;
}
</style>
