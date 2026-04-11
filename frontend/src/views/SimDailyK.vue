<template>
  <div class="sim-daily-k">
    <el-card shadow="never">
      <template #header>
        <div class="card-header">
          <span>📈 日 K 记录</span>
          <div class="header-info">
            <el-tag v-if="currentStock" type="success">{{ currentStock.name }}</el-tag>
            <el-tag v-if="currentPrice" type="warning">现价：¥{{ currentPrice.toFixed(2) }}</el-tag>
          </div>
        </div>
      </template>

      <!-- 查询条件 -->
      <div class="search-bar">
        <el-select
          v-model="searchForm.stockCode"
          placeholder="选择股票"
          filterable
          style="width: 240px"
          @change="onStockChange"
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
        <el-button type="primary" @click="loadDailyKData" :loading="loading">
          <el-icon><Search /></el-icon> 查询
        </el-button>
      </div>

      <!-- K 线图表 -->
      <div ref="kChartRef" class="k-chart" v-loading="loading"></div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { sim, dailyK } from '../api'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'

const loading = ref(false)
const stockList = ref([])
const kChartRef = ref(null)
const currentStock = ref(null)
const currentPrice = ref(0)
let kChartInstance = null

const defaultDateRange = computed(() => {
  const end = new Date()
  const start = new Date()
  start.setDate(start.getDate() - 30)  // 默认最近 30 天
  return [start.toISOString().split('T')[0], end.toISOString().split('T')[0]]
})

const searchForm = ref({
  stockCode: '',
  dateRange: []
})

// 加载股票列表
const loadStockList = async () => {
  try {
    const res = await sim.getList()
    if (res.data.success) {
      stockList.value = res.data.data.map(s => ({
        code: s.stock_code,
        name: s.stock_name,
        current_price: parseFloat(s.current_price) || 0
      }))
      if (stockList.value.length > 0) {
        searchForm.value.stockCode = stockList.value[0].code
        currentStock.value = stockList.value[0]
        currentPrice.value = stockList.value[0].current_price
        loadDailyKData()
      }
    }
  } catch (error) {
    console.error('加载股票列表失败:', error)
  }
}

// 股票选择变化
const onStockChange = (code) => {
  currentStock.value = stockList.value.find(s => s.code === code)
  currentPrice.value = currentStock.value?.current_price || 0
  loadDailyKData()
}

// 加载日 K 数据（使用真实数据）
const loadDailyKData = async () => {
  if (!searchForm.value.stockCode) return
  
  loading.value = true
  try {
    const dateRange = searchForm.value.dateRange || defaultDateRange.value
    const start = dateRange[0]
    const end = dateRange[1]
    console.log('默认日期范围:', defaultDateRange.value)
    console.log('查询日期范围:', start, end)
    console.log('股票代码:', searchForm.value.stockCode)
    
    // 获取真实日 K 数据
    const res = await dailyK.getData(searchForm.value.stockCode, start, end)
    if (res.data.success) {
      const kData = res.data.data
      
      if (kData.length === 0) {
        ElMessage.warning('暂无该股票日 K 数据')
        loading.value = false
        return
      }
      
      // 准备图表数据
      const dates = kData.map(item => item.date)
      const ohlcData = kData.map(item => [
        item.open,
        item.low,
        item.high,
        item.close
      ])
      const volumes = kData.map(item => item.volume)
      const ma5Data = kData.map(item => item.ma5)
      const ma10Data = kData.map(item => item.ma10)
      const ma20Data = kData.map(item => item.ma20)
      
      renderKChart(dates, ohlcData, volumes, { ma5Data, ma10Data, ma20Data })
    }
  } catch (error) {
    console.error('加载日 K 数据失败:', error)
    ElMessage.error('加载数据失败')
  } finally {
    loading.value = false
  }
}

