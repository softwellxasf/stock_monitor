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
        <el-select
          v-model="filters.industry"
          placeholder="行业"
          clearable
          filterable
          style="width: 150px"
          @change="handleSearch"
        >
          <el-option label="全部" value="" />
          <el-option
            v-for="ind in industries"
            :key="ind"
            :label="ind"
            :value="ind"
          />
        </el-select>
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
        <el-table-column label="操作" width="120" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="handleEdit(row)">修改</el-button>
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
    </el-card>

    <!-- 编辑对话框 -->
    <el-dialog v-model="editDialogVisible" title="修改最高价" width="400px">
      <el-form :model="editForm" label-width="80px">
        <el-form-item label="股票代码">
          <span>{{ editForm.stock_code }} - {{ editForm.stock_name }}</span>
        </el-form-item>
        <el-form-item label="现价">
          <span>¥{{ editForm.current_price?.toFixed(4) }}</span>
        </el-form-item>
        <el-form-item label="最高价">
          <el-input-number v-model="editForm.highest_price" :precision="4" :step="0.01" :min="0" style="width: 100%" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmEdit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { actual } from '../api'
import { ElMessage } from 'element-plus'

const positions = ref([])
const loading = ref(false)
const industries = ref([])

const filters = reactive({
  keyword: '',
  industry: ''
})

const pagination = reactive({
  page: 1,
  pageSize: 20,
  total: 0
})

// 编辑对话框
const editDialogVisible = ref(false)
const editForm = ref({
  id: null,
  stock_code: '',
  stock_name: '',
  current_price: 0,
  highest_price: 0
})

// 编辑
const handleEdit = (row) => {
  editForm.value = {
    id: row.id,
    stock_code: row.stock_code,
    stock_name: row.stock_name,
    current_price: row.current_price,
    highest_price: row.highest_price
  }
  editDialogVisible.value = true
}

// 确认编辑
const confirmEdit = async () => {
  try {
    await actual.updatePosition(editForm.value.id, { highest_price: editForm.value.highest_price })
    ElMessage.success('修改成功')
    editDialogVisible.value = false
    await loadPositions()
  } catch (e) {
    ElMessage.error('修改失败')
  }
}

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
      // 提取行业列表
      if (res.data.industries) {
        industries.value = res.data.industries
      }
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
