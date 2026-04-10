<template>
  <div class="dashboard">
    <el-row :gutter="20">
      <el-col :xs="12" :sm="6">
        <el-card class="stat-card">
          <el-statistic title="今日课程" :value="stats.todaySessions">
            <template #prefix>
              <el-icon><Reading /></el-icon>
            </template>
          </el-statistic>
        </el-card>
      </el-col>
      <el-col :xs="12" :sm="6">
        <el-card class="stat-card">
          <el-statistic title="教师总数" :value="stats.teacherCount">
            <template #prefix>
              <el-icon><User /></el-icon>
            </template>
          </el-statistic>
        </el-card>
      </el-col>
      <el-col :xs="12" :sm="6">
        <el-card class="stat-card">
          <el-statistic title="学生总数" :value="stats.studentCount">
            <template #prefix>
              <el-icon><Avatar /></el-icon>
            </template>
          </el-statistic>
        </el-card>
      </el-col>
      <el-col :xs="12" :sm="6">
        <el-card class="stat-card">
          <el-statistic title="课程总数" :value="stats.courseCount">
            <template #prefix>
              <el-icon><Collection /></el-icon>
            </template>
          </el-statistic>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :span="24">
        <el-card>
          <template #header>
            <div class="schedule-header">
              <div class="header-left">
                <span class="schedule-title">今日课表</span>
                <span class="schedule-date">{{ todayDate }}</span>
              </div>
              <el-button type="primary" link @click="goToSchedule">查看全部</el-button>
            </div>
          </template>

          <div v-if="loading" class="loading-container">
            <el-icon class="is-loading" :size="32"><Loading /></el-icon>
          </div>

          <div v-else-if="timeSlots.length === 0" class="empty-container">
            <el-empty description="请先在排课周期中配置时间段" />
          </div>

          <div v-else-if="teachers.length === 0" class="empty-container">
            <el-empty description="暂无教师，请先添加教师" />
          </div>

          <div v-else class="schedule-table-wrapper">
            <table class="schedule-table">
              <thead>
                <tr>
                  <th class="header-cell header-teacher">教师</th>
                  <th
                    v-for="slot in timeSlots"
                    :key="slot.id"
                    class="header-cell header-time"
                  >
                    <div class="time-name">{{ slot.name }}</div>
                    <div class="time-range">{{ slot.start_time }}-{{ slot.end_time }}</div>
                  </th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="teacher in teachers" :key="teacher.id">
                  <td class="cell-teacher">{{ teacher.name }}</td>
                  <td
                    v-for="slot in timeSlots"
                    :key="slot.id"
                    class="cell-content"
                    :class="getCellClass(teacher.id, slot.id)"
                  >
                    <div
                      v-if="getSession(teacher.id, slot.id)"
                      class="session-card"
                      @click="showSessionDetail(getSession(teacher.id, slot.id))"
                    >
                      <div class="course-name">{{ getSession(teacher.id, slot.id).course_name }}</div>
                      <div class="classroom-name">{{ getSession(teacher.id, slot.id).classroom_name }}</div>
                      <div class="student-count">{{ getSession(teacher.id, slot.id).student_count }}人</div>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 课程详情弹窗 -->
    <el-dialog v-model="detailVisible" title="课程详情" width="400px">
      <div v-if="currentSession" class="session-detail">
        <el-descriptions :column="1" border>
          <el-descriptions-item label="课程">{{ currentSession.course_name }}</el-descriptions-item>
          <el-descriptions-item label="教师">{{ currentSession.teacher_name }}</el-descriptions-item>
          <el-descriptions-item label="教室">{{ currentSession.classroom_name }}</el-descriptions-item>
          <el-descriptions-item label="时间">{{ currentSession.time_slot_name }}</el-descriptions-item>
          <el-descriptions-item label="学生数">{{ currentSession.student_count }}人</el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="getStatusType(currentSession.status)" size="small">
              {{ getStatusText(currentSession.status) }}
            </el-tag>
          </el-descriptions-item>
        </el-descriptions>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { scheduleApi, cycleApi } from '@/api/schedule'
import { teacherApi, studentApi, courseApi } from '@/api/resource'
import { Reading, User, Avatar, Collection, Loading } from '@element-plus/icons-vue'

const router = useRouter()
const loading = ref(false)

const stats = reactive({
  todaySessions: 0,
  teacherCount: 0,
  studentCount: 0,
  courseCount: 0
})

const timeSlots = ref([])
const teachers = ref([])
const sessions = ref([])
const sessionMap = ref({})

const detailVisible = ref(false)
const currentSession = ref(null)

