<template>
  <div class="login-container">
    <el-card class="login-card">
      <h2 class="title">📊 stockMonitor</h2>
      <p class="subtitle">股票监控系统</p>
      
      <el-form :model="form" :rules="rules" ref="formRef">
        <el-form-item prop="username">
          <el-input v-model="form.username" placeholder="用户名" prefix-icon="User" />
        </el-form-item>
        <el-form-item prop="password">
          <el-input v-model="form.password" type="password" placeholder="密码" prefix-icon="Lock" @keyup.enter="handleLogin" />
        </el-form-item>
        
        <!-- 验证码（错误 2 次后显示） -->
        <el-form-item prop="captcha" v-if="showCaptcha">
          <div class="captcha-row">
            <el-input v-model="form.captcha" placeholder="拖动滑块验证" :disabled="captchaVerified" style="width: 200px" />
            <el-button :disabled="captchaVerified" @click="showCaptchaModal = true">
              {{ captchaVerified ? '✅ 已验证' : '🔒 验证' }}
            </el-button>
          </div>
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" :loading="loading" @click="handleLogin" style="width: 100%">登录</el-button>
        </el-form-item>
      </el-form>
      
      <el-alert v-if="showCaptcha" type="warning" :closable="false" style="margin-top: 10px">
        <i>安全提示：连续登录失败，需要验证码</i>
      </el-alert>
    </el-card>
    
    <!-- 拖拉验证码弹窗 -->
    <el-dialog v-model="showCaptchaModal" title="安全验证" width="400px" :close-on-click-modal="false">
      <div class="captcha-container">
        <div class="captcha-bg" :style="{ height: '40px', background: '#f0f0f0', position: 'relative', borderRadius: '4px' }">
          <div class="captcha-block" :style="{
            position: 'absolute',
            left: blockPosition + 'px',
            top: '0',
            width: '50px',
            height: '40px',
            background: '#409EFF',
            transition: 'left 0.3s'
          }"></div>
          <el-slider v-model="blockPosition" :min="0" :max="300" :step="1" 
                     @change="handleCaptchaSlide" style="position: absolute; width: 350px; top: 5px; left: 10px" />
        </div>
        <p style="text-align: center; margin-top: 15px; color: #666">拖动滑块完成验证</p>
      </div>
      <template #footer>
        <el-button @click="showCaptchaModal = false; resetCaptcha()">重置</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { auth } from '../api'

const router = useRouter()
const formRef = ref(null)
const loading = ref(false)
const failedCount = ref(parseInt(localStorage.getItem('login_failed_count') || '0'))
const showCaptcha = ref(failedCount.value >= 2)
const showCaptchaModal = ref(false)
const blockPosition = ref(0)
const captchaVerified = ref(false)

const form = reactive({ username: '', password: '', captcha: '' })

const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
  captcha: [{ 
    validator: (rule, value, callback) => {
      if (showCaptcha.value && !captchaVerified.value) {
        callback(new Error('请先完成滑块验证'))
      } else {
        callback()
      }
    },
    trigger: 'blur'
  }]
}

const handleCaptchaSlide = (value) => {
  if (value >= 280 && value <= 300) {
    captchaVerified.value = true
    showCaptchaModal.value = false
    form.captcha = 'verified'
    ElMessage.success('验证通过')
  }
}

const resetCaptcha = () => {
  blockPosition.value = 0
  captchaVerified.value = false
  form.captcha = ''
}

const handleLogin = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (!valid) return
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
  if (failedCount.value >= 2) {
    showCaptcha.value = true
  }
}
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
  width: 400px;
  padding: 20px;
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
.captcha-row {
  display: flex;
  align-items: center;
  gap: 10px;
}
.captcha-container {
  padding: 20px;
}
</style>
