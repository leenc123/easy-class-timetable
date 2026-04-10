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

    <!-- 课表视图 -->
    <el-card v-loading="loading">
      <div v-if="groupedSessions.length === 0" class="empty-container">
        <el-empty description="暂无课程安排" />
      </div>

      <div v-else class="schedule-groups">
        <div
          v-for="group in groupedSessions"
          :key="group.date"
          class="schedule-group"
        >
          <div class="group-header" @click="toggleGroup(group.date)">
            <div class="header-left">
              <el-icon class="toggle-icon" :class="{ expanded: expandedDates.has(group.date) }">
                <ArrowRight />
              </el-icon>
              <span class="date-text">{{ formatDate(group.date) }}</span>
              <span class="date-weekday">{{ getWeekday(group.date) }}</span>
            </div>
            <div class="header-right">
              <el-tag type="info" size="small">{{ group.sessions.length }} 节课</el-tag>
            </div>
          </div>

          <div v-show="expandedDates.has(group.date)" class="group-content">
            <div class="schedule-table-wrapper">
              <table class="schedule-table">
                <thead>
                  <tr>
                    <th class="header-cell header-teacher">教师</th>
                    <th
                      v-for="slot in group.timeSlots"
                      :key="slot.id"
                      class="header-cell header-time"
                    >
                      <div class="time-name">{{ slot.name }}</div>
                      <div class="time-range">{{ slot.start_time }}-{{ slot.end_time }}</div>
                    </th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="teacher in group.teachers" :key="teacher.id">
                    <td class="cell-teacher">{{ teacher.name }}</td>
                    <td
                      v-for="slot in group.timeSlots"
                      :key="slot.id"
                      class="cell-content"
                      :class="getCellClass(teacher.id, slot.id, group.sessionMap)"
                    >
                      <div
                        v-if="getSession(teacher.id, slot.id, group.sessionMap)"
                        class="session-card"
                        :class="`session-${getSession(teacher.id, slot.id, group.sessionMap).status}`"
                        @click="handleEdit(getSession(teacher.id, slot.id, group.sessionMap))"
                      >
                        <div class="course-name">{{ getSession(teacher.id, slot.id, group.sessionMap).course_name }}</div>
                        <div class="classroom-name">{{ getSession(teacher.id, slot.id, group.sessionMap).classroom_name }}</div>
                        <div class="student-count">{{ getSession(teacher.id, slot.id, group.sessionMap).student_count || 0 }}人</div>
                      </div>
                      <div
                        v-else
                        class="empty-cell"
                        @click="handleAddWithParams(teacher.id, slot.id, group.date)"
                      >
                        <el-icon><Plus /></el-icon>
                      </div>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
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

    <!-- 导出机构选择弹窗 -->
    <el-dialog v-model="exportDialogVisible" title="选择导出机构" width="400px">
      <el-form label-width="80px">
        <el-form-item label="所属机构" required>
          <el-select v-model="exportOrgId" placeholder="请选择机构" style="width: 100%" :loading="orgLoading">
            <el-option v-for="org in orgOptions" :key="org.id" :label="org.name" :value="org.id" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="exportDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmExport">确定导出</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, watch, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ArrowRight, Plus } from '@element-plus/icons-vue'
import { scheduleApi, cycleApi, exportApi } from '@/api/schedule'
import { courseApi, teacherApi, studentApi, classroomApi } from '@/api/resource'
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

// 展开的日期
const expandedDates = ref(new Set())

// 导出机构选择
const exportDialogVisible = ref(false)
const exportType = ref('')
const exportOrgId = ref(null)
const orgOptions = ref([])
const orgLoading = ref(false)

const dateRange = ref([])
const filters = reactive({
  teacher_id: null,
  classroom_id: null
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

// 按日期分组的课表数据
const groupedSessions = computed(() => {
  const groups = {}

  // 获取所有时间段（按开始时间排序）
  const allTimeSlots = [...timeSlotOptions.value].sort((a, b) => a.start_time.localeCompare(b.start_time))

  // 按日期分组
  tableData.value.forEach(session => {
    const date = session.session_date
    if (!groups[date]) {
      groups[date] = {
        date,
        sessions: [],
        teachers: new Map(),
        sessionMap: {},
        timeSlots: allTimeSlots // 使用所有时间段
      }
    }
    groups[date].sessions.push(session)

    // 收集该日期的教师
    if (!groups[date].teachers.has(session.teacher_id)) {
      groups[date].teachers.set(session.teacher_id, { id: session.teacher_id, name: session.teacher_name })
    }

    // 构建映射表
    const key = `${session.teacher_id}_${session.time_slot_id}`
    groups[date].sessionMap[key] = session
  })

  // 转换为数组并排序
  return Object.values(groups)
    .sort((a, b) => a.date.localeCompare(b.date))
    .map(group => ({
      ...group,
      teachers: Array.from(group.teachers.values()).sort((a, b) => a.name.localeCompare(b.name))
    }))
})

const formatDate = (dateStr) => {
  const date = new Date(dateStr)
  return `${date.getMonth() + 1}月${date.getDate()}日`
}

const getWeekday = (dateStr) => {
  const weekdays = ['星期日', '星期一', '星期二', '星期三', '星期四', '星期五', '星期六']
  return weekdays[new Date(dateStr).getDay()]
}

const toggleGroup = (date) => {
  if (expandedDates.value.has(date)) {
    expandedDates.value.delete(date)
  } else {
    expandedDates.value.add(date)
  }
}

const getSession = (teacherId, timeSlotId, sessionMap) => {
  const key = `${teacherId}_${timeSlotId}`
  return sessionMap[key]
}

const getCellClass = (teacherId, timeSlotId, sessionMap) => {
  const session = getSession(teacherId, timeSlotId, sessionMap)
  if (!session) return ''
  return `cell-${session.status}`
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
      page: 1,
      page_size: 100,
      ...filters
    }

    if (dateRange.value && dateRange.value.length === 2) {
      params.start_date = dateRange.value[0]
      params.end_date = dateRange.value[1]
    }

    const res = await scheduleApi.getList(params)
    tableData.value = res.data || []

    // 默认展开所有日期
    expandedDates.value = new Set(tableData.value.map(s => s.session_date))
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
    student_ids: form.student_ids,
    exclude_session_id: form.id
  })
  conflictInfo.value = res
}

