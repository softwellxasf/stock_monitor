<template>
  <div class="login-container">
    <el-card class="login-card">
      <h2 class="title">📊 stockMonitor</h2>
      <p class="subtitle">股票监控系统</p>
      
      <el-form :model="form" :rules="rules" ref="formRef">
        <el-form-item prop="username">
          <el-input v-model="form.username" placeholder="用户名" prefix-icon="User" size="large" />
        </el-form-item>
        <el-form-item prop="password">
          <el-input v-model="form.password" type="password" placeholder="密码" prefix-icon="Lock" size="large" @keyup.enter="handleLogin" />
        </el-form-item>
        
        <!-- 验证码（错误 2 次后显示） -->
        <el-form-item v-if="showCaptcha" class="captcha-item">
          <div class="captcha-wrapper" ref="captchaContainer">
            <!-- 背景图 -->
            <div class="captcha-bg" :style="{ width: '300px', height: '160px', background: captchaBg, position: 'relative', borderRadius: '4px', overflow: 'hidden' }">
              <!-- 拼图块 -->
              <div class="puzzle-piece" :style="{
                position: 'absolute',
                left: puzzlePosition + 'px',
                top: puzzleTop + 'px',
                width: '50px',
                height: '50px',
                background: captchaBg,
                backgroundPosition: `-${puzzlePosition}px -${puzzleTop}px`,
                transition: slideSuccess ? 'left 0.3s' : 'none',
                boxShadow: '0 0 10px rgba(0,0,0,0.3)',
                zIndex: 2
              }"></div>
              <!-- 缺口 -->
              <div class="puzzle-hole" :style="{
                position: 'absolute',
                right: '10px',
                top: puzzleTop + 'px',
                width: '50px',
                height: '50px',
                background: 'rgba(255,255,255,0.8)',
                boxShadow: 'inset 0 0 10px rgba(0,0,0,0.2)',
                zIndex: 1
              }"></div>
            </div>
            
            <!-- 滑块 -->
            <div class="slider-container">
              <div class="slider-track" :style="{ 
                background: slideSuccess ? '#67c23a' : (slideFailed ? '#f56c6c' : '#e4e7ed'),
                height: '40px',
                borderRadius: '20px',
                position: 'relative',
                overflow: 'hidden'
              }">
                <!-- 进度条 -->
                <div class="slider-progress" :style="{
                  width: sliderOffset + 'px',
                  height: '100%',
                  background: slideSuccess ? '#67c23a' : (slideFailed ? '#f56c6c' : '#409EFF'),
                  opacity: 0.3,
                  transition: slideFailed ? 'width 0.3s' : 'none'
                }"></div>
                
                <!-- 滑块按钮 -->
                <div class="slider-button" :style="{
                  left: sliderOffset + 'px',
                  top: '0',
                  position: 'absolute',
                  width: '50px',
                  height: '40px',
                  background: slideSuccess ? '#67c23a' : (slideFailed ? '#f56c6c' : '#fff'),
                  border: '2px solid ' + (slideSuccess ? '#67c23a' : (slideFailed ? '#f56c6c' : '#409EFF')),
                  borderRadius: '20px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  cursor: isDragging ? 'grabbing' : 'grab',
                  boxShadow: '0 2px 8px rgba(0,0,0,0.2)',
                  transition: slideFailed ? 'left 0.3s' : 'none',
                  userSelect: 'none'
                }" @mousedown="startDrag" @touchstart="startDrag">
                  <span v-if="slideSuccess">✓</span>
                  <span v-else-if="slideFailed">✗</span>
                  <span v-else>➜</span>
                </div>
                
                <!-- 提示文字 -->
                <div class="slider-text">{{ sliderText }}</div>
              </div>
            </div>
            
            <!-- 刷新按钮 -->
            <el-button size="small" @click="initCaptcha" style="margin-top: 10px">
              🔄 换一张
            </el-button>
          </div>
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" :loading="loading" @click="handleLogin" size="large" style="width: 100%">登录</el-button>
        </el-form-item>
      </el-form>
      
      <el-alert v-if="showCaptcha" type="warning" :closable="false" show-icon style="margin-top: 10px">
        <i>安全验证：请拖动滑块完成拼图</i>
      </el-alert>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { auth } from '../api'

const router = useRouter()
const formRef = ref(null)
const loading = ref(false)
const failedCount = ref(parseInt(localStorage.getItem('login_failed_count') || '0'))
const showCaptcha = ref(failedCount.value >= 2)
const captchaVerified = ref(false)

const form = reactive({ username: '', password: '' })

const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
}

// 验证码相关
const captchaContainer = ref(null)
const captchaBg = ref('')
const puzzlePosition = ref(0)
const puzzleTop = ref(0)
const sliderOffset = ref(0)
const isDragging = ref(false)
const slideSuccess = ref(false)
const slideFailed = ref(false)
const targetPosition = ref(250)

