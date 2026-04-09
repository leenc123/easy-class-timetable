<template>
  <div class="page-container">
    <div class="page-header">
      <h3 class="page-title">课表管理</h3>
      <div>
        <el-button @click="handleExport('excel')">导出Excel</el-button>
        <el-button @click="handleExport('pdf')">导出PDF</el-button>
        <el-button type="primary" @click="handleAdd">新增课程</el-button>
      </div>
    </div>

    <!-- 筛选条件 -->
    <el-card style="margin-bottom: 20px">
      <el-form :inline="true" :model="filters" @submit.prevent="fetchData">
        <el-form-item label="日期范围">
          <el-date-picker
            v-model="dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            value-format="YYYY-MM-DD"
            @change="fetchData"
          />
        </el-form-item>
        <el-form-item label="教师">
          <el-select v-model="filters.teacher_id" placeholder="全部" clearable @change="fetchData">
            <el-option v-for="t in teacherOptions" :key="t.id" :label="t.name" :value="t.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="教室">
          <el-select v-model="filters.classroom_id" placeholder="全部" clearable @change="fetchData">
            <el-option v-for="c in classroomOptions" :key="c.id" :label="c.name" :value="c.id" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="fetchData">查询</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 课表日历视图 -->
    <el-card>
      <el-table :data="tableData" v-loading="loading" stripe>
        <el-table-column prop="session_date" label="日期" width="120" />
        <el-table-column label="时间" width="120">
          <template #default="{ row }">
            {{ row.start_time }} - {{ row.end_time }}
          </template>
        </el-table-column>
        <el-table-column prop="course_name" label="课程" />
        <el-table-column prop="teacher_name" label="教师" width="100" />
        <el-table-column prop="classroom_name" label="教室" width="120" />
        <el-table-column prop="student_count" label="学生数" width="80" />
        <el-table-column prop="status" label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">{{ getStatusText(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="handleEdit(row)">编辑</el-button>
            <el-button type="danger" link @click="handleDelete(row)">取消</el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.pageSize"
        :total="pagination.total"
        :page-sizes="[20, 50, 100]"
        layout="total, sizes, prev, pager, next"
        @change="fetchData"
        style="margin-top: 20px; justify-content: flex-end"
      />
    </el-card>

    <!-- 新增/编辑弹窗 -->
    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑课程' : '新增课程'" width="550px">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="80px">
        <el-form-item label="课程" prop="course_id">
          <el-select v-model="form.course_id" placeholder="请选择课程" style="width: 100%" filterable>
            <el-option v-for="c in courseOptions" :key="c.id" :label="c.name" :value="c.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="教师" prop="teacher_id">
          <el-select v-model="form.teacher_id" placeholder="请选择教师" style="width: 100%">
            <el-option v-for="t in teacherOptions" :key="t.id" :label="t.name" :value="t.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="教室" prop="classroom_id">
          <el-select v-model="form.classroom_id" placeholder="请选择教室" style="width: 100%">
            <el-option v-for="c in classroomOptions" :key="c.id" :label="c.name" :value="c.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="日期" prop="session_date">
          <el-date-picker v-model="form.session_date" type="date" placeholder="选择日期" value-format="YYYY-MM-DD" style="width: 100%" />
        </el-form-item>
        <el-form-item label="时间段" prop="time_slot_id">
          <el-select v-model="form.time_slot_id" placeholder="请选择时间段" style="width: 100%" @change="checkConflict">
            <el-option v-for="s in timeSlotOptions" :key="s.id" :label="`${s.name} (${s.start_time}-${s.end_time})`" :value="s.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="学生" prop="student_ids">
          <el-select v-model="form.student_ids" multiple placeholder="请选择学生" style="width: 100%" filterable>
            <el-option v-for="s in studentOptions" :key="s.id" :label="s.name" :value="s.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="备注" prop="notes">
          <el-input v-model="form.notes" type="textarea" rows="2" />
        </el-form-item>

        <!-- 冲突提示 -->
        <el-alert v-if="conflictInfo.has_conflict" type="error" :closable="false" style="margin-bottom: 16px">
          <template #title>存在冲突</template>
          <div v-for="c in conflictInfo.conflicts" :key="c.type">{{ c.description }}</div>
        </el-alert>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitLoading" @click="handleSubmit" :disabled="conflictInfo.has_conflict">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { scheduleApi, cycleApi, exportApi } from '@/api/schedule'
import { courseApi, teacherApi, studentApi, classroomApi } from '@/api/resource'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()
const loading = ref(false)
const submitLoading = ref(false)
const dialogVisible = ref(false)
const isEdit = ref(false)
const tableData = ref([])
const formRef = ref()

const dateRange = ref([])
const filters = reactive({
  teacher_id: null,
  classroom_id: null
})

const pagination = reactive({
  page: 1,
  pageSize: 20,
  total: 0
})

const form = reactive({
  id: null,
  course_id: null,
  teacher_id: null,
  classroom_id: null,
  session_date: '',
  time_slot_id: null,
  student_ids: [],
  notes: ''
})

