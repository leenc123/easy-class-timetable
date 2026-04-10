<template>
  <div class="page-container">
    <div class="page-header">
      <h3 class="page-title">用户管理</h3>
      <el-button type="primary" @click="handleAdd">
        <el-icon><Plus /></el-icon>新增用户
      </el-button>
    </div>

    <!-- 筛选条件 -->
    <el-card style="margin-bottom: 20px">
      <el-form :inline="true" :model="filters" @submit.prevent="fetchData">
        <el-form-item label="角色">
          <el-select v-model="filters.role" placeholder="全部" clearable @change="fetchData">
            <el-option label="机构管理员" value="org_admin" />
            <el-option label="教师" value="teacher" />
            <el-option label="学生/家长" value="student_parent" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="filters.is_active" placeholder="全部" clearable @change="fetchData">
            <el-option label="启用" :value="true" />
            <el-option label="禁用" :value="false" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="fetchData">查询</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card>
      <el-table :data="tableData" v-loading="loading" stripe>
        <el-table-column prop="username" label="用户名" width="120" />
        <el-table-column prop="real_name" label="姓名" width="100" />
        <el-table-column prop="role" label="角色" width="120">
          <template #default="{ row }">
            <el-tag :type="getRoleType(row.role)">{{ getRoleText(row.role) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="org_name" label="所属机构" />
        <el-table-column prop="is_active" label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'danger'">
              {{ row.is_active ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <template v-if="row.role !== 'super_admin'">
              <el-button type="primary" link @click="handleEdit(row)">编辑</el-button>
              <el-button
                v-if="row.is_active"
                type="danger"
                link
                @click="handleToggleStatus(row)"
              >
                禁用
              </el-button>
              <el-button
                v-else
                type="success"
                link
                @click="handleToggleStatus(row)"
              >
                启用
              </el-button>
            </template>
            <span v-else class="text-gray-400">-</span>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.pageSize"
        :total="pagination.total"
        :page-sizes="[10, 20, 50]"
        layout="total, sizes, prev, pager, next"
        @change="fetchData"
        style="margin-top: 20px; justify-content: flex-end"
      />
    </el-card>

    <!-- 编辑弹窗 -->
    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑用户' : '新增用户'" width="500px">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="80px">
        <el-form-item label="用户名" prop="username" v-if="!isEdit">
          <el-input v-model="form.username" placeholder="请输入用户名" />
        </el-form-item>
        <el-form-item label="密码" prop="password" v-if="!isEdit">
          <el-input v-model="form.password" type="password" placeholder="请输入密码" show-password />
        </el-form-item>
        <el-form-item label="姓名" prop="real_name">
          <el-input v-model="form.real_name" placeholder="请输入姓名" />
        </el-form-item>
        <el-form-item label="角色" prop="role">
          <el-select v-model="form.role" placeholder="请选择角色" style="width: 100%">
            <el-option label="机构管理员" value="org_admin" />
            <el-option label="教师" value="teacher" />
            <el-option label="学生/家长" value="student_parent" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitLoading" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { authApi } from '@/api/auth'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()
const loading = ref(false)
const submitLoading = ref(false)
const dialogVisible = ref(false)
const isEdit = ref(false)
const tableData = ref([])
const formRef = ref()

const filters = reactive({
  role: null,
  is_active: null
})

const pagination = reactive({
  page: 1,
  pageSize: 20,
  total: 0
})

const form = reactive({
  id: null,
  username: '',
  password: '',
  real_name: '',
  role: 'teacher',
  org_id: null
})

const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
  real_name: [{ required: true, message: '请输入姓名', trigger: 'blur' }],
  role: [{ required: true, message: '请选择角色', trigger: 'change' }]
}

const getRoleType = (role) => {
  const types = { super_admin: 'danger', org_admin: 'warning', teacher: '', student_parent: 'info' }
  return types[role] || ''
}

const getRoleText = (role) => {
  const texts = { super_admin: '超级管理员', org_admin: '机构管理员', teacher: '教师', student_parent: '学生/家长' }
  return texts[role] || role
}

const fetchData = async () => {
  loading.value = true
  try {
    const res = await authApi.getList({
      page: pagination.page,
      page_size: pagination.pageSize,
      ...filters
    })
    tableData.value = res.data || []
    pagination.total = res.total || 0
  } finally {
    loading.value = false
  }
}

const handleAdd = () => {
  form.id = null
  form.username = ''
  form.password = ''
  form.real_name = ''
  form.role = 'teacher'
  form.org_id = userStore.user?.org_id
  isEdit.value = false
  dialogVisible.value = true
}

const handleEdit = (row) => {
  form.id = row.id
  form.real_name = row.real_name
  form.role = row.role
  isEdit.value = true
  dialogVisible.value = true
}

const handleToggleStatus = async (row) => {
  const action = row.is_active ? '禁用' : '启用'

  if (row.role === 'super_admin' && row.is_active) {
    ElMessage.warning('不能禁用超级管理员')
    return
  }

  await ElMessageBox.confirm(`确定要${action}该用户吗？`, '提示', { type: 'warning' })

  await authApi.updateUser(row.id, { is_active: !row.is_active })
  ElMessage.success(`已${action}`)
  fetchData()
}

const handleSubmit = async () => {
  await formRef.value.validate()
  submitLoading.value = true
  try {
    if (isEdit.value) {
      await authApi.updateUser(form.id, {
        real_name: form.real_name,
        role: form.role
      })
    } else {
      await authApi.createUser(form)
    }
    ElMessage.success(isEdit.value ? '更新成功' : '创建成功')
    dialogVisible.value = false
    fetchData()
  } finally {
    submitLoading.value = false
  }
}

onMounted(() => {
  fetchData()
})
</script>