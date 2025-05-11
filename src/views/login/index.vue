<template>
  <div class="login-container">
    <div class="login-box">
      <h2>系统登录</h2>
      <form @submit.prevent="handleLogin" style="width: 100%;">
        <div class="form-group">
          <el-input
            class="custom-el-input"
            type="password"
            v-model="password"
            placeholder="请输入密码"
            required
          />
        </div>
        <button type="submit" :disabled="loading">
          {{ loading ? '登录中...' : '登录' }}
        </button>
      </form>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { login } from '../../api/auth'
import { ElMessage } from 'element-plus'

export default {
  name: 'Login',
  setup() {
    const router = useRouter()
    const password = ref('')
    const loading = ref(false)

    const handleLogin = async () => {
      try {
        loading.value = true
        const result = await login(password.value)
        
        if (result.success) {
          router.push('/')
        } else {
          ElMessage.error('登录失败：' + result.error)
        }
      } catch (error) {
        ElMessage.error('登录失败：' + (error.response?.data?.error || error.message))
      } finally {
        loading.value = false
      }
    }

    return {
      password,
      loading,
      handleLogin
    }
  }
}
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background: linear-gradient(135deg, #e3f0ff 0%, #f8fbff 100%);
}

.login-box {
  width: 370px;
  padding: 40px 32px 32px 32px;
  background: #fff;
  border-radius: 18px;
  box-shadow: 0 8px 32px 0 rgba(27, 151, 249, 0.10), 0 1.5px 6px 0 rgba(0,0,0,0.04);
  display: flex;
  flex-direction: column;
  align-items: center;
}

h2 {
  text-align: center;
  margin-bottom: 32px;
  color: #1B97F9;
  font-size: 26px;
  font-weight: 700;
  letter-spacing: 2px;
}

.form-group {
  width: 100%;
  margin-bottom: 24px;
}

/* 深度选择器适配 el-input 内部结构 */
.custom-el-input {
  --el-input-bg-color: #f7fbff;
  --el-input-border-color: #e3eaf2;
  --el-input-hover-border-color: #1B97F9;
  --el-input-focus-border-color: #1B97F9;
  --el-input-placeholder-color: #b0b8c9;
  --el-input-text-color: #333;
  width: 100%;
  border-radius: 8px;
  font-size: 16px;
}

/* 兼容性写法，进一步美化 */
.custom-el-input .el-input__wrapper {
  border-radius: 8px !important;
  box-shadow: none !important;
  background: #f7fbff !important;
  border: 1.5px solid #e3eaf2 !important;
  transition: border-color 0.2s;
}

.custom-el-input .el-input__wrapper:hover,
.custom-el-input .el-input__wrapper.is-focus {
  border-color: #1B97F9 !important;
  background: #fff !important;
}

.custom-el-input .el-input__inner {
  color: #333 !important;
  font-size: 16px !important;
  background: transparent !important;
}

.custom-el-input .el-input__inner::placeholder {
  color: #b0b8c9 !important;
  font-size: 15px;
}

button {
  width: 100%;
  padding: 13px 0;
  background: linear-gradient(90deg, #1B97F9 0%, #4fc3f7 100%);
  color: #fff;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 17px;
  font-weight: 600;
  letter-spacing: 1px;
  box-shadow: 0 2px 8px 0 rgba(27, 151, 249, 0.10);
  transition: background 0.2s, box-shadow 0.2s;
}

button:disabled {
  background: #b3d8fb;
  cursor: not-allowed;
  color: #fff;
}

button:hover:not(:disabled) {
  background: linear-gradient(90deg, #1B97F9 0%, #1976d2 100%);
  box-shadow: 0 4px 16px 0 rgba(27, 151, 249, 0.15);
}
</style> 