const rules = {
  course_id: [{ required: true, message: '请选择课程', trigger: 'change' }],
  teacher_id: [{ required: true, message: '请选择教师', trigger: 'change' }],
  classroom_id: [{ required: true, message: '请选择教室', trigger: 'change' }],
  session_date: [{ required: true, message: '请选择日期', trigger: 'change' }],
  time_slot_id: [{ required: true, message: '请选择时间段', trigger: 'change' }]
}

const courseOptions = ref([])
const teacherOptions = ref([])
const classroomOptions = ref([])
const studentOptions = ref([])
const timeSlotOptions = ref([])

const conflictInfo = ref({ has_conflict: false, conflicts: [] })

const getStatusType = (status) => {
  const types = { scheduled: '', completed: 'success', cancelled: 'danger', rescheduled: 'warning' }
  return types[status] || ''
}

const getStatusText = (status) => {
  const texts = { scheduled: '已安排', completed: '已完成', cancelled: '已取消', rescheduled: '已调课' }
  return texts[status] || status
}

const fetchOptions = async () => {
  const [courses, teachers, classrooms, students, slots] = await Promise.all([
    courseApi.getList({ page: 1, page_size: 100 }),
    teacherApi.getList({ page: 1, page_size: 100 }),
    classroomApi.getList({ page: 1, page_size: 100 }),
    studentApi.getList({ page: 1, page_size: 100 }),
    cycleApi.getTimeSlots(userStore.user?.org_id)
  ])
  courseOptions.value = courses.data || []
  teacherOptions.value = teachers.data || []
  classroomOptions.value = classrooms.data || []
  studentOptions.value = students.data || []
  timeSlotOptions.value = slots.data || []
}

const fetchData = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.pageSize,
      ...filters
    }

    if (dateRange.value && dateRange.value.length === 2) {
      params.start_date = dateRange.value[0]
      params.end_date = dateRange.value[1]
    }

    const res = await scheduleApi.getList(params)
    tableData.value = res.data || []
    pagination.total = res.total || 0
  } finally {
    loading.value = false
  }
}

const checkConflict = async () => {
  if (!form.session_date || !form.time_slot_id || isEdit.value) return

  const res = await scheduleApi.checkConflict({
    teacher_id: form.teacher_id,
    classroom_id: form.classroom_id,
    session_date: form.session_date,
    time_slot_id: form.time_slot_id,
    exclude_session_id: form.id
  })
  conflictInfo.value = res
}

watch([() => form.teacher_id, () => form.classroom_id, () => form.session_date, () => form.time_slot_id], () => {
  if (form.session_date && form.time_slot_id) {
    checkConflict()
  }
})

const handleAdd = () => {
  form.id = null
  form.course_id = null
  form.teacher_id = null
  form.classroom_id = null
  form.session_date = ''
  form.time_slot_id = null
  form.student_ids = []
  form.notes = ''
  conflictInfo.value = { has_conflict: false, conflicts: [] }
  isEdit.value = false
  dialogVisible.value = true
}

const handleEdit = (row) => {
  form.id = row.id
  form.course_id = row.course_id
  form.teacher_id = row.teacher_id
  form.classroom_id = row.classroom_id
  form.session_date = row.session_date
  form.time_slot_id = row.time_slot_id
  form.student_ids = []
  form.notes = row.notes || ''
  conflictInfo.value = { has_conflict: false, conflicts: [] }
  isEdit.value = true
  dialogVisible.value = true
}

const handleDelete = async (row) => {
  await ElMessageBox.confirm('确定要取消该课程吗？', '提示', { type: 'warning' })
  await scheduleApi.delete(row.id)
  ElMessage.success('已取消')
  fetchData()
}

const handleSubmit = async () => {
  await formRef.value.validate()
  submitLoading.value = true
  try {
    if (isEdit.value) {
      await scheduleApi.update(form.id, form)
    } else {
      await scheduleApi.create(form)
    }
    ElMessage.success(isEdit.value ? '更新成功' : '创建成功')
    dialogVisible.value = false
    fetchData()
  } finally {
    submitLoading.value = false
  }
}

const handleExport = async (type) => {
  if (!dateRange.value || dateRange.value.length !== 2) {
    ElMessage.warning('请选择日期范围')
    return
  }

  const params = {
    start_date: dateRange.value[0],
    end_date: dateRange.value[1],
    ...filters
  }

  try {
    const res = type === 'pdf'
      ? await exportApi.exportPdf(params)
      : await exportApi.exportExcel(params)

    const blob = new Blob([res], {
      type: type === 'pdf' ? 'application/pdf' : 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `课表_${dateRange.value[0]}_${dateRange.value[1]}.${type === 'pdf' ? 'pdf' : 'xlsx'}`
    a.click()
    URL.revokeObjectURL(url)
  } catch (error) {
    ElMessage.error('导出失败')
  }
}

onMounted(() => {
  // 默认查询本周
  const today = new Date()
  const dayOfWeek = today.getDay() || 7
  const monday = new Date(today)
  monday.setDate(today.getDate() - dayOfWeek + 1)
  const sunday = new Date(monday)
  sunday.setDate(monday.getDate() + 6)

  dateRange.value = [
    monday.toISOString().split('T')[0],
    sunday.toISOString().split('T')[0]
  ]

  fetchOptions()
  fetchData()
})
</script>