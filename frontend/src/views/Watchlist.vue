<template>
  <div class="watchlist">
    <el-container>
      <el-header><h2>⭐ 自选表</h2><el-button @click="$router.push('/')">返回</el-button></el-header>
      <el-main>
        <el-table :data="list" stripe style="width: 100%">
          <el-table-column prop="stock_code" label="代码" width="120" />
          <el-table-column prop="stock_name" label="名称" width="120" />
          <el-table-column prop="target_price" label="目标价" width="100" />
          <el-table-column prop="current_price" label="现价" width="100" />
          <el-table-column prop="remark" label="备注" />
        </el-table>
      </el-main>
    </el-container>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { watchlist } from '../api'

const list = ref([])

onMounted(async () => {
  const res = await watchlist.getList()
  if (res.data.success) list.value = res.data.data
})
</script>

<style scoped>
.watchlist { min-height: 100vh; background: #f5f7fa; }
.el-header { background: #fff; border-bottom: 1px solid #e4e7ed; padding: 0 20px; display: flex; justify-content: space-between; align-items: center; }
.el-main { padding: 20px; }
</style>