watch([() => form.teacher_id, () => form.classroom_id, () => form.session_date, () => form.time_slot_id, () => form.student_ids], () => {
  if (form.session_date && form.time_slot_id) {
    checkConflict()
  }
}, { deep: true })

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

const handleAddWithParams = (teacherId, timeSlotId, date) => {
  form.id = null
  form.course_id = null
  form.teacher_id = teacherId
  form.classroom_id = null
  form.session_date = date
  form.time_slot_id = timeSlotId
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
  form.student_ids = row.student_ids || []
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
    let res
    if (isEdit.value) {
      res = await scheduleApi.update(form.id, form)
    } else {
      res = await scheduleApi.create(form)
    }

    // 检查是否有冲突
    if (res.conflicts && res.conflicts.length > 0) {
      conflictInfo.value = { has_conflict: true, conflicts: res.conflicts }
      ElMessage.error(res.message || '存在排课冲突')
      return
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

  // 超管需要先选择机构
  if (isSuperAdmin.value) {
    exportType.value = type
    exportOrgId.value = null
    exportDialogVisible.value = true
    await fetchOrgOptions()
  } else {
    doExport(type)
  }
}

const fetchOrgOptions = async () => {
  orgLoading.value = true
  try {
    const res = await organizationApi.getList({ page: 1, page_size: 100 })
    orgOptions.value = res.data || []
  } finally {
    orgLoading.value = false
  }
}

const doExport = async (type, orgId = null) => {
  const params = {
    start_date: dateRange.value[0],
    end_date: dateRange.value[1],
    ...filters
  }

  // 超管导出时添加机构ID
  if (orgId) {
    params.org_id = orgId
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
    exportDialogVisible.value = false
  } catch (error) {
    ElMessage.error('导出失败')
  }
}

const confirmExport = () => {
  if (!exportOrgId.value) {
    ElMessage.warning('请选择机构')
    return
  }
  doExport(exportType.value, exportOrgId.value)
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

<style scoped>
.empty-container {
  padding: 40px 0;
  text-align: center;
}

.schedule-groups {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.schedule-group {
  border: 1px solid #ebeef5;
  border-radius: 8px;
  overflow: hidden;
}

.group-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  background: #f5f7fa;
  cursor: pointer;
  user-select: none;
}

.group-header:hover {
  background: #eef1f6;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 8px;
}

.toggle-icon {
  transition: transform 0.3s;
  color: #909399;
}

.toggle-icon.expanded {
  transform: rotate(90deg);
}

.date-text {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.date-weekday {
  font-size: 14px;
  color: #909399;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 8px;
}

.group-content {
  padding: 16px;
}

.schedule-table-wrapper {
  overflow-x: auto;
}

.schedule-table {
  width: 100%;
  border-collapse: collapse;
  border-spacing: 0;
  min-width: 500px;
}

.header-cell {
  background: #f5f7fa;
  border: 1px solid #ebeef5;
  padding: 10px 8px;
  text-align: center;
  font-weight: 600;
  color: #303133;
}

.header-teacher {
  width: 80px;
}

.header-time {
  min-width: 100px;
}

.time-name {
  font-size: 13px;
  margin-bottom: 2px;
}

.time-range {
  font-size: 11px;
  color: #909399;
  font-weight: normal;
}

.cell-teacher {
  border: 1px solid #ebeef5;
  padding: 6px;
  text-align: center;
  font-weight: 500;
  color: #303133;
  background: #fafafa;
}

.cell-content {
  border: 1px solid #ebeef5;
  padding: 4px;
  min-height: 70px;
  vertical-align: top;
}

.cell-scheduled {
  background: #ecf5ff;
}

.cell-completed {
  background: #f0f9eb;
}

.cell-cancelled {
  background: #fef0f0;
}

.cell-rescheduled {
  background: #fdf6ec;
}

.session-card {
  background: #fff;
  border-radius: 4px;
  padding: 6px;
  cursor: pointer;
  transition: all 0.2s;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.08);
}

.session-card:hover {
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.12);
}

.course-name {
  font-size: 13px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 2px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.classroom-name {
  font-size: 11px;
  color: #606266;
}

.student-count {
  font-size: 11px;
  color: #909399;
}

.session-completed {
  opacity: 0.8;
}

.session-cancelled {
  opacity: 0.6;
}

.empty-cell {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 60px;
  cursor: pointer;
  color: #c0c4cc;
  border-radius: 4px;
  transition: all 0.2s;
}

.empty-cell:hover {
  background: #f0f7ff;
  color: #409eff;
}

@media (max-width: 768px) {
  .schedule-table {
    font-size: 12px;
  }

  .header-time {
    min-width: 80px;
  }

  .course-name {
    font-size: 12px;
  }
}
</style>