// 渲染专业 K 线图表
const renderKChart = (dates, ohlcData, volumes, indicators) => {
  if (!kChartRef.value) return
  
  if (kChartInstance) {
    kChartInstance.dispose()
  }
  
  kChartInstance = echarts.init(kChartRef.value, 'light', {
    renderer: 'canvas',
    devicePixelRatio: window.devicePixelRatio || 1
  })
  
  // 专业金融配色
  const colorUp = '#ef232a'      // 红色（涨）
  const colorDown = '#14b143'    // 绿色（跌）
  const colorMa5 = '#ffd700'     // 金黄色
  const colorMa10 = '#00ced1'    // 青色
  const colorMa20 = '#ff69b4'    // 粉色
  
  const option = {
    backgroundColor: '#ffffff',
    animation: false,
    title: {
      text: `${searchForm.value.stockCode} 日 K 线图`,
      left: 'center',
      textStyle: {
        fontSize: 14,
        fontWeight: 'bold'
      }
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'cross'
      },
      borderWidth: 1,
      borderColor: '#ccc',
      padding: 10,
      textStyle: {
        fontSize: 12
      },
      formatter: (params) => {
        const dataIndex = params[0].dataIndex
        const data = ohlcData[dataIndex]
        const date = dates[dataIndex]
        const open = data[0].toFixed(2)
        const high = data[2].toFixed(2)
        const low = data[1].toFixed(2)
        const close = data[3].toFixed(2)
        const volume = volumes[dataIndex].toLocaleString()
        
        return `
          <div style="font-weight:bold;margin-bottom:5px;">${date}</div>
          <div>开盘：${open}</div>
          <div>最高：${high}</div>
          <div>最低：${low}</div>
          <div>收盘：${close}</div>
          <div>成交量：${volume}</div>
        `
      }
    },
    legend: {
      data: ['K 线', 'MA5', 'MA10', 'MA20', '成交量'],
      top: 30,
      textStyle: {
        fontSize: 11
      }
    },
    grid: [
      {
        left: '8%',
        right: '8%',
        height: '55%',
        top: '12%'
      },
      {
        left: '8%',
        right: '8%',
        top: '70%',
        height: '12%'
      }
    ],
    axisPointer: {
      link: [
        { xAxisIndex: [0, 1] }
      ]
    },
    xAxis: [
      {
        type: 'category',
        data: dates,
        scale: true,
        boundaryGap: false,
        axisLine: {
          lineStyle: {
            color: '#ccc'
          }
        },
        axisLabel: {
          fontSize: 10,
          rotate: 0,
          interval: Math.floor(dates.length / 10)
        },
        splitLine: {
          show: false
        },
        min: 'dataMin',
        max: 'dataMax'
      },
      {
        type: 'category',
        gridIndex: 1,
        data: dates,
        axisLabel: {
          show: false
        },
        axisLine: {
          lineStyle: {
            color: '#ccc'
          }
        },
        splitLine: {
          show: false
        }
      }
    ],
    yAxis: [
      {
        scale: true,
        name: '股价',
        nameLocation: 'middle',
        nameGap: 50,
        position: 'right',
        axisLine: {
          lineStyle: {
            color: '#ccc'
          }
        },
        axisLabel: {
          fontSize: 10,
          formatter: (value) => value.toFixed(2)
        },
        splitLine: {
          lineStyle: {
            color: '#f0f0f0',
            type: 'dashed'
          }
        }
      },
      {
        scale: true,
        gridIndex: 1,
        name: '成交量',
        nameLocation: 'middle',
        nameGap: 40,
        position: 'right',
        axisLine: {
          lineStyle: {
            color: '#ccc'
          }
        },
        axisLabel: {
          fontSize: 10,
          formatter: (value) => {
            if (value >= 1000000) {
              return (value / 1000000).toFixed(1) + 'M'
            } else if (value >= 1000) {
              return (value / 1000).toFixed(0) + 'K'
            }
            return value.toString()
          }
        },
        splitLine: {
          show: false
        }
      }
    ],
    dataZoom: [
      {
        type: 'inside',
        xAxisIndex: [0, 1],
        start: 50,
        end: 100,
        minValueSpan: 10
      },
      {
        show: true,
        xAxisIndex: [0, 1],
        type: 'slider',
        top: '95%',
        height: 20,
        start: 50,
        end: 100,
        borderColor: '#ddd',
        fillerColor: 'rgba(0,0,0,0.1)',
        handleStyle: {
          color: '#999'
        }
      }
    ],
    series: [
      {
        name: 'K 线',
        type: 'candlestick',
        data: ohlcData,
        itemStyle: {
          color: colorUp,
          color0: colorDown,
          borderColor: colorUp,
          borderColor0: colorDown,
          borderWidth: 2
        },
        barMaxWidth: 20,
        barMinWidth: 8,
        zlevel: 1
      },
      {
        name: 'MA5',
        type: 'line',
        data: indicators.ma5Data,
        smooth: true,
        lineStyle: {
          width: 1,
          color: colorMa5,
          type: 'solid'
        },
        symbol: 'none',
        zlevel: 2
      },
      {
        name: 'MA10',
        type: 'line',
        data: indicators.ma10Data,
        smooth: true,
        lineStyle: {
          width: 1,
          color: colorMa10,
          type: 'solid'
        },
        symbol: 'none',
        zlevel: 2
      },
      {
        name: 'MA20',
        type: 'line',
        data: indicators.ma20Data,
        smooth: true,
        lineStyle: {
          width: 1,
          color: colorMa20,
          type: 'solid'
        },
        symbol: 'none',
        zlevel: 2
      },
      {
        name: '成交量',
        type: 'bar',
        xAxisIndex: 1,
        yAxisIndex: 1,
        data: volumes.map((vol, idx) => {
          const open = ohlcData[idx][0]
          const close = ohlcData[idx][3]
          return {
            value: vol,
            itemStyle: {
              color: close >= open ? colorUp : colorDown,
              opacity: 0.8
            }
          }
        }),
        barMaxWidth: 15,
        zlevel: 1
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
  // 设置默认日期范围（最近 30 天）
  const end = new Date()
  const start = new Date()
  start.setDate(start.getDate() - 30)
  searchForm.value.dateRange = [
    start.toISOString().split('T')[0],
    end.toISOString().split('T')[0]
  ]
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

.header-info {
  display: flex;
  gap: 8px;
  align-items: center;
}

.search-bar {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
  flex-wrap: wrap;
  align-items: center;
}

.k-chart {
  width: 100%;
  height: 650px;
}
</style>
