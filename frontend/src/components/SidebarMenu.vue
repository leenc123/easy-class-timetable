<template>
  <el-menu
    :default-active="activeMenu"
    :router="true"
    background-color="#304156"
    text-color="#bfcbd9"
    active-text-color="#409eff"
  >
    <el-menu-item index="/">
      <el-icon><HomeFilled /></el-icon>
      <span>首页</span>
    </el-menu-item>

    <el-sub-menu index="resources" v-if="showResourceMenu">
      <template #title>
        <el-icon><Collection /></el-icon>
        <span>资源管理</span>
      </template>
      <el-menu-item index="/classrooms">
        <el-icon><School /></el-icon>
        <span>教室管理</span>
      </el-menu-item>
      <el-menu-item index="/teachers">
        <el-icon><User /></el-icon>
        <span>教师管理</span>
      </el-menu-item>
      <el-menu-item index="/students">
        <el-icon><Avatar /></el-icon>
        <span>学生管理</span>
      </el-menu-item>
      <el-menu-item index="/courses">
        <el-icon><Reading /></el-icon>
        <span>课程管理</span>
      </el-menu-item>
    </el-sub-menu>

    <el-menu-item index="/cycles">
      <el-icon><Calendar /></el-icon>
      <span>排课周期</span>
    </el-menu-item>

    <el-menu-item index="/schedule">
      <el-icon><Grid /></el-icon>
      <span>课表管理</span>
    </el-menu-item>

    <el-menu-item index="/checkins">
      <el-icon><Finished /></el-icon>
      <span>课程盘点</span>
    </el-menu-item>

    <el-menu-item index="/users" v-if="showUserMenu">
      <el-icon><Setting /></el-icon>
      <span>用户管理</span>
    </el-menu-item>

    <el-menu-item index="/organizations" v-if="showOrgMenu">
      <el-icon><OfficeBuilding /></el-icon>
      <span>机构管理</span>
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

const emit = defineEmits(['select'])

const activeMenu = computed(() => route.path)

const userRole = computed(() => userStore.user?.role)

// 菜单权限控制
const showResourceMenu = computed(() => ['super_admin', 'org_admin'].includes(userRole.value))
const showUserMenu = computed(() => ['super_admin', 'org_admin'].includes(userRole.value))
const showOrgMenu = computed(() => userRole.value === 'super_admin')
</script>

<style scoped>
.el-menu {
  border-right: none;
}

.el-menu-item.is-active {
  background-color: #263445 !important;
}
</style>