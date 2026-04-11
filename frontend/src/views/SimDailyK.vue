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

      <!-- K 线图表容器 -->
      <div ref="chartContainer" class="chart-container" v-loading="loading"></div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { sim, dailyK } from '../api'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'

const loading = ref(false)
const stockList = ref([])
const chartContainer = ref(null)
const currentStock = ref(null)
const currentPrice = ref(0)
const tradeRecords = ref([])

let chart = null
const colorUp = '#FF0000'      // 红色（涨）
const colorDown = '#00CC00'    // 绿色（跌）

const defaultDateRange = computed(() => {
  const end = new Date()
  const start = new Date()
  start.setDate(start.getDate() - 180)
  return [start.toISOString().split('T')[0], end.toISOString().split('T')[0]]
})

const searchForm = ref({
  stockCode: '',
  dateRange: []
})

// 初始化图表
const initChart = () => {
  if (!chartContainer.value) return
  
  // 销毁旧图表
  if (chart) {
    chart.dispose()
  }
  
  // 创建新图表
  chart = echarts.init(chartContainer.value, 'light', {
    renderer: 'canvas',
    devicePixelRatio: window.devicePixelRatio || 1
  })
  
  // 窗口大小变化时重新渲染
  window.addEventListener('resize', handleResize)
}

// 处理窗口大小变化
const handleResize = () => {
  if (chart && chartContainer.value) {
    chart.resize()
  }
}

// 计算 MA 均线
const calculateMA = (data, period) => {
  const ma = []
  for (let i = 0; i < data.length; i++) {
    if (i < period - 1) {
      ma.push('-')
      continue
    }
    let sum = 0
    for (let j = 0; j < period; j++) {
      sum += data[i - j][1] // 使用收盘价
    }
    ma.push(sum / period)
  }
  return ma
}

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

// 加载日 K 数据
const loadDailyKData = async () => {
  if (!searchForm.value.stockCode) return
  
  loading.value = true
  try {
    const dateRange = searchForm.value.dateRange || defaultDateRange.value
    const [start, end] = dateRange
    
    console.log('查询日期范围:', start, end)
    console.log('股票代码:', searchForm.value.stockCode)
    
    // 获取真实日 K 数据
    const res = await dailyK.getData(searchForm.value.stockCode, start, end)
    
    // 获取交易记录
    const tradesRes = await sim.getTrades({
      stock_code: searchForm.value.stockCode,
      start_date: start,
      end_date: end
    })
    if (tradesRes.data.success) {
      tradeRecords.value = tradesRes.data.data || []
      console.log('交易记录:', tradeRecords.value.length, '条')
    }
    
    if (res.data.success) {
      const kData = res.data.data
      
      // 准备图表数据
      const dates = kData.map(item => item.date)
      const ohlcData = kData.map(item => [
        item.open,
        item.close,
        item.low,
        item.high
      ])
      const volumes = kData.map(item => item.volume)
      
      // 计算均线
      const ma5Data = calculateMA(ohlcData, 5)
      const ma10Data = calculateMA(ohlcData, 10)
      const ma20Data = calculateMA(ohlcData, 20)
      
      // 准备交易标记
      const markers = prepareMarkers(kData, dates)
      
      // 渲染图表
      renderChart(dates, ohlcData, volumes, { ma5Data, ma10Data, ma20Data }, markers)
      
      console.log('K 线数据:', kData.length, '条')
      console.log('交易记录:', tradeRecords.value.length, '条')
      console.log('交易标记:', markers.length, '个')
    }
  } catch (error) {
    console.error('加载日 K 数据失败:', error)
    ElMessage.error('加载数据失败')
  } finally {
    loading.value = false
  }
}

