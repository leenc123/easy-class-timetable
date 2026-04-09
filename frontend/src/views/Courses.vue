<template>
  <div class="page-container">
    <div class="page-header">
      <h3 class="page-title">课程管理</h3>
      <el-button type="primary" @click="handleAdd">
        <el-icon><Plus /></el-icon>新增课程
      </el-button>
    </div>

    <el-card>
      <el-table :data="tableData" v-loading="loading" stripe>
        <el-table-column prop="name" label="课程名称" />
        <el-table-column prop="code" label="编码" width="100" />
        <el-table-column prop="subject" label="科目" width="80" />
        <el-table-column prop="duration_minutes" label="时长(分钟)" width="100" />
        <el-table-column label="学生数" width="80">
          <template #default="{ row }">
            {{ row.students?.length || 0 }}
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="row.status === 'active' ? 'success' : 'info'">
              {{ row.status === 'active' ? '进行中' : '已结束' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="250" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="handleEdit(row)">编辑</el-button>
            <el-button type="warning" link @click="handleAssignTeachers(row)">分配教师</el-button>
            <el-button type="info" link @click="handleAssignStudents(row)">选课学生</el-button>
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
    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑课程' : '新增课程'" width="500px">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
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
        <el-form-item label="课程名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入课程名称" />
        </el-form-item>
        <el-form-item label="编码" prop="code">
          <el-input v-model="form.code" placeholder="请输入课程编码" />
        </el-form-item>
        <el-form-item label="科目" prop="subject">
          <el-select v-model="form.subject" placeholder="请选择科目" style="width: 100%">
            <el-option label="语文" value="语文" />
            <el-option label="数学" value="数学" />
            <el-option label="英语" value="英语" />
            <el-option label="物理" value="物理" />
            <el-option label="化学" value="化学" />
            <el-option label="生物" value="生物" />
          </el-select>
        </el-form-item>
        <el-form-item label="单次时长" prop="duration_minutes">
          <el-input-number v-model="form.duration_minutes" :min="15" :max="240" :step="15" />
          <span style="margin-left: 10px">分钟</span>
        </el-form-item>
        <el-form-item label="最少学生" prop="min_students">
          <el-input-number v-model="form.min_students" :min="1" :max="100" />
        </el-form-item>
        <el-form-item label="最多学生" prop="max_students">
          <el-input-number v-model="form.max_students" :min="1" :max="100" />
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input v-model="form.description" type="textarea" rows="2" placeholder="请输入描述" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitLoading" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>

    <!-- 分配教师弹窗 -->
    <el-dialog v-model="teacherDialogVisible" title="分配教师" width="400px">
      <el-select v-model="selectedTeachers" multiple placeholder="请选择教师" style="width: 100%">
        <el-option
          v-for="t in teacherOptions"
          :key="t.id"
          :label="t.name"
          :value="t.id"
        />
      </el-select>
      <template #footer>
        <el-button @click="teacherDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitLoading" @click="saveTeachers">保存</el-button>
      </template>
    </el-dialog>

    <!-- 选课学生弹窗 -->
    <el-dialog v-model="studentDialogVisible" title="选课学生" width="400px">
      <el-select v-model="selectedStudents" multiple placeholder="请选择学生" style="width: 100%" filterable>
        <el-option
          v-for="s in studentOptions"
          :key="s.id"
          :label="`${s.name} (${s.grade})`"
          :value="s.id"
        />
      </el-select>
      <template #footer>
        <el-button @click="studentDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitLoading" @click="saveStudents">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { courseApi, teacherApi, studentApi } from '@/api/resource'
import { organizationApi } from '@/api/organization'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()
const isSuperAdmin = computed(() => userStore.user?.role === 'super_admin')

const loading = ref(false)
const submitLoading = ref(false)
const dialogVisible = ref(false)
const teacherDialogVisible = ref(false)
const studentDialogVisible = ref(false)
const isEdit = ref(false)
const tableData = ref([])
const formRef = ref()
const currentCourseId = ref(null)
const teacherOptions = ref([])
const studentOptions = ref([])
const selectedTeachers = ref([])
const selectedStudents = ref([])

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
  code: '',
  subject: '',
  duration_minutes: 60,
  min_students: 1,
  max_students: 30,
  description: ''
})

const rules = {
  name: [{ required: true, message: '请输入课程名称', trigger: 'blur' }],
  subject: [{ required: true, message: '请选择科目', trigger: 'change' }],
  org_id: [{ required: true, message: '请选择所属机构', trigger: 'change' }]
}

const resetForm = () => {
  form.id = null
  form.org_id = null
  form.name = ''
  form.code = ''
  form.subject = ''
  form.duration_minutes = 60
  form.min_students = 1
  form.max_students = 30
  form.description = ''
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
    const res = await courseApi.getList({
      page: pagination.page,
      page_size: pagination.pageSize
    })
    tableData.value = res.data || []
    pagination.total = res.total || 0
  } finally {
    loading.value = false
  }
}

const fetchOptions = async () => {
  const [teachers, students] = await Promise.all([
    teacherApi.getList({ page_size: 1000 }),
    studentApi.getList({ page_size: 1000 })
  ])
  teacherOptions.value = teachers.data || []
  studentOptions.value = students.data || []
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

const handleAssignTeachers = async (row) => {
  currentCourseId.value = row.id
  selectedTeachers.value = row.teachers || []
  await fetchOptions()
  teacherDialogVisible.value = true
}

const handleAssignStudents = async (row) => {
  currentCourseId.value = row.id
  selectedStudents.value = row.students || []
  await fetchOptions()
  studentDialogVisible.value = true
}

const saveTeachers = async () => {
  submitLoading.value = true
  try {
    await courseApi.assignTeachers(currentCourseId.value, {
      teacher_ids: selectedTeachers.value
    })
    ElMessage.success('保存成功')
    teacherDialogVisible.value = false
    fetchData()
  } finally {
    submitLoading.value = false
  }
}

const saveStudents = async () => {
  submitLoading.value = true
  try {
    await courseApi.assignStudents(currentCourseId.value, {
      student_ids: selectedStudents.value
    })
    ElMessage.success('保存成功')
    studentDialogVisible.value = false
    fetchData()
  } finally {
    submitLoading.value = false
  }
}

const handleSubmit = async () => {
  await formRef.value.validate()
  submitLoading.value = true
  try {
    const submitData = { ...form }
    if (!isSuperAdmin.value) {
      delete submitData.org_id
    }

    if (isEdit.value) {
      await courseApi.update(form.id, submitData)
    } else {
      await courseApi.create(submitData)
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