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
            <span>今日课表</span>
            <el-button type="primary" link @click="goToSchedule">查看全部</el-button>
          </template>
          <el-table :data="todaySchedule" v-loading="loading" stripe>
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
            <el-table-column prop="status" label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="getStatusType(row.status)">
                  {{ getStatusText(row.status) }}
                </el-tag>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { scheduleApi } from '@/api/schedule'
import { teacherApi, studentApi, courseApi } from '@/api/resource'
import { Reading, User, Avatar, Collection } from '@element-plus/icons-vue'

const router = useRouter()
const loading = ref(false)

const stats = reactive({
  todaySessions: 0,
  teacherCount: 0,
  studentCount: 0,
  courseCount: 0
})

const todaySchedule = ref([])

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
    scheduled: '已安排',
    completed: '已完成',
    cancelled: '已取消',
    rescheduled: '已调课'
  }
  return texts[status] || status
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
      page_size: 10
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
</style>