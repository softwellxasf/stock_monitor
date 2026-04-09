<template>
  <div class="real-analysis">
    <el-row :gutter="20">
      <el-col :span="8">
        <el-card shadow="never">
          <template #header>
            <div class="card-header">
              <span>总收益</span>
              <el-icon color="#f56c6c"><TrendCharts /></el-icon>
            </div>
          </template>
          <div class="stat-value real">+¥12,345</div>
          <div class="stat-sub">+8.23%</div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="never">
          <template #header>
            <div class="card-header">
              <span>今日盈亏</span>
              <el-icon color="#409EFF"><Money /></el-icon>
            </div>
          </template>
          <div class="stat-value">+¥1,234</div>
          <div class="stat-sub">+0.82%</div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="never">
          <template #header>
            <div class="card-header">
              <span>持仓股数</span>
              <el-icon color="#e6a23c"><List /></el-icon>
            </div>
          </template>
          <div class="stat-value">3 只</div>
          <div class="stat-sub">2 盈 1 亏</div>
        </el-card>
      </el-col>
    </el-row>
    
    <el-card style="margin-top: 20px" shadow="never">
      <template #header>
        <div class="card-header">
          <span>💼 实盘收益分析</span>
          <el-tag type="warning" size="small">实盘</el-tag>
        </div>
      </template>
      
      <el-alert
        title="实盘数据接入中..."
        type="warning"
        :closable="false"
        style="margin-bottom: 20px"
        show-icon
      />
      
      <div class="chart-placeholder">
        <el-empty description="收益趋势图开发中..." :image-size="100" />
      </div>
    </el-card>
  </div>
</template>

<script setup>
</script>

<style scoped>
.real-analysis {
  padding: 10px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.stat-value {
  font-size: 28px;
  font-weight: bold;
  color: #f56c6c;
  text-align: center;
  padding: 15px 0;
}

.stat-sub {
  text-align: center;
  color: #909399;
  font-size: 14px;
  padding-bottom: 15px;
}

.chart-placeholder {
  height: 300px;
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>
