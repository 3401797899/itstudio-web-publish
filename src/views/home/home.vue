<script setup>
import { ref, onMounted } from 'vue'
import { DataLine, Link } from '@element-plus/icons-vue'
import { getDomainList } from '../../api/domain'

const domainCount = ref(0)
const greeting = ref('')
const currentTime = ref('')

const updateGreeting = () => {
  const hour = new Date().getHours()
  if (hour < 6) {
    greeting.value = '凌晨好'
  } else if (hour < 9) {
    greeting.value = '早上好'
  } else if (hour < 12) {
    greeting.value = '上午好'
  } else if (hour < 14) {
    greeting.value = '中午好'
  } else if (hour < 17) {
    greeting.value = '下午好'
  } else if (hour < 19) {
    greeting.value = '傍晚好'
  } else {
    greeting.value = '晚上好'
  }
}

const updateTime = () => {
  const now = new Date()
  const options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' }
  currentTime.value = now.toLocaleDateString('zh-CN', options)
}

const fetchDomainCount = async () => {
  try {
    const domains = await getDomainList()
    domainCount.value = domains.length
  } catch (error) {
    console.error('获取域名数量失败:', error)
    domainCount.value = 0
  }
}

onMounted(() => {
  updateGreeting()
  updateTime()
  fetchDomainCount()
  
  // 每分钟更新一次时间和问候语
  setInterval(() => {
    updateGreeting()
    updateTime()
  }, 60000)
})
</script>

<template>
  <div class="home-page">
    <!-- 欢迎语区域 -->
    <el-card class="welcome-card">
      <div class="welcome-content">
        <h2>{{ greeting }}，管理员</h2>
        <p class="current-time">{{ currentTime }}</p>
        <p class="welcome-text">欢迎使用爱特工作室域名管理系统</p>
      </div>
    </el-card>

    <!-- 统计数据区域 -->
    <div class="stats-container">
      <el-card class="stats-card">
        <template #header>
          <div class="card-header">
            <el-icon><DataLine /></el-icon>
            <span>数据统计</span>
          </div>
        </template>
        <div class="stats-content">
          <div class="stat-item">
            <el-icon><Link /></el-icon>
            <div class="stat-info">
              <div class="stat-label">域名总数</div>
              <div class="stat-value">{{ domainCount }}</div>
            </div>
          </div>
        </div>
      </el-card>
    </div>
  </div>
</template>

<style scoped>
.home-page {
  padding: 20px;
}

.welcome-card {
  margin-bottom: 20px;
  background: linear-gradient(135deg, #1890ff 0%, #36cfc9 100%);
  color: white;
}

.welcome-content {
  padding: 10px;
}

.welcome-content h2 {
  margin: 0;
  font-size: 24px;
}

.current-time {
  margin: 10px 0;
  font-size: 14px;
  opacity: 0.8;
}

.welcome-text {
  margin: 5px 0;
  font-size: 16px;
}

.stats-container {
  display: flex;
  gap: 20px;
}

.stats-card {
  flex: 1;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
}

.stats-content {
  padding: 20px 0;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 16px;
}

.stat-info {
  display: flex;
  flex-direction: column;
}

.stat-label {
  font-size: 14px;
  color: #909399;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #303133;
  margin-top: 4px;
}

.el-icon {
  font-size: 24px;
  color: #409EFF;
}
</style>