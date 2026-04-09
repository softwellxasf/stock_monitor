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
        <el-form-item>
          <el-button type="primary" :loading="loading" @click="handleLogin" style="width: 100%">登录</el-button>
        </el-form-item>
      </el-form>
      
      <p class="hint">默认账号：admin / admin123</p>
    </el-card>
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

const form = reactive({ username: '', password: '' })

const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
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
        ElMessage.success('登录成功')
        router.push('/')
      } else {
        ElMessage.error(res.data.message || '登录失败')
      }
    } catch (e) {
      ElMessage.error('登录失败，请检查网络连接')
    } finally {
      loading.value = false
    }
  })
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
.hint {
  text-align: center;
  color: #999;
  font-size: 12px;
  margin-top: 15px;
}
</style>