// ⭐ 容错范围：±15px（更容易通过）
const tolerance = 15

const sliderText = computed(() => {
  if (slideSuccess.value) return '验证通过 ✓'
  if (slideFailed.value) return '验证失败 ✗'
  return '向右拖动滑块完成拼图'
})

// 生成随机背景色
const generateCaptchaBg = () => {
  const gradients = [
    'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    'linear-gradient(120deg, #f6d365 0%, #fda085 100%)',
    'linear-gradient(120deg, #84fab0 0%, #8fd3f4 100%)',
    'linear-gradient(120deg, #a1c4fd 0%, #c2e9fb 100%)',
    'linear-gradient(120deg, #d4fc79 0%, #96e6a1 100%)'
  ]
  return gradients[Math.floor(Math.random() * gradients.length)]
}

// 初始化验证码
const initCaptcha = () => {
  captchaBg.value = generateCaptchaBg()
  puzzlePosition.value = 0
  puzzleTop.value = Math.floor(Math.random() * 80) + 20
  sliderOffset.value = 0
  slideSuccess.value = false
  slideFailed.value = false
  // 目标位置范围缩小，更容易命中
  targetPosition.value = Math.floor(Math.random() * 30) + 235
}

// 开始拖动
const startDrag = (e) => {
  if (slideSuccess.value || slideFailed.value) return
  isDragging.value = true
  document.addEventListener('mousemove', onDrag)
  document.addEventListener('mouseup', stopDrag)
  document.addEventListener('touchmove', onDrag, { passive: false })
  document.addEventListener('touchend', stopDrag)
}

// 拖动中
const onDrag = (e) => {
  if (!isDragging.value) return
  e.preventDefault()
  const clientX = e.touches ? e.touches[0].clientX : e.clientX
  const rect = captchaContainer.value.getBoundingClientRect()
  const newOffset = Math.min(Math.max(0, clientX - rect.left - 25), 250)
  sliderOffset.value = newOffset
  puzzlePosition.value = newOffset
}

// 停止拖动
const stopDrag = () => {
  isDragging.value = false
  document.removeEventListener('mousemove', onDrag)
  document.removeEventListener('mouseup', stopDrag)
  document.removeEventListener('touchmove', onDrag)
  document.removeEventListener('touchend', stopDrag)
  
  // ⭐ 检查是否验证成功（容错±15px）
  const diff = Math.abs(sliderOffset.value - targetPosition.value)
  if (diff <= tolerance) {
    slideSuccess.value = true
    captchaVerified.value = true
    form.captcha = 'verified'
    ElMessage.success('验证通过 ✓')
  } else {
    slideFailed.value = true
    // 显示提示
    if (diff <= tolerance + 10) {
      ElMessage.warning('很接近了，再试试~')
    } else {
      ElMessage.error('验证失败，请重试')
    }
    setTimeout(() => {
      sliderOffset.value = 0
      puzzlePosition.value = 0
      slideFailed.value = false
    }, 800)
  }
}

const handleLogin = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    if (showCaptcha.value && !captchaVerified.value) {
      ElMessage.warning('请先完成滑块验证')
      return
    }
    loading.value = true
    try {
      const res = await auth.login(form.username, form.password)
      if (res.data.success) {
        localStorage.setItem('token', res.data.token)
        localStorage.setItem('login_failed_count', '0')
        ElMessage.success('登录成功')
        router.push('/')
      } else {
        handleLoginFailure()
        ElMessage.error(res.data.message || '登录失败')
      }
    } catch (e) {
      handleLoginFailure()
      ElMessage.error('登录失败，请检查网络连接')
    } finally {
      loading.value = false
    }
  })
}

const handleLoginFailure = () => {
  failedCount.value++
  localStorage.setItem('login_failed_count', failedCount.value.toString())
  if (failedCount.value >= 2 && !showCaptcha.value) {
    showCaptcha.value = true
    initCaptcha()
  }
}

// 初始化
initCaptcha()
</script>

<style scoped>
.login-container {
  height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}
.login-card {
  width: 420px;
  padding: 30px;
}
.title {
  text-align: center;
  font-size: 28px;
  color: #333;
  margin-bottom: 10px;
}
.subtitle {
  text-align: center;
  color: #666;
  margin-bottom: 30px;
}
.captcha-item {
  margin-bottom: 10px !important;
}
.captcha-wrapper {
  width: 100%;
}
.slider-container {
  margin-top: 15px;
}
.slider-track {
  position: relative;
}
.slider-text {
  position: absolute;
  width: 100%;
  text-align: center;
  line-height: 40px;
  color: #666;
  font-size: 14px;
  pointer-events: none;
  z-index: 1;
}
.puzzle-piece {
  border-radius: 4px;
}
</style>
