<template>
  <el-menu
    :default-active="activeMenu"
    :router="true"
    :collapse="isCollapsed"
    background-color="#304156"
    text-color="#bfcbd9"
    active-text-color="#409eff"
    @select="handleSelect"
  >
    <el-menu-item index="/">
      <el-icon><HomeFilled /></el-icon>
      <template #title>首页</template>
    </el-menu-item>

    <el-sub-menu index="resources" v-if="showResourceMenu">
      <template #title>
        <el-icon><Collection /></el-icon>
        <span>资源管理</span>
      </template>
      <el-menu-item index="/classrooms">
        <el-icon><School /></el-icon>
        <template #title>教室管理</template>
      </el-menu-item>
      <el-menu-item index="/teachers">
        <el-icon><User /></el-icon>
        <template #title>教师管理</template>
      </el-menu-item>
      <el-menu-item index="/students">
        <el-icon><Avatar /></el-icon>
        <template #title>学生管理</template>
      </el-menu-item>
      <el-menu-item index="/courses">
        <el-icon><Reading /></el-icon>
        <template #title>课程管理</template>
      </el-menu-item>
    </el-sub-menu>

    <el-menu-item index="/cycles">
      <el-icon><Calendar /></el-icon>
      <template #title>排课周期</template>
    </el-menu-item>

    <el-menu-item index="/schedule">
      <el-icon><Grid /></el-icon>
      <template #title>课表管理</template>
    </el-menu-item>

    <el-menu-item index="/checkins">
      <el-icon><Finished /></el-icon>
      <template #title>课程盘点</template>
    </el-menu-item>

    <el-menu-item index="/users" v-if="showUserMenu">
      <el-icon><Setting /></el-icon>
      <template #title>用户管理</template>
    </el-menu-item>

    <el-menu-item index="/organizations" v-if="showOrgMenu">
      <el-icon><OfficeBuilding /></el-icon>
      <template #title>机构管理</template>
    </el-menu-item>
  </el-menu>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useUserStore } from '@/stores/user'
import {
  HomeFilled, Collection, School, User, Avatar,
  Reading, Calendar, Grid, Finished, Setting, OfficeBuilding
} from '@element-plus/icons-vue'

const route = useRoute()
const userStore = useUserStore()

const props = defineProps({
  isCollapsed: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['select'])

const activeMenu = computed(() => route.path)

const userRole = computed(() => userStore.user?.role)

const handleSelect = () => {
  emit('select')
}

// 菜单权限控制
const showResourceMenu = computed(() => ['super_admin', 'org_admin'].includes(userRole.value))
const showUserMenu = computed(() => ['super_admin', 'org_admin'].includes(userRole.value))
const showOrgMenu = computed(() => userRole.value === 'super_admin')
</script>

<style scoped>
.el-menu {
  border-right: none;
}

.el-menu:not(.el-menu--collapse) {
  width: 220px;
}

.el-menu--collapse {
  width: 64px;
}

.el-menu-item.is-active {
  background-color: #263445 !important;
}

/* PC端侧边栏内边距 */
.el-menu-item,
.el-sub-menu__title {
  padding-left: 20px !important;
}

.el-menu--collapse .el-menu-item,
.el-menu--collapse .el-sub-menu__title {
  padding-left: 0 !important;
}
</style>