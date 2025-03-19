<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getDomainList, addDomain, updateDomain, deleteDomain } from '../../api/domain'

// 表格数据
const tableData = ref([])

// 对话框相关
const dialogVisible = ref(false)
const dialogTitle = ref('添加域名')
const isEdit = ref(false)
const editIndex = ref(-1)

// 表单数据
const formData = reactive({
  domain: '',
  proxy_pass: '',
  host: '',
  note: ''
})

// 表单验证规则
const rules = {
  domain: [
    { required: true, message: '请输入域名', trigger: 'blur' },
    { pattern: /^[a-zA-Z0-9][-a-zA-Z0-9]{0,62}(\.[a-zA-Z0-9][-a-zA-Z0-9]{0,62})+$/, message: '请输入有效的域名', trigger: 'blur' }
  ],
  proxy_pass: [
    { required: true, message: '请输入反代地址', trigger: 'blur' }
  ],
  host: [],
  note: []
}

const formRef = ref(null)

// 获取域名列表
const fetchDomainList = async () => {
  try {
    const data = await getDomainList()
    tableData.value = data
  } catch (error) {
    ElMessage.error('获取域名列表失败')
  }
}

onMounted(() => {
  fetchDomainList()
})

// 打开添加对话框
const handleAdd = () => {
  dialogTitle.value = '添加域名'
  isEdit.value = false
  resetForm()
  dialogVisible.value = true
}

// 打开编辑对话框
const handleEdit = (row, index) => {
  dialogTitle.value = '编辑域名'
  isEdit.value = true
  editIndex.value = index
  Object.assign(formData, row)
  dialogVisible.value = true
}

// 删除确认
const handleDelete = (row, index) => {
  ElMessageBox.confirm('确认删除该域名配置吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      await deleteDomain(row.id)
      tableData.value.splice(index, 1)
      ElMessage.success('删除成功')
    } catch (error) {
      ElMessage.error(error.response?.data?.message || '删除失败')
    }
  }).catch(() => {})
}

// 提交表单
const handleSubmit = async () => {
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
    if (isEdit.value) {
      // 编辑模式
      const updatedData = await updateDomain(tableData.value[editIndex.value].id, formData)
      Object.assign(tableData.value[editIndex.value], updatedData)
      ElMessage.success('修改成功')
    } else {
      // 添加模式
      const newDomain = await addDomain(formData)
      tableData.value.push(newDomain)
      ElMessage.success('添加成功')
    }
    dialogVisible.value = false
  } catch (error) {
    ElMessage.error(error.response?.data?.message || '操作失败')
  }
}

// 重置表单
const resetForm = () => {
  if (formRef.value) {
    formRef.value.resetFields()
  }
  Object.assign(formData, {
    domain: '',
    proxy_pass: '',
    host: '',
    note: ''
  })
}
</script>

<template>
  <div class="domain-add-container">
    <el-card class="domain-card">
      <template #header>
        <div class="card-header">
          <h2>域名管理</h2>
          <el-button type="primary" @click="handleAdd">添加域名</el-button>
        </div>
      </template>

      <el-table :data="tableData" border style="width: 100%">
        <el-table-column prop="domain" label="域名" min-width="200" />
        <el-table-column prop="proxy_pass" label="反代地址" min-width="150" />
        <el-table-column prop="host" label="Host" min-width="200" />
        <el-table-column prop="note" label="备注" min-width="200" />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row, $index }">
            <el-button type="primary" link @click="handleEdit(row, $index)">编辑</el-button>
            <el-button type="danger" link @click="handleDelete(row, $index)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 添加/编辑对话框 -->
      <el-dialog
        v-model="dialogVisible"
        :title="dialogTitle"
        width="500px"
        @close="resetForm"
      >
        <el-form
          ref="formRef"
          :model="formData"
          :rules="rules"
          label-width="100px"
          label-position="right"
        >
          <el-form-item label="域名" prop="domain">
            <el-input v-model="formData.domain" placeholder="请输入域名" />
          </el-form-item>
          <el-form-item label="反代地址" prop="proxy_pass">
            <el-input v-model="formData.proxy_pass" placeholder="请输入反代地址" />
          </el-form-item>
          <el-form-item label="Host" prop="host">
            <el-input v-model="formData.host" placeholder="请输入Host" />
          </el-form-item>
          <el-form-item label="备注" prop="note">
            <el-input v-model="formData.note" placeholder="请输入备注" />
          </el-form-item>
        </el-form>
        <template #footer>
          <span class="dialog-footer">
            <el-button @click="dialogVisible = false">取消</el-button>
            <el-button type="primary" @click="handleSubmit">确定</el-button>
          </span>
        </template>
      </el-dialog>
    </el-card>
  </div>
</template>

<style scoped>
.domain-add-container {
  padding: 20px;
  height: calc(95% - 40px);
  width: calc(95% - 40px);
}

.domain-card {
  height: 100%;
  width: 100%;
  margin: 0;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}
</style>