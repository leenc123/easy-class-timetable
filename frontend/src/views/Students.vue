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
        <el-table-column label="学时" width="120">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="handleHours(row)">
              配置学时
            </el-button>
          </template>
        </el-table-column>
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

    <!-- 学时配置弹窗 -->
    <el-dialog v-model="hoursDialogVisible" title="学时配置" width="600px">
      <div class="hours-header">
        <span>学生：{{ currentStudent?.name }}</span>
        <el-button type="primary" size="small" @click="handleAddHours">添加学科</el-button>
      </div>
      <el-table :data="hoursList" v-loading="hoursLoading" stripe size="small">
        <el-table-column prop="subject" label="学科" width="120" />
        <el-table-column prop="total_hours" label="总学时(分钟)" width="120" />
        <el-table-column prop="remaining_hours" label="剩余学时(分钟)" width="120" />
        <el-table-column label="已用学时" width="100">
          <template #default="{ row }">
            {{ row.total_hours - row.remaining_hours }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="handleEditHours(row)">编辑</el-button>
            <el-button type="danger" link size="small" @click="handleDeleteHours(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      <template #footer>
        <el-button @click="hoursDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>

    <!-- 学时编辑弹窗 -->
    <el-dialog v-model="hoursEditDialogVisible" :title="isEditHours ? '编辑学时' : '添加学时'" width="400px">
      <el-form ref="hoursFormRef" :model="hoursForm" :rules="hoursRules" label-width="80px">
        <el-form-item label="学科" prop="subject">
          <el-select v-model="hoursForm.subject" placeholder="请选择学科" style="width: 100%" :disabled="isEditHours">
            <el-option label="语文" value="语文" />
            <el-option label="数学" value="数学" />
            <el-option label="英语" value="英语" />
            <el-option label="物理" value="物理" />
            <el-option label="化学" value="化学" />
            <el-option label="生物" value="生物" />
            <el-option label="历史" value="历史" />
            <el-option label="地理" value="地理" />
            <el-option label="政治" value="政治" />
            <el-option label="音乐" value="音乐" />
            <el-option label="美术" value="美术" />
            <el-option label="体育" value="体育" />
            <el-option label="信息" value="信息" />
          </el-select>
        </el-form-item>
        <el-form-item label="总学时" prop="total_hours">
          <el-input-number v-model="hoursForm.total_hours" :min="0" :step="60" placeholder="请输入总学时(分钟)" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="hoursEditDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="hoursSubmitLoading" @click="handleSubmitHours">确定</el-button>
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

// 学时相关
const hoursDialogVisible = ref(false)
const hoursEditDialogVisible = ref(false)
const hoursLoading = ref(false)
const hoursSubmitLoading = ref(false)
const hoursList = ref([])
const currentStudent = ref(null)
const isEditHours = ref(false)
const hoursFormRef = ref()

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

const hoursForm = reactive({
  id: null,
  student_id: null,
  subject: '',
  total_hours: 0
})

const rules = {
  name: [{ required: true, message: '请输入学生姓名', trigger: 'blur' }],
  org_id: [{ required: true, message: '请选择所属机构', trigger: 'change' }]
}

const hoursRules = {
  subject: [{ required: true, message: '请选择学科', trigger: 'change' }],
  total_hours: [{ required: true, message: '请输入总学时', trigger: 'blur' }]
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

const resetHoursForm = () => {
  hoursForm.id = null
  hoursForm.student_id = null
  hoursForm.subject = ''
  hoursForm.total_hours = 0
  hoursFormRef.value?.resetFields()
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

// 学时管理
const handleHours = async (row) => {
  currentStudent.value = row
  hoursDialogVisible.value = true
  await fetchHoursList(row.id)
}

const fetchHoursList = async (studentId) => {
  hoursLoading.value = true
  try {
    const res = await studentApi.getSubjectHours(studentId)
    hoursList.value = res.data || []
  } finally {
    hoursLoading.value = false
  }
}

const handleAddHours = () => {
  resetHoursForm()
  hoursForm.student_id = currentStudent.value.id
  isEditHours.value = false
  hoursEditDialogVisible.value = true
}

const handleEditHours = (row) => {
  resetHoursForm()
  isEditHours.value = true
  Object.assign(hoursForm, {
    id: row.id,
    student_id: currentStudent.value.id,
    subject: row.subject,
    total_hours: row.total_hours
  })
  hoursEditDialogVisible.value = true
}

const handleDeleteHours = async (row) => {
  await ElMessageBox.confirm('确定要删除该学科学时配置吗？', '提示', { type: 'warning' })
  await studentApi.deleteSubjectHours(currentStudent.value.id, row.id)
  ElMessage.success('删除成功')
  fetchHoursList(currentStudent.value.id)
}

const handleSubmitHours = async () => {
  await hoursFormRef.value.validate()
  hoursSubmitLoading.value = true
  try {
    if (isEditHours.value) {
      await studentApi.updateSubjectHours(currentStudent.value.id, hoursForm.id, {
        total_hours: hoursForm.total_hours
      })
    } else {
      await studentApi.createSubjectHours(currentStudent.value.id, {
        subject: hoursForm.subject,
        total_hours: hoursForm.total_hours
      })
    }
    ElMessage.success(isEditHours.value ? '更新成功' : '添加成功')
    hoursEditDialogVisible.value = false
    fetchHoursList(currentStudent.value.id)
  } finally {
    hoursSubmitLoading.value = false
  }
}

onMounted(() => {
  fetchData()
  fetchOrgList()
})
</script>

<style scoped>
.hours-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}
</style>