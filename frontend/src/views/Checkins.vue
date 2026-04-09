<template>
  <div class="page-container">
    <div class="page-header">
      <h3 class="page-title">课程盘点</h3>
    </div>

    <!-- 筛选 -->
    <el-card style="margin-bottom: 20px">
      <el-form :inline="true" @submit.prevent="fetchData">
        <el-form-item label="日期">
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
        <el-form-item>
          <el-button type="primary" @click="fetchData">查询</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 列表 -->
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
        <el-table-column label="应到" width="80">
          <template #default="{ row }">
            {{ row.checkin?.expected_count ?? row.student_count ?? '-' }}
          </template>
        </el-table-column>
        <el-table-column label="实到" width="80">
          <template #default="{ row }">
            {{ row.checkin?.actual_count ?? '-' }}
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag v-if="row.checkin" type="success">已盘点</el-tag>
            <el-tag v-else type="warning">待盘点</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="120" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="handleCheckin(row)" :disabled="!!row.checkin">
              {{ row.checkin ? '已盘点' : '盘点' }}
            </el-button>
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

    <!-- 盘点弹窗 -->
    <el-dialog v-model="checkinDialogVisible" title="课程人数盘点" width="400px">
      <el-form ref="checkinFormRef" :model="checkinForm" :rules="checkinRules" label-width="80px">
        <el-form-item label="课程">
          <span>{{ currentSession?.course_name }}</span>
        </el-form-item>
        <el-form-item label="时间">
          <span>{{ currentSession?.session_date }} {{ currentSession?.start_time }}-{{ currentSession?.end_time }}</span>
        </el-form-item>
        <el-form-item label="应到人数" prop="expected_count">
          <el-input-number v-model="checkinForm.expected_count" :min="0" :max="500" style="width: 100%" />
        </el-form-item>
        <el-form-item label="实到人数" prop="actual_count">
          <el-input-number v-model="checkinForm.actual_count" :min="0" :max="500" style="width: 100%" />
        </el-form-item>
        <el-form-item label="备注" prop="notes">
          <el-input v-model="checkinForm.notes" type="textarea" rows="2" placeholder="如有缺勤原因可填写" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="checkinDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitLoading" @click="submitCheckin">提交</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { scheduleApi, checkinApi } from '@/api/schedule'
import { teacherApi } from '@/api/resource'

const loading = ref(false)
const submitLoading = ref(false)
const checkinDialogVisible = ref(false)
const tableData = ref([])
const checkinFormRef = ref()
const currentSession = ref(null)

const dateRange = ref([])
const filters = reactive({
  teacher_id: null
})

const pagination = reactive({
  page: 1,
  pageSize: 20,
  total: 0
})

const teacherOptions = ref([])

const checkinForm = reactive({
  session_id: null,
  expected_count: 0,
  actual_count: 0,
  notes: ''
})

const checkinRules = {
  expected_count: [{ required: true, message: '请输入应到人数', trigger: 'blur' }],
  actual_count: [{ required: true, message: '请输入实到人数', trigger: 'blur' }]
}

const fetchTeachers = async () => {
  const res = await teacherApi.getList({ page_size: 1000 })
  teacherOptions.value = res.data || []
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

const handleCheckin = (row) => {
  currentSession.value = row
  checkinForm.session_id = row.id
  checkinForm.expected_count = row.student_count || 0
  checkinForm.actual_count = 0
  checkinForm.notes = ''
  checkinDialogVisible.value = true
}

const submitCheckin = async () => {
  await checkinFormRef.value.validate()
  submitLoading.value = true
  try {
    await checkinApi.create(checkinForm)
    ElMessage.success('盘点成功')
    checkinDialogVisible.value = false
    fetchData()
  } finally {
    submitLoading.value = false
  }
}

onMounted(() => {
  // 默认查询今天
  const today = new Date().toISOString().split('T')[0]
  dateRange.value = [today, today]

  fetchTeachers()
  fetchData()
})
</script>