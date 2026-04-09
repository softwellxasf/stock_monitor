<template>
  <div class="real-positions">
    <el-card shadow="never">
      <template #header>
        <div class="card-header">
          <span>💼 实盘持仓</span>
          <el-tag type="warning" size="small">实盘</el-tag>
        </div>
      </template>
      
      <el-alert
        title="实盘数据接入中..."
        type="warning"
        :closable="false"
        style="margin-bottom: 20px"
        show-icon
      >
        实盘数据需要从券商 API 或手动导入，当前显示示例数据
      </el-alert>
      
      <el-table :data="sampleData" stripe style="width: 100%">
        <el-table-column prop="stock_code" label="代码" width="120" />
        <el-table-column prop="stock_name" label="名称" width="120" />
        <el-table-column prop="quantity" label="数量" width="100" />
        <el-table-column prop="cost_price" label="成本价" width="100">
          <template #default="{ row }">¥{{ row.cost_price?.toFixed(2) }}</template>
        </el-table-column>
        <el-table-column prop="current_price" label="现价" width="100">
          <template #default="{ row }">¥{{ row.current_price?.toFixed(2) }}</template>
        </el-table-column>
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
    </el-card>
  </div>
</template>

<script setup>
const sampleData = [
  { stock_code: '600519.SH', stock_name: '贵州茅台', quantity: 100, cost_price: 1680.00, current_price: 1750.00, profit_pct: 4.17 },
  { stock_code: '000858.SZ', stock_name: '五粮液', quantity: 500, cost_price: 95.00, current_price: 92.00, profit_pct: -3.16 },
  { stock_code: '300750.SZ', stock_name: '宁德时代', quantity: 200, cost_price: 180.00, current_price: 195.00, profit_pct: 8.33 }
]
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

.profit {
  color: #f56c6c;
  font-weight: bold;
}

.loss {
  color: #67c23a;
  font-weight: bold;
}
</style>