const todayDate = computed(() => {
  const today = new Date()
  const weekDays = ['星期日', '星期一', '星期二', '星期三', '星期四', '星期五', '星期六']
  return `${today.getFullYear()}年${today.getMonth() + 1}月${today.getDate()}日 ${weekDays[today.getDay()]}`
})

const getStatusType = (status) => {
  const types = {
    scheduled: '',
    completed: 'success',
    cancelled: 'danger',
    rescheduled: 'warning'
  }
  return types[status] || ''
}

const getStatusText = (status) => {
  const texts = {
    scheduled: '待上课',
    completed: '已完成',
    cancelled: '已取消',
    rescheduled: '已调课'
  }
  return texts[status] || status
}

const getSession = (teacherId, timeSlotId) => {
  const key = `${teacherId}_${timeSlotId}`
  return sessionMap.value[key]
}

const getCellClass = (teacherId, timeSlotId) => {
  const session = getSession(teacherId, timeSlotId)
  if (!session) return ''
  return `cell-${session.status}`
}

const showSessionDetail = (session) => {
  currentSession.value = session
  detailVisible.value = true
}

const goToSchedule = () => {
  router.push('/schedule')
}

const fetchData = async () => {
  loading.value = true
  try {
    const today = new Date().toISOString().split('T')[0]

    // 并行获取所有数据
    const [slotsRes, teachersRes, scheduleRes, studentsRes, coursesRes] = await Promise.all([
      cycleApi.getTimeSlots(),
      teacherApi.getList({ page: 1, page_size: 100 }),
      scheduleApi.getList({ start_date: today, end_date: today, page_size: 100 }),
      studentApi.getList({ page: 1, page_size: 1 }),
      courseApi.getList({ page: 1, page_size: 1 })
    ])

    // 时间段按开始时间排序
    timeSlots.value = (slotsRes.data || []).sort((a, b) => {
      return a.start_time.localeCompare(b.start_time)
    })

    teachers.value = teachersRes.data || []
    sessions.value = scheduleRes.data || []

    // 构建课程映射表 (teacher_id + time_slot_id -> session)
    const map = {}
    sessions.value.forEach(session => {
      const key = `${session.teacher_id}_${session.time_slot_id}`
      map[key] = session
    })
    sessionMap.value = map

    stats.todaySessions = scheduleRes.total || 0
    stats.teacherCount = teachersRes.total || 0
    stats.studentCount = studentsRes.total || 0
    stats.courseCount = coursesRes.total || 0
  } catch (error) {
    console.error('获取数据失败:', error)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchData()
})
</script>

<style scoped>
.dashboard {
  padding: 0;
}

.stat-card {
  text-align: center;
}

:deep(.el-statistic__head) {
  font-size: 14px;
  color: #909399;
}

:deep(.el-statistic__content) {
  font-size: 28px;
  font-weight: bold;
}

.schedule-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.schedule-title {
  font-size: 16px;
  font-weight: 600;
}

.schedule-date {
  color: #909399;
  font-size: 14px;
}

.loading-container,
.empty-container {
  padding: 40px 0;
  text-align: center;
}

.schedule-table-wrapper {
  overflow-x: auto;
}

.schedule-table {
  width: 100%;
  border-collapse: collapse;
  border-spacing: 0;
  min-width: 600px;
}

.header-cell {
  background: #f5f7fa;
  border: 1px solid #ebeef5;
  padding: 12px 8px;
  text-align: center;
  font-weight: 600;
  color: #303133;
}

.header-teacher {
  width: 100px;
  position: sticky;
  left: 0;
  z-index: 2;
  background: #f5f7fa;
}

.header-time {
  min-width: 120px;
}

.time-name {
  font-size: 14px;
  margin-bottom: 4px;
}

.time-range {
  font-size: 12px;
  color: #909399;
  font-weight: normal;
}

.cell-teacher {
  border: 1px solid #ebeef5;
  padding: 8px;
  text-align: center;
  font-weight: 500;
  color: #303133;
  background: #fafafa;
  position: sticky;
  left: 0;
  z-index: 1;
}

.cell-content {
  border: 1px solid #ebeef5;
  padding: 4px;
  min-height: 80px;
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
  border-radius: 6px;
  padding: 8px;
  cursor: pointer;
  transition: all 0.2s;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  height: 100%;
}

.session-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.course-name {
  font-size: 14px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 4px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.classroom-name {
  font-size: 12px;
  color: #606266;
  margin-bottom: 2px;
}

.student-count {
  font-size: 12px;
  color: #909399;
}

.session-detail {
  padding: 10px 0;
}

@media (max-width: 768px) {
  .header-left {
    flex-direction: column;
    align-items: flex-start;
    gap: 4px;
  }

  .schedule-table {
    font-size: 12px;
  }

  .header-time {
    min-width: 100px;
  }

  .course-name {
    font-size: 12px;
  }
}
</style>