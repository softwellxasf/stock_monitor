<template>
  <div class="sim-daily-k">
    <el-card shadow="never">
      <template #header>
        <div class="card-header">
          <span>📈 日 K 记录</span>
        </div>
      </template>

      <!-- 查询条件 -->
      <div class="search-bar">
        <el-select
          v-model="searchForm.stockCode"
          placeholder="选择股票"
          style="width: 200px"
          @change="loadDailyKData"
        >
          <el-option
            v-for="stock in stockList"
            :key="stock.code"
            :label="`${stock.code} ${stock.name}`"
            :value="stock.code"
          />
        </el-select>
        <el-date-picker
          v-model="searchForm.dateRange"
          type="daterange"
          range-separator="至"
          start-placeholder="开始日期"
          end-placeholder="结束日期"
          value-format="YYYY-MM-DD"
          style="width: 240px"
          @change="loadDailyKData"
        />
        <el-button type="primary" @click="loadDailyKData">查询</el-button>
      </div>

      <!-- K 线图表 -->
      <div ref="kChartRef" class="k-chart" v-loading="loading"></div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { sim } from '../api'
import * as echarts from 'echarts'

const loading = ref(false)
const stockList = ref([])
const kChartRef = ref(null)
let kChartInstance = null

const searchForm = ref({
  stockCode: '',
  dateRange: []
})

// 计算 MACD 指标
const calculateMACD = (prices, shortPeriod = 12, longPeriod = 26, signalPeriod = 9) => {
  const macdData = []
  const emaShort = []
  const emaLong = []
  
  // 计算 EMA
  const calculateEMA = (data, period) => {
    const ema = []
    const multiplier = 2 / (period + 1)
    
    for (let i = 0; i < data.length; i++) {
      if (i === 0) {
        ema.push(data[i])
      } else {
        ema.push((data[i] - ema[i - 1]) * multiplier + ema[i - 1])
      }
    }
    return ema
  }
  
  // 计算收盘价 EMA
  const closePrices = prices.map(p => p[1]) // [date, close, open, low, high, volume]
  emaShort.push(...calculateEMA(closePrices, shortPeriod))
  emaLong.push(...calculateEMA(closePrices, longPeriod))
  
  // 计算 DIF 和 DEA
  for (let i = 0; i < prices.length; i++) {
    const dif = emaShort[i] - emaLong[i]
    
    // 计算 DEA (DIF 的 EMA)
    let dea = 0
    if (i === 0) {
      dea = dif
    } else {
      const prevDea = macdData[i - 1] ? macdData[i - 1][1] : dif
      dea = (dif - prevDea) * (2 / (signalPeriod + 1)) + prevDea
    }
    
    // 计算 MACD 柱
    const macd = 2 * (dif - dea)
    
    macdData.push([dif, dea, macd])
  }
  
  return macdData
}

// 加载股票列表
const loadStockList = async () => {
  try {
    const res = await sim.getList()
    if (res.data.success) {
      stockList.value = res.data.data.map(s => ({
        code: s.stock_code,
        name: s.stock_name
      }))
      if (stockList.value.length > 0) {
        searchForm.value.stockCode = stockList.value[0].code
        loadDailyKData()
      }
    }
  } catch (error) {
    console.error('加载股票列表失败:', error)
  }
}

// 加载日 K 数据
const loadDailyKData = async () => {
  if (!searchForm.value.stockCode) return
  
  loading.value = true
  try {
    const [start, end] = searchForm.value.dateRange || []
    const res = await sim.getAnalysis(start, end)
    if (res.data.success) {
      const dailyData = res.data.data.daily_returns || []
      
      // 转换为 K 线数据格式 [date, close, open, low, high, volume]
      const kData = dailyData.map(d => [
        d.date,
        d.total_asset, // 使用总资产作为 close
        d.total_asset * 0.98, // 估算 open
        d.total_asset * 0.95, // 估算 low
        d.total_asset * 1.05, // 估算 high
        Math.random() * 1000000 // 估算 volume
      ])
      
      // 计算 MACD
      const macdData = calculateMACD(kData)
      
      renderKChart(kData, macdData)
    }
  } catch (error) {
    console.error('加载日 K 数据失败:', error)
  } finally {
    loading.value = false
  }
}

