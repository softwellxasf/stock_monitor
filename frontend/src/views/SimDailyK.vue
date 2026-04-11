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
          :default-value="defaultDateRange"
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
import { sim } from '../api'
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
  start.setDate(start.getDate() - 60)
  return [start.toISOString().split('T')[0], end.toISOString().split('T')[0]]
})

const searchForm = ref({
  stockCode: '',
  dateRange: []
})

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

// 计算 MACD 指标
const calculateMACD = (data) => {
  const closes = data.map(item => item[1])
  const ema12 = []
  const ema26 = []
  
  // 计算 EMA12
  for (let i = 0; i < closes.length; i++) {
    if (i === 0) {
      ema12.push(closes[i])
    } else {
      ema12.push((closes[i] - ema12[i - 1]) * (2 / 13) + ema12[i - 1])
    }
  }
  
  // 计算 EMA26
  for (let i = 0; i < closes.length; i++) {
    if (i === 0) {
      ema26.push(closes[i])
    } else {
      ema26.push((closes[i] - ema26[i - 1]) * (2 / 27) + ema26[i - 1])
    }
  }
  
  // 计算 DIF、DEA、MACD
  const dif = []
  const dea = []
  const macd = []
  
  for (let i = 0; i < closes.length; i++) {
    dif.push(ema12[i] - ema26[i])
    
    if (i === 0) {
      dea.push(dif[i])
    } else {
      dea.push((dif[i] - dea[i - 1]) * (2 / 10) + dea[i - 1])
    }
    
    macd.push((dif[i] - dea[i]) * 2)
  }
  
  return { dif, dea, macd }
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
    const [start, end] = searchForm.value.dateRange || defaultDateRange.value
    
    // 获取持仓数据
    const positionsRes = await sim.getPositions()
    if (positionsRes.data.success) {
      const positions = positionsRes.data.data || []
      const stock = positions.find(p => p.stock_code === searchForm.value.stockCode)
      
      if (!stock) {
        ElMessage.warning('未找到该股票持仓数据')
        loading.value = false
        return
      }
      
      // 获取收益分析数据
      const analysisRes = await sim.getAnalysis(start, end)
      if (analysisRes.data.success) {
        const dailyData = analysisRes.data.data.daily_returns || []
        
        // 生成专业 K 线数据
        const kData = generateKData(dailyData, stock)
        
        // 计算技术指标
        const ma5 = calculateMA(kData, 5)
        const ma10 = calculateMA(kData, 10)
        const ma20 = calculateMA(kData, 20)
        const { dif, dea, macd } = calculateMACD(kData)
        
        renderKChart(kData, { ma5, ma10, ma20, dif, dea, macd })
      }
    }
  } catch (error) {
    console.error('加载日 K 数据失败:', error)
    ElMessage.error('加载数据失败')
  } finally {
    loading.value = false
  }
}

// 生成 K 线数据
const generateKData = (dailyData, stock) => {
  const currentPrice = parseFloat(stock.current_price) || 10
  
  return dailyData.map((d, index) => {
    const totalReturn = parseFloat(d.total_return) || 0
    const dailyReturn = parseFloat(d.daily_return) || 0
    
    // 计算股价
    const priceRatio = 1 + (totalReturn / 100) * (index / dailyData.length)
    const close = currentPrice * priceRatio
    
    // 根据日收益率生成 OHLC
    const dailyRatio = dailyReturn / 100
    const open = close / (1 + dailyRatio)
    const low = Math.min(open, close) * (0.98 + Math.random() * 0.015)
    const high = Math.max(open, close) * (1.015 + Math.random() * 0.015)
    
    // 生成成交量（与收益率正相关）
    const baseVolume = 500000
    const volume = Math.floor(baseVolume * (1 + Math.abs(dailyRatio) * 10) * (0.8 + Math.random() * 0.4))
    
    return [
      d.date,      // 0: 日期
      close,       // 1: 收盘价
      open,        // 2: 开盘价
      low,         // 3: 最低价
      high,        // 4: 最高价
      volume       // 5: 成交量
    ]
  })
}

// 渲染专业 K 线图表
const renderKChart = (kData, indicators) => {
  if (!kChartRef.value) return
  
  if (kChartInstance) {
    kChartInstance.dispose()
  }
  
  kChartInstance = echarts.init(kChartRef.value, 'light', {
    renderer: 'canvas',
    devicePixelRatio: window.devicePixelRatio || 1
  })
  
  const dates = kData.map(item => item[0])
  const closes = kData.map(item => item[1])
  const volumes = kData.map(item => item[5])
  
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
        const data = kData[params[0].dataIndex]
        const date = data[0]
        const open = data[2].toFixed(2)
        const high = data[4].toFixed(2)
        const low = data[3].toFixed(2)
        const close = data[1].toFixed(2)
        const volume = data[5].toLocaleString()
        
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
        data: kData.map(item => [
          item[2], // open
          item[3], // low
          item[4], // high
          item[1]  // close
        ]),
        itemStyle: {
          color: colorUp,
          color0: colorDown,
          borderColor: colorUp,
          borderColor0: colorDown,
          borderWidth: 1
        },
        barMaxWidth: 15,
        zlevel: 1
      },
      {
        name: 'MA5',
        type: 'line',
        data: indicators.ma5,
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
        data: indicators.ma10,
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
        data: indicators.ma20,
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
          const open = kData[idx][2]
          const close = kData[idx][1]
          return {
            value: vol,
            itemStyle: {
              color: close >= open ? colorUp : colorDown
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
