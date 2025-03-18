<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getGlobalConfig, updateGlobalConfig } from '../../api/config'

const formData = reactive({
  cloudFlareTunnelId: '',
  cloudFlareToken: '',
  configYmlPath: '',
  tencentSecretKey: '',
  tencentSecretId: ''
})

const rules = {
  cloudFlareTunnelId: [
    { required: true, message: '请输入Cloud Flare Tunnel ID', trigger: 'blur' }
  ],
  cloudFlareToken: [
    { required: true, message: '请输入Cloud Flare Token', trigger: 'blur' }
  ],
  configYmlPath: [
    { required: true, message: '请输入config.yml路径', trigger: 'blur' }
  ],
  tencentSecretKey: [
    { required: true, message: '请输入腾讯云SecretKey', trigger: 'blur' }
  ],
  tencentSecretId: [
    { required: true, message: '请输入腾讯云SecretID', trigger: 'blur' }
  ]
}

const formRef = ref(null)

const handleSubmit = async () => {
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
    const apiData = {
      cloudflare_tunnel_id: formData.cloudFlareTunnelId,
      cloudflare_token: formData.cloudFlareToken,
      config_yml_path: formData.configYmlPath,
      tencent_secret_key: formData.tencentSecretKey,
      tencent_secret_id: formData.tencentSecretId
    }
    await updateGlobalConfig(apiData)
    ElMessage.success('配置保存成功')
  } catch (error) {
    if (error.response && error.response.data) {
      const errorData = error.response.data
      const errorMessages = []
      
      // 处理每个字段的错误信息
      Object.entries(errorData).forEach(([field, messages]) => {
        if (Array.isArray(messages) && messages.length > 0) {
          const fieldMap = {
            cloudflare_tunnel_id: 'Cloud Flare Tunnel ID',
            cloudflare_token: 'Cloud Flare Token',
            config_yml_path: 'config.yml路径',
            tencent_secret_key: '腾讯云SecretKey',
            tencent_secret_id: '腾讯云SecretID'
          }
          errorMessages.push(`${fieldMap[field] || field}：${messages[0]}`)
        }
      })
      
      if (errorMessages.length > 0) {
        ElMessage.error(errorMessages.join('\n'))
      } else {
        ElMessage.error('保存配置失败')
      }
    } else {
      ElMessage.error(error.message || '保存配置失败')
    }
  }
}

onMounted(async () => {
  try {
    const config = await getGlobalConfig()
    // 映射API返回的数据到表单字段
    formData.cloudFlareTunnelId = config.cloudflare_tunnel_id
    formData.cloudFlareToken = config.cloudflare_token
    formData.configYmlPath = config.config_yml_path
    formData.tencentSecretKey = config.tencent_secret_key
    formData.tencentSecretId = config.tencent_secret_id
  } catch (error) {
    ElMessage.error('获取配置失败')
  }
})
</script>

<template>
  <div class="global-config-container">
    <el-card class="config-card">
      <template #header>
        <div class="card-header">
          <h2>全局配置</h2>
        </div>
      </template>
      
      <el-form
        ref="formRef"
        :model="formData"
        :rules="rules"
        label-width="180px"
        label-position="left"
        class="config-form"
      >
        <el-form-item label="Cloud Flare Tunnel ID" prop="cloudFlareTunnelId">
          <el-input
            v-model="formData.cloudFlareTunnelId"
            placeholder="请输入Cloud Flare Tunnel ID"
          />
        </el-form-item>

        <el-form-item label="Cloud Flare Token" prop="cloudFlareToken">
          <el-input
            v-model="formData.cloudFlareToken"
            type="password"
            placeholder="请输入Cloud Flare Token"
            show-password
          />
        </el-form-item>

        <el-form-item label="config.yml路径" prop="configYmlPath">
          <el-input
            v-model="formData.configYmlPath"
            placeholder="请输入config.yml的完整路径"
          />
        </el-form-item>

        <el-form-item label="腾讯云SecretKey" prop="tencentSecretKey">
          <el-input
            v-model="formData.tencentSecretKey"
            type="password"
            placeholder="请输入腾讯云SecretKey"
            show-password
          />
        </el-form-item>

        <el-form-item label="腾讯云SecretID" prop="tencentSecretId">
          <el-input
            v-model="formData.tencentSecretId"
            type="password"
            placeholder="请输入腾讯云SecretID"
            show-password
          />
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="handleSubmit">保存配置</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<style scoped>
.global-config-container {
  padding: 20px;
  height: calc(95% - 40px);
  width: calc(95% - 40px);
}

.config-card {
  height: 100%;
  width: 100%;
  margin: 0;
}

.card-header {
  display: flex;
  justify-content: flex-start;
  align-items: center;
}

.config-form {
  margin-top: 20px;
  max-width: 600px;
}

.el-form-item__label {
  justify-content: flex-start !important;
}
</style>