// 渲染 K 线图表
const renderKChart = (kData, macdData) => {
  if (!kChartRef.value) return
  
  if (kChartInstance) {
    kChartInstance.dispose()
  }
  
  kChartInstance = echarts.init(kChartRef.value)
  
  const dates = kData.map(item => item[0])
  
  const option = {
    title: {
      text: `${searchForm.value.stockCode} 日 K 线图`,
      left: 'center'
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'cross'
      }
    },
    grid: [
      {
        left: '10%',
        right: '8%',
        height: '50%',
        top: '10%'
      },
      {
        left: '10%',
        right: '8%',
        top: '65%',
        height: '15%'
      },
      {
        left: '10%',
        right: '8%',
        top: '82%',
        height: '15%'
      }
    ],
    xAxis: [
      {
        type: 'category',
        data: dates,
        scale: true,
        boundaryGap: false,
        axisLine: { onZero: false },
        splitLine: { show: false },
        min: 'dataMin',
        max: 'dataMax'
      },
      {
        type: 'category',
        gridIndex: 1,
        data: dates,
        axisLabel: { show: false }
      },
      {
        type: 'category',
        gridIndex: 2,
        data: dates,
        axisLabel: { show: false }
      }
    ],
    yAxis: [
      {
        scale: true,
        splitArea: { show: true }
      },
      {
        scale: true,
        gridIndex: 1,
        splitNumber: 2,
        axisLabel: { show: false },
        axisLine: { show: false },
        splitLine: { show: false }
      },
      {
        scale: true,
        gridIndex: 2,
        splitNumber: 2,
        axisLabel: { show: false },
        axisLine: { show: false },
        splitLine: { show: false }
      }
    ],
    dataZoom: [
      {
        type: 'inside',
        xAxisIndex: [0, 1, 2],
        start: 50,
        end: 100
      },
      {
        show: true,
        xAxisIndex: [0, 1, 2],
        type: 'slider',
        top: '95%',
        start: 50,
        end: 100
      }
    ],
    series: [
      {
        name: '日 K',
        type: 'candlestick',
        data: kData.map(item => [
          item[2], // open
          item[3], // low
          item[4], // high
          item[1]  // close
        ]),
        itemStyle: {
          color: '#ec0000',
          color0: '#00da3c',
          borderColor: '#ec0000',
          borderColor0: '#00da3c'
        }
      },
      {
        name: '成交量',
        type: 'bar',
        xAxisIndex: 1,
        yAxisIndex: 1,
        data: kData.map(item => item[5]),
        itemStyle: {
          color: (params) => {
            const dataIndex = params.dataIndex
            const kDataItem = kData[dataIndex]
            return kDataItem[1] >= kDataItem[2] ? '#ec0000' : '#00da3c'
          }
        }
      },
      {
        name: 'DIF',
        type: 'line',
        xAxisIndex: 2,
        yAxisIndex: 2,
        data: macdData.map(item => item[0]),
        smooth: true,
        lineStyle: {
          width: 1,
          color: '#FFD700'
        }
      },
      {
        name: 'DEA',
        type: 'line',
        xAxisIndex: 2,
        yAxisIndex: 2,
        data: macdData.map(item => item[1]),
        smooth: true,
        lineStyle: {
          width: 1,
          color: '#00FFFF'
        }
      },
      {
        name: 'MACD',
        type: 'bar',
        xAxisIndex: 2,
        yAxisIndex: 2,
        data: macdData.map(item => item[2]),
        itemStyle: {
          color: (params) => {
            return params.value >= 0 ? '#ec0000' : '#00da3c'
          }
        }
      }
    ]
  }
  
  kChartInstance.setOption(option)
}

// 窗口大小变化时重新渲染图表
window.addEventListener('resize', () => {
  if (kChartInstance) {
    kChartInstance.resize()
  }
})

onMounted(() => {
  loadStockList()
})
</script>

<style scoped>
.sim-daily-k {
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

.k-chart {
  width: 100%;
  height: 600px;
}
</style>