// 准备交易标记
const prepareMarkers = (kData, dates) => {
  const markers = []
  
  tradeRecords.value.forEach(trade => {
    const tradeDate = trade.trade_date?.split(' ')[0] || trade.trade_date
    const dataIndex = dates.indexOf(tradeDate)
    if (dataIndex === -1) return
    
    const candle = kData[dataIndex]
    const isTTrade = trade.remark?.includes('T') || trade.remark?.includes('做 T')
    
    if (trade.direction === 'BUY') {
      if (isTTrade) {
        // 做 T 买入：橙色小圆点
        markers.push({
          coord: [tradeDate, candle.low * 0.96],
          value: 'T',
          itemStyle: {
            color: '#FF9900',
            borderColor: '#FFFFFF',
            borderWidth: 1
          },
          symbol: 'circle',
          symbolSize: 8
        })
      } else {
        // 底仓买入：红色圆形 B
        markers.push({
          coord: [tradeDate, candle.low * 0.94],
          value: 'B',
          itemStyle: {
            color: '#FF4444',
            borderColor: '#FFFFFF',
            borderWidth: 1
          },
          symbol: 'circle',
          symbolSize: 12
        })
      }
    } else if (trade.direction === 'SELL') {
      if (isTTrade) {
        // 做 T 卖出：绿色小圆点
        markers.push({
          coord: [tradeDate, candle.high * 1.04],
          value: 'T',
          itemStyle: {
            color: '#00CC00',
            borderColor: '#FFFFFF',
            borderWidth: 1
          },
          symbol: 'circle',
          symbolSize: 8
        })
      } else {
        // 底仓卖出：蓝色圆形 S
        markers.push({
          coord: [tradeDate, candle.high * 1.06],
          value: 'S',
          itemStyle: {
            color: '#4488FF',
            borderColor: '#FFFFFF',
            borderWidth: 1
          },
          symbol: 'circle',
          symbolSize: 12
        })
      }
    }
  })
  
  return markers
}

// 渲染图表
const renderChart = (dates, ohlcData, volumes, indicators, markers) => {
  const option = {
    backgroundColor: '#FFFFFF',
    animation: false,
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
        const high = data[3].toFixed(2)
        const low = data[2].toFixed(2)
        const close = data[1].toFixed(2)
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
            color: '#333333'
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
            color: '#333333'
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
            color: '#333333'
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
            color: '#333333'
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
          width: 2,
          color: '#FFFFFF',
          type: 'solid',
          shadowColor: 'rgba(0,0,0,0.3)',
          shadowBlur: 2
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
          width: 2,
          color: '#FFD700',
          type: 'solid',
          shadowColor: 'rgba(0,0,0,0.3)',
          shadowBlur: 2
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
          width: 2,
          color: '#00FFFF',
          type: 'solid',
          shadowColor: 'rgba(0,0,0,0.3)',
          shadowBlur: 2
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
          const close = ohlcData[idx][1]
          return {
            value: vol,
            itemStyle: {
              color: close >= open ? colorUp : colorDown,
              opacity: 0.8
            }
          }
        }),
        barMaxWidth: 20,
        zlevel: 1
      },
      {
        name: '交易标记',
        type: 'scatter',
        xAxisIndex: 0,
        yAxisIndex: 0,
        data: markers,
        symbol: (value, params) => {
          return params.data.symbol || 'circle'
        },
        symbolSize: (value, params) => {
          return params.data.symbolSize || 10
        },
        itemStyle: {
          color: (params) => {
            return params.data.itemStyle?.color || '#FF0000'
          },
          borderColor: '#FFFFFF',
          borderWidth: 1
        },
        label: {
          show: true,
          formatter: (params) => {
            return params.data.value || ''
          },
          color: '#FFFFFF',
          fontSize: 10,
          fontWeight: 'bold',
          position: 'inside'
        },
        zlevel: 3
      }
    ]
  }
  
  chart.setOption(option)
}

// 清理资源
onUnmounted(() => {
  if (chart) {
    chart.dispose()
    window.removeEventListener('resize', handleResize)
  }
})

onMounted(() => {
  initChart()
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

.chart-container {
  width: 100%;
  height: 600px;
}
</style>
