<template>
  <div class="watchlist">
    <el-container>
      <el-header>
        <h2>⭐ 自选表</h2>
        <div class="header-actions">
          <el-button @click="$router.push('/')">返回</el-button>
        </div>
      </el-header>
      <el-main>
        <!-- 搜索条件 -->
        <el-card class="search-card" shadow="never">
          <el-form :inline="true" :model="searchForm">
            <el-form-item label="代码/名称">
              <el-input v-model="searchForm.keyword" placeholder="输入代码或名称" clearable style="width: 200px" />
            </el-form-item>
            <el-form-item label="状态">
              <el-select v-model="searchForm.status" placeholder="全部" clearable style="width: 120px">
                <el-option label="活跃" value="active" />
                <el-option label=" inactive" value="inactive" />
              </el-select>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="handleSearch">搜索</el-button>
              <el-button @click="resetSearch">重置</el-button>
            </el-form-item>
          </el-form>
        </el-card>
        
        <!-- 数据表格 -->
        <el-card style="margin-top: 15px">
          <el-table :data="paginatedList" stripe style="width: 100%" v-loading="loading">
            <el-table-column prop="stock_code" label="代码" width="120" sortable />
            <el-table-column prop="stock_name" label="名称" width="120" />
            <el-table-column prop="target_price" label="目标价" width="100" sortable>
              <template #default="{ row }">¥{{ row.target_price?.toFixed(2) }}</template>
            </el-table-column>
            <el-table-column prop="current_price" label="现价" width="100" sortable>
              <template #default="{ row }">¥{{ row.current_price?.toFixed(2) }}</template>
            </el-table-column>
            <el-table-column label="折扣率" width="100" sortable>
              <template #default="{ row }">
                <span :class="getDiscountClass(row)">
                  {{ getDiscount(row) }}%
                </span>
              </template>
            </el-table-column>
            <el-table-column prop="status" label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="row.status === 'active' ? 'success' : 'info'">{{ row.status === 'active' ? '活跃' : '停用' }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="remark" label="备注" />
          </el-table>
          
          <!-- 分页 -->
          <div class="pagination-container">
            <el-pagination
              v-model:current-page="currentPage"
              v-model:page-size="pageSize"
              :page-sizes="[10, 20, 50, 100]"
              :total="total"
              layout="total, sizes, prev, pager, next, jumper"
              @size-change="handleSizeChange"
              @current-change="handleCurrentChange"
            />
          </div>
        </el-card>
      </el-main>
    </el-container>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { Search } from '@element-plus/icons-vue'
import { watchlist } from '../api'
import { ElMessage } from 'element-plus'

const loading = ref(false)
const allList = ref([])
const filteredList = ref([])
const currentPage = ref(1)
const pageSize = ref(20)

const searchForm = ref({
  keyword: '',
  status: ''
})

// 过滤后的列表
const paginatedList = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredList.value.slice(start, end)
})

// 总数
const total = computed(() => filteredList.value.length)

// 获取折扣率
const getDiscount = (row) => {
  if (!row.target_price || !row.current_price || row.current_price === 0) return 0
  return ((1 - row.current_price / row.target_price) * 100).toFixed(1)
}

// 折扣率样式
const getDiscountClass = (row) => {
  const discount = parseFloat(getDiscount(row))
  if (discount > 10) return 'discount-high'
  if (discount > 5) return 'discount-medium'
  if (discount > 0) return 'discount-low'
  return 'discount-negative'
}

// 搜索
const handleSearch = () => {
  filteredList.value = allList.value.filter(item => {
    const matchKeyword = !searchForm.value.keyword || 
      item.stock_code.includes(searchForm.value.keyword) || 
      item.stock_name.includes(searchForm.value.keyword)
    const matchStatus = !searchForm.value.status || item.status === searchForm.value.status
    return matchKeyword && matchStatus
  })
  currentPage.value = 1
  ElMessage.success(`找到 ${filteredList.value.length} 条记录`)
}

// 重置搜索
const resetSearch = () => {
  searchForm.value = { keyword: '', status: '' }
  handleSearch()
}

// 分页事件
const handleSizeChange = () => { currentPage.value = 1 }
const handleCurrentChange = () => { window.scrollTo(0, 0) }

// 加载数据
onMounted(async () => {
  loading.value = true
  try {
    const res = await watchlist.getList()
    if (res.data.success) {
      allList.value = res.data.data
      filteredList.value = res.data.data
    }
  } catch (e) {
    ElMessage.error('加载数据失败')
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.watchlist {
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

.discount-high { color: #f56c6c; font-weight: bold; }
.discount-medium { color: #e6a23c; font-weight: bold; }
.discount-low { color: #67c23a; }
.discount-negative { color: #909399; }
</style>
