<template>
  <div class="page-container">
    <div class="page-header">
      <h3 class="page-title">学生管理</h3>
      <el-button type="primary" @click="handleAdd">
        <el-icon><Plus /></el-icon>新增学生
      </el-button>
    </div>

    <el-card>
      <el-table :data="tableData" v-loading="loading" stripe>
        <el-table-column prop="name" label="姓名" width="100" />
        <el-table-column prop="grade" label="年级" width="80" />
        <el-table-column prop="phone" label="电话" width="130" />
        <el-table-column prop="parent_name" label="家长姓名" width="100" />
        <el-table-column prop="parent_phone" label="家长电话" width="130" />
        <el-table-column prop="notes" label="备注" />
        <el-table-column prop="is_active" label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'danger'">
              {{ row.is_active ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="handleEdit(row)">编辑</el-button>
            <el-button type="danger" link @click="handleDelete(row)">删除</el-button>
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
    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑学生' : '新增学生'" width="500px">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="80px">
        <!-- 超管创建时显示机构选择 -->
        <el-form-item v-if="isSuperAdmin && !isEdit" label="所属机构" prop="org_id">
          <el-select v-model="form.org_id" placeholder="请选择机构" style="width: 100%" :loading="orgLoading">
            <el-option
              v-for="org in orgList"
              :key="org.id"
              :label="org.name"
              :value="org.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="姓名" prop="name">
          <el-input v-model="form.name" placeholder="请输入学生姓名" />
        </el-form-item>
        <el-form-item label="年级" prop="grade">
          <el-select v-model="form.grade" placeholder="请选择年级" style="width: 100%">
            <el-option label="一年级" value="一年级" />
            <el-option label="二年级" value="二年级" />
            <el-option label="三年级" value="三年级" />
            <el-option label="四年级" value="四年级" />
            <el-option label="五年级" value="五年级" />
            <el-option label="六年级" value="六年级" />
            <el-option label="初一" value="初一" />
            <el-option label="初二" value="初二" />
            <el-option label="初三" value="初三" />
            <el-option label="高一" value="高一" />
            <el-option label="高二" value="高二" />
            <el-option label="高三" value="高三" />
          </el-select>
        </el-form-item>
        <el-form-item label="电话" prop="phone">
          <el-input v-model="form.phone" placeholder="请输入联系电话" />
        </el-form-item>
        <el-form-item label="家长姓名" prop="parent_name">
          <el-input v-model="form.parent_name" placeholder="请输入家长姓名" />
        </el-form-item>
        <el-form-item label="家长电话" prop="parent_phone">
          <el-input v-model="form.parent_phone" placeholder="请输入家长电话" />
        </el-form-item>
        <el-form-item label="备注" prop="notes">
          <el-input v-model="form.notes" type="textarea" rows="2" placeholder="请输入备注" />
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
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { studentApi } from '@/api/resource'
import { organizationApi } from '@/api/organization'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()
const isSuperAdmin = computed(() => userStore.user?.role === 'super_admin')

const loading = ref(false)
const submitLoading = ref(false)
const dialogVisible = ref(false)
const isEdit = ref(false)
const tableData = ref([])
const formRef = ref()

// 机构相关
const orgList = ref([])
const orgLoading = ref(false)

const pagination = reactive({
  page: 1,
  pageSize: 20,
  total: 0
})

const form = reactive({
  id: null,
  org_id: null,
  name: '',
  grade: '',
  phone: '',
  parent_name: '',
  parent_phone: '',
  notes: ''
})

const rules = {
  name: [{ required: true, message: '请输入学生姓名', trigger: 'blur' }],
  org_id: [{ required: true, message: '请选择所属机构', trigger: 'change' }]
}

const resetForm = () => {
  form.id = null
  form.org_id = null
  form.name = ''
  form.grade = ''
  form.phone = ''
  form.parent_name = ''
  form.parent_phone = ''
  form.notes = ''
  formRef.value?.resetFields()
}

// 获取机构列表（超管使用）
const fetchOrgList = async () => {
  if (!isSuperAdmin.value) return
  orgLoading.value = true
  try {
    const res = await organizationApi.getList({ page: 1, page_size: 100 })
    orgList.value = res.data || []
  } finally {
    orgLoading.value = false
  }
}

const fetchData = async () => {
  loading.value = true
  try {
    const res = await studentApi.getList({
      page: pagination.page,
      page_size: pagination.pageSize
    })
    tableData.value = res.data || []
    pagination.total = res.total || 0
  } finally {
    loading.value = false
  }
}

const handleAdd = () => {
  resetForm()
  isEdit.value = false
  dialogVisible.value = true
}

const handleEdit = (row) => {
  resetForm()
  isEdit.value = true
  Object.assign(form, row)
  dialogVisible.value = true
}

const handleDelete = async (row) => {
  await ElMessageBox.confirm('确定要删除该学生吗？', '提示', { type: 'warning' })
  await studentApi.delete(row.id)
  ElMessage.success('删除成功')
  fetchData()
}

const handleSubmit = async () => {
  await formRef.value.validate()
  submitLoading.value = true
  try {
    const submitData = { ...form }
    // 非超管不传org_id，由后端自动填充
    if (!isSuperAdmin.value) {
      delete submitData.org_id
    }

    if (isEdit.value) {
      await studentApi.update(form.id, submitData)
    } else {
      await studentApi.create(submitData)
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
  fetchOrgList()
})
</script>