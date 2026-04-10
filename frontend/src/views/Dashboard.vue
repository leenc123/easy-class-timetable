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
              <span class="schedule-title">今日课表</span>
              <span class="schedule-date">{{ todayDate }}</span>
              <el-button type="primary" link @click="goToSchedule">查看全部</el-button>
            </div>
          </template>

          <div v-if="loading" class="loading-container">
            <el-icon class="is-loading" :size="32"><Loading /></el-icon>
          </div>

          <div v-else-if="todaySchedule.length === 0" class="empty-container">
            <el-empty description="今日暂无课程安排" />
          </div>

          <div v-else class="schedule-timeline">
            <div
              v-for="item in todaySchedule"
              :key="item.id"
              class="schedule-item"
              :class="{'schedule-item-completed': item.status === 'completed', 'schedule-item-current': isCurrentSession(item)}"
            >
              <div class="schedule-time">
                <div class="time-slot">{{ item.time_slot_name || `第${item.time_slot_id}节` }}</div>
                <div class="time-range">{{ item.start_time }} - {{ item.end_time }}</div>
              </div>
              <div class="schedule-content">
                <div class="course-name">{{ item.course_name }}</div>
                <div class="course-info">
                  <span class="info-item">
                    <el-icon><User /></el-icon>
                    {{ item.teacher_name }}
                  </span>
                  <span class="info-item">
                    <el-icon><Location /></el-icon>
                    {{ item.classroom_name }}
                  </span>
                  <span class="info-item">
                    <el-icon><Avatar /></el-icon>
                    {{ item.student_count }}人
                  </span>
                </div>
              </div>
              <div class="schedule-status">
                <el-tag :type="getStatusType(item.status)" size="small">
                  {{ getStatusText(item.status) }}
                </el-tag>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { scheduleApi } from '@/api/schedule'
import { teacherApi, studentApi, courseApi } from '@/api/resource'
import { Reading, User, Avatar, Collection, Location, Loading } from '@element-plus/icons-vue'

const router = useRouter()
const loading = ref(false)

const stats = reactive({
  todaySessions: 0,
  teacherCount: 0,
  studentCount: 0,
  courseCount: 0
})

const todaySchedule = ref([])

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

const isCurrentSession = (item) => {
  if (item.status !== 'scheduled') return false
  const now = new Date()
  const currentTime = `${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}`
  return item.start_time <= currentTime && item.end_time > currentTime
}

const goToSchedule = () => {
  router.push('/schedule')
}

const fetchData = async () => {
  loading.value = true
  try {
    // 获取今日课表
    const today = new Date().toISOString().split('T')[0]
    const scheduleRes = await scheduleApi.getList({
      start_date: today,
      end_date: today,
      page_size: 20
    })
    todaySchedule.value = scheduleRes.data || []
    stats.todaySessions = scheduleRes.total || 0

    // 获取统计数据
    const [teachers, students, courses] = await Promise.all([
      teacherApi.getList({ page: 1, page_size: 1 }),
      studentApi.getList({ page: 1, page_size: 1 }),
      courseApi.getList({ page: 1, page_size: 1 })
    ])

    stats.teacherCount = teachers.total || 0
    stats.studentCount = students.total || 0
    stats.courseCount = courses.total || 0
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

.schedule-timeline {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.schedule-item {
  display: flex;
  align-items: center;
  padding: 16px;
  background: #f8fafc;
  border-radius: 8px;
  border-left: 4px solid #409eff;
  transition: all 0.3s;
}

.schedule-item:hover {
  background: #f0f7ff;
}

.schedule-item-completed {
  border-left-color: #67c23a;
  background: #f0f9eb;
}

.schedule-item-current {
  border-left-color: #e6a23c;
  background: #fdf6ec;
  box-shadow: 0 2px 8px rgba(230, 162, 60, 0.2);
}

.schedule-time {
  width: 100px;
  flex-shrink: 0;
  text-align: center;
}

.time-slot {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.time-range {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

.schedule-content {
  flex: 1;
  padding: 0 20px;
}

.course-name {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 8px;
}

.course-info {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
}

.info-item {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 13px;
  color: #606266;
}

.info-item .el-icon {
  color: #909399;
}

.schedule-status {
  flex-shrink: 0;
}

@media (max-width: 768px) {
  .schedule-item {
    flex-direction: column;
    align-items: flex-start;
  }

  .schedule-time {
    width: auto;
    margin-bottom: 8px;
  }

  .schedule-content {
    padding: 0;
    margin-bottom: 8px;
  }

  .schedule-status {
    margin-top: 8px;
  }
}
</style>