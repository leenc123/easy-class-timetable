<template>
  <div class="page-container">
    <div class="page-header">
      <h3 class="page-title">排课周期</h3>
      <el-button type="primary" @click="handleAddCycle">
        <el-icon><Plus /></el-icon>新增周期
      </el-button>
    </div>

    <el-row :gutter="20">
      <!-- 周期列表 -->
      <el-col :span="24">
        <el-card>
          <template #header>
            <span>周期列表</span>
          </template>
          <el-table :data="cycleList" v-loading="loading" stripe>
            <el-table-column prop="name" label="周期名称" />
            <el-table-column prop="cycle_days" label="周期天数" width="100" />
            <el-table-column prop="start_date" label="开始日期" width="120" />
            <el-table-column prop="end_date" label="结束日期" width="120" />
            <el-table-column prop="is_active" label="状态" width="80">
              <template #default="{ row }">
                <el-tag :type="row.is_active ? 'success' : 'info'">
                  {{ row.is_active ? '启用' : '禁用' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="200">
              <template #default="{ row }">
                <el-button type="primary" link @click="handleEditCycle(row)">编辑</el-button>
                <el-button type="warning" link @click="handleGenerateDates(row)">生成日期</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px">
      <!-- 时间段设置 -->
      <el-col :span="24">
        <el-card>
          <template #header>
            <div style="display: flex; justify-content: space-between; align-items: center">
              <span>时间段设置</span>
              <el-button type="primary" size="small" @click="handleAddTimeSlot">新增时间段</el-button>
            </div>
          </template>
          <el-table :data="timeSlotList" stripe size="small">
            <el-table-column prop="display_order" label="序号" width="60" />
            <el-table-column prop="name" label="名称" />
            <el-table-column prop="start_time" label="开始时间" width="100" />
            <el-table-column prop="end_time" label="结束时间" width="100" />
            <el-table-column label="操作" width="100">
              <template #default="{ row }">
                <el-button type="primary" link size="small" @click="handleEditTimeSlot(row)">编辑</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>

    <!-- 周期编辑弹窗 -->
    <el-dialog v-model="cycleDialogVisible" :title="isEditCycle ? '编辑周期' : '新增周期'" width="450px">
      <el-form ref="cycleFormRef" :model="cycleForm" :rules="cycleRules" label-width="80px">
        <!-- 超管创建时显示机构选择 -->
        <el-form-item v-if="isSuperAdmin && !isEditCycle" label="所属机构" prop="org_id">
          <el-select v-model="cycleForm.org_id" placeholder="请选择机构" style="width: 100%" :loading="orgLoading">
            <el-option
              v-for="org in orgList"
              :key="org.id"
              :label="org.name"
              :value="org.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="名称" prop="name">
          <el-input v-model="cycleForm.name" placeholder="如：7天循环、10天循环" />
        </el-form-item>
        <el-form-item label="周期天数" prop="cycle_days">
          <el-input-number v-model="cycleForm.cycle_days" :min="1" :max="365" />
        </el-form-item>
        <el-form-item label="开始日期" prop="start_date">
          <el-date-picker v-model="cycleForm.start_date" type="date" placeholder="选择日期" value-format="YYYY-MM-DD" style="width: 100%" />
        </el-form-item>
        <el-form-item label="结束日期" prop="end_date">
          <el-date-picker v-model="cycleForm.end_date" type="date" placeholder="选择日期" value-format="YYYY-MM-DD" style="width: 100%" />
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input v-model="cycleForm.description" type="textarea" rows="2" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="cycleDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitLoading" @click="submitCycle">确定</el-button>
      </template>
    </el-dialog>

    <!-- 生成日期弹窗 -->
    <el-dialog v-model="generateDialogVisible" title="生成周期日期映射" width="400px">
      <el-form label-width="80px">
        <el-form-item label="结束日期">
          <el-date-picker v-model="generateEndDate" type="date" placeholder="选择日期" value-format="YYYY-MM-DD" style="width: 100%" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="generateDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitLoading" @click="doGenerateDates">生成</el-button>
      </template>
    </el-dialog>

    <!-- 时间段编辑弹窗 -->
    <el-dialog v-model="timeSlotDialogVisible" :title="isEditTimeSlot ? '编辑时间段' : '新增时间段'" width="400px">
      <el-form ref="timeSlotFormRef" :model="timeSlotForm" :rules="timeSlotRules" label-width="80px">
        <!-- 超管创建时显示机构选择 -->
        <el-form-item v-if="isSuperAdmin && !isEditTimeSlot" label="所属机构" prop="org_id">
          <el-select v-model="timeSlotForm.org_id" placeholder="请选择机构" style="width: 100%" :loading="orgLoading">
            <el-option
              v-for="org in orgList"
              :key="org.id"
              :label="org.name"
              :value="org.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="名称" prop="name">
          <el-input v-model="timeSlotForm.name" placeholder="如：第1节、早读" />
        </el-form-item>
        <el-form-item label="开始时间" prop="start_time">
          <el-time-select v-model="timeSlotForm.start_time" placeholder="选择时间" style="width: 100%" start="08:00" end="21:00" step="01:00" />
        </el-form-item>
        <el-form-item label="结束时间" prop="end_time">
          <el-time-select v-model="timeSlotForm.end_time" placeholder="选择时间" style="width: 100%" start="08:00" end="21:00" step="01:00" />
        </el-form-item>
        <el-form-item label="序号" prop="display_order">
          <el-input-number v-model="timeSlotForm.display_order" :min="1" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="timeSlotDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitLoading" @click="submitTimeSlot">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { cycleApi } from '@/api/schedule'
import { organizationApi } from '@/api/organization'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()
const isSuperAdmin = computed(() => userStore.user?.role === 'super_admin')

const loading = ref(false)
const submitLoading = ref(false)

// 机构相关
const orgList = ref([])
const orgLoading = ref(false)

const cycleList = ref([])
const timeSlotList = ref([])

const cycleDialogVisible = ref(false)
const generateDialogVisible = ref(false)
const timeSlotDialogVisible = ref(false)
const isEditCycle = ref(false)
const isEditTimeSlot = ref(false)
const currentCycleId = ref(null)
const generateEndDate = ref('')

const cycleFormRef = ref()
const timeSlotFormRef = ref()

const cycleForm = reactive({
  id: null,
  org_id: null,
  name: '',
  cycle_days: 7,
  start_date: '',
  end_date: '',
  description: ''
})

const timeSlotForm = reactive({
  id: null,
  org_id: null,
  name: '',
  start_time: '',
  end_time: '',
  display_order: 1
})

const cycleRules = {
  name: [{ required: true, message: '请输入名称', trigger: 'blur' }],
  cycle_days: [{ required: true, message: '请输入天数', trigger: 'blur' }],
  start_date: [{ required: true, message: '请选择开始日期', trigger: 'change' }],
  org_id: [{ required: true, message: '请选择所属机构', trigger: 'change' }]
}

const timeSlotRules = {
  name: [{ required: true, message: '请输入名称', trigger: 'blur' }],
  start_time: [{ required: true, message: '请选择开始时间', trigger: 'change' }],
  end_time: [{ required: true, message: '请选择结束时间', trigger: 'change' }],
  org_id: [{ required: true, message: '请选择所属机构', trigger: 'change' }]
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

const fetchCycles = async () => {
  loading.value = true
  try {
    const res = await cycleApi.getList({ page: 1, page_size: 100 })
    cycleList.value = res.data || []
  } finally {
    loading.value = false
  }
}

const fetchTimeSlots = async () => {
  const orgId = userStore.user?.org_id
  const res = await cycleApi.getTimeSlots(orgId)
  timeSlotList.value = res.data || []
}

const handleAddCycle = () => {
  cycleForm.id = null
  cycleForm.org_id = null
  cycleForm.name = ''
  cycleForm.cycle_days = 7
  cycleForm.start_date = ''
  cycleForm.end_date = ''
  cycleForm.description = ''
  isEditCycle.value = false
  cycleDialogVisible.value = true
}

const handleEditCycle = (row) => {
  Object.assign(cycleForm, row)
  isEditCycle.value = true
  cycleDialogVisible.value = true
}

const handleGenerateDates = (row) => {
  currentCycleId.value = row.id
  generateEndDate.value = ''
  generateDialogVisible.value = true
}

const doGenerateDates = async () => {
  if (!generateEndDate.value) {
    ElMessage.warning('请选择结束日期')
    return
  }
  submitLoading.value = true
  try {
    const res = await cycleApi.generateDates(currentCycleId.value, generateEndDate.value)
    ElMessage.success(res.message)
    generateDialogVisible.value = false
  } finally {
    submitLoading.value = false
  }
}

const submitCycle = async () => {
  await cycleFormRef.value.validate()
  submitLoading.value = true
  try {
    const submitData = { ...cycleForm }
    if (!isSuperAdmin.value) {
      delete submitData.org_id
    }

    if (isEditCycle.value) {
      await cycleApi.update(cycleForm.id, submitData)
    } else {
      await cycleApi.create(submitData)
    }
    ElMessage.success('保存成功')
    cycleDialogVisible.value = false
    fetchCycles()
  } finally {
    submitLoading.value = false
  }
}

const handleAddTimeSlot = () => {
  timeSlotForm.id = null
  timeSlotForm.org_id = null
  timeSlotForm.name = ''
  timeSlotForm.start_time = ''
  timeSlotForm.end_time = ''
  timeSlotForm.display_order = timeSlotList.value.length + 1
  isEditTimeSlot.value = false
  timeSlotDialogVisible.value = true
}

const handleEditTimeSlot = (row) => {
  Object.assign(timeSlotForm, row)
  isEditTimeSlot.value = true
  timeSlotDialogVisible.value = true
}

const submitTimeSlot = async () => {
  await timeSlotFormRef.value.validate()
  submitLoading.value = true
  try {
    const submitData = { ...timeSlotForm }
    if (!isSuperAdmin.value) {
      delete submitData.org_id
    }

    if (isEditTimeSlot.value) {
      await cycleApi.updateTimeSlot(timeSlotForm.id, submitData)
    } else {
      await cycleApi.createTimeSlot(submitData)
    }
    ElMessage.success('保存成功')
    timeSlotDialogVisible.value = false
    fetchTimeSlots()
  } finally {
    submitLoading.value = false
  }
}

onMounted(() => {
  fetchCycles()
  fetchTimeSlots()
  fetchOrgList()
})
</script>