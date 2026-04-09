<template>
  <div class="page-container">
    <div class="page-header">
      <h3 class="page-title">教师管理</h3>
      <el-button type="primary" @click="handleAdd">
        <el-icon><Plus /></el-icon>新增教师
      </el-button>
    </div>

    <el-card>
      <el-table :data="tableData" v-loading="loading" stripe>
        <el-table-column prop="name" label="姓名" width="100" />
        <el-table-column prop="phone" label="电话" width="130" />
        <el-table-column prop="email" label="邮箱" />
        <el-table-column label="可教授科目" min-width="150">
          <template #default="{ row }">
            <el-tag v-for="item in row.subjects" :key="item" size="small" style="margin-right: 4px">
              {{ item }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="max_hours_per_week" label="周课时上限" width="100" />
        <el-table-column prop="is_active" label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'danger'">
              {{ row.is_active ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="handleEdit(row)">编辑</el-button>
            <el-button type="warning" link @click="handleAvailability(row)">时间设置</el-button>
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
    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑教师' : '新增教师'" width="500px">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-form-item label="姓名" prop="name">
          <el-input v-model="form.name" placeholder="请输入教师姓名" />
        </el-form-item>
        <el-form-item label="电话" prop="phone">
          <el-input v-model="form.phone" placeholder="请输入联系电话" />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="form.email" placeholder="请输入邮箱" />
        </el-form-item>
        <el-form-item label="可教授科目" prop="subjects">
          <el-select v-model="form.subjects" multiple placeholder="请选择科目" style="width: 100%">
            <el-option label="语文" value="语文" />
            <el-option label="数学" value="数学" />
            <el-option label="英语" value="英语" />
            <el-option label="物理" value="物理" />
            <el-option label="化学" value="化学" />
            <el-option label="生物" value="生物" />
          </el-select>
        </el-form-item>
        <el-form-item label="周课时上限" prop="max_hours_per_week">
          <el-input-number v-model="form.max_hours_per_week" :min="1" :max="60" />
        </el-form-item>
        <el-form-item label="简介" prop="bio">
          <el-input v-model="form.bio" type="textarea" rows="3" placeholder="请输入简介" />
        </el-form-item>
        <el-form-item label="创建账号" prop="create_user_account" v-if="!isEdit">
          <el-switch v-model="form.create_user_account" />
          <span style="margin-left: 10px; color: #909399; font-size: 12px">同时创建登录账号</span>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitLoading" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>

    <!-- 可用时间设置弹窗 -->
    <el-dialog v-model="availabilityVisible" title="设置可用时间" width="600px">
      <el-table :data="availabilityList" size="small">
        <el-table-column prop="day_of_week" label="星期" width="100">
          <template #default="{ row }">
            {{ weekDays[row.day_of_week] }}
          </template>
        </el-table-column>
        <el-table-column prop="start_time" label="开始时间" width="120" />
        <el-table-column prop="end_time" label="结束时间" width="120" />
        <el-table-column label="操作" width="100">
          <template #default="{ $index }">
            <el-button type="danger" link @click="availabilityList.splice($index, 1)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      <div style="margin-top: 16px">
        <el-select v-model="newAvailability.day_of_week" placeholder="选择星期" style="width: 100px">
          <el-option v-for="(day, idx) in weekDays" :key="idx" :label="day" :value="idx" />
        </el-select>
        <el-time-select v-model="newAvailability.start_time" placeholder="开始时间" style="width: 120px" />
        <el-time-select v-model="newAvailability.end_time" placeholder="结束时间" style="width: 120px" />
        <el-button type="primary" @click="addAvailability">添加</el-button>
      </div>
      <template #footer>
        <el-button @click="availabilityVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitLoading" @click="saveAvailability">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { teacherApi } from '@/api/resource'

const loading = ref(false)
const submitLoading = ref(false)
const dialogVisible = ref(false)
const availabilityVisible = ref(false)
const isEdit = ref(false)
const tableData = ref([])
const formRef = ref()
const currentTeacherId = ref(null)

const weekDays = ['周日', '周一', '周二', '周三', '周四', '周五', '周六']

const pagination = reactive({
  page: 1,
  pageSize: 20,
  total: 0
})

const form = reactive({
  id: null,
  name: '',
  phone: '',
  email: '',
  subjects: [],
  max_hours_per_week: 20,
  bio: '',
  create_user_account: false
})

const availabilityList = ref([])
const newAvailability = reactive({
  day_of_week: 1,
  start_time: '08:00',
  end_time: '18:00'
})

const rules = {
  name: [{ required: true, message: '请输入教师姓名', trigger: 'blur' }]
}

const resetForm = () => {
  form.id = null
  form.name = ''
  form.phone = ''
  form.email = ''
  form.subjects = []
  form.max_hours_per_week = 20
  form.bio = ''
  form.create_user_account = false
  formRef.value?.resetFields()
}

const fetchData = async () => {
  loading.value = true
  try {
    const res = await teacherApi.getList({
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

const handleAvailability = async (row) => {
  currentTeacherId.value = row.id
  const res = await teacherApi.getAvailability(row.id)
  availabilityList.value = res.data || []
  availabilityVisible.value = true
}

const addAvailability = () => {
  availabilityList.value.push({ ...newAvailability })
}

const saveAvailability = async () => {
  submitLoading.value = true
  try {
    await teacherApi.setAvailability(currentTeacherId.value, availabilityList.value)
    ElMessage.success('保存成功')
    availabilityVisible.value = false
  } finally {
    submitLoading.value = false
  }
}

const handleDelete = async (row) => {
  await ElMessageBox.confirm('确定要删除该教师吗？', '提示', { type: 'warning' })
  await teacherApi.delete(row.id)
  ElMessage.success('删除成功')
  fetchData()
}

const handleSubmit = async () => {
  await formRef.value.validate()
  submitLoading.value = true
  try {
    if (isEdit.value) {
      await teacherApi.update(form.id, form)
    } else {
      await teacherApi.create(form)
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