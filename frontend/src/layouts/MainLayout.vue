<template>
  <div class="main-layout">
    <!-- 移动端菜单按钮 -->
    <div class="mobile-header" v-if="isMobile">
      <el-button @click="drawerVisible = true" :icon="Menu" />
      <span class="logo">{{ appTitle }}</span>
      <el-dropdown @command="handleCommand">
        <el-avatar :size="32" :icon="UserFilled" />
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item command="profile">{{ userStore.user?.real_name }}</el-dropdown-item>
            <el-dropdown-item command="logout" divided>退出登录</el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </div>

    <!-- 移动端侧边栏抽屉 -->
    <el-drawer
      v-model="drawerVisible"
      direction="ltr"
      :with-header="false"
      size="220px"
      v-if="isMobile"
      class="mobile-drawer"
    >
      <sidebar-menu @select="drawerVisible = false" />
    </el-drawer>

    <!-- 桌面端布局 -->
    <el-container v-else class="desktop-layout">
      <el-aside :width="isCollapsed ? '64px' : '220px'" class="sidebar">
        <div class="logo-wrapper">
          <span class="logo" v-show="!isCollapsed">{{ appTitle }}</span>
          <el-icon v-show="isCollapsed" class="logo-icon"><Calendar /></el-icon>
        </div>
        <!-- 折叠按钮 -->
        <div class="collapse-btn" @click="toggleCollapse">
          <el-icon :size="20">
            <component :is="isCollapsed ? 'Expand' : 'Fold'" />
          </el-icon>
        </div>
        <sidebar-menu :is-collapsed="isCollapsed" />
      </el-aside>
      <el-main>
        <div class="header">
          <el-breadcrumb separator="/">
            <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
            <el-breadcrumb-item v-if="currentRouteName">{{ currentRouteName }}</el-breadcrumb-item>
          </el-breadcrumb>
          <el-dropdown @command="handleCommand">
            <span class="user-info">
              <el-avatar :size="32" :icon="UserFilled" />
              <span class="username">{{ userStore.user?.real_name }}</span>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">个人信息</el-dropdown-item>
                <el-dropdown-item command="logout" divided>退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
        <div class="content">
          <router-view />
        </div>
      </el-main>
    </el-container>

    <!-- 移动端内容 -->
    <div class="mobile-content" v-if="isMobile">
      <router-view />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { Menu, UserFilled, Fold, Expand, Calendar } from '@element-plus/icons-vue'
import SidebarMenu from '@/components/SidebarMenu.vue'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

const appTitle = '排课表系统'
const drawerVisible = ref(false)
const windowWidth = ref(window.innerWidth)
const isCollapsed = ref(false)

const isMobile = computed(() => windowWidth.value < 768)

const currentRouteName = computed(() => route.meta?.title || route.name)

const toggleCollapse = () => {
  isCollapsed.value = !isCollapsed.value
}

const handleCommand = (command) => {
  if (command === 'logout') {
    userStore.logout()
  }
}

const handleResize = () => {
  windowWidth.value = window.innerWidth
}

onMounted(() => {
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
})
</script>

<style scoped>
.main-layout {
  height: 100%;
}

.desktop-layout {
  height: 100%;
}

.sidebar {
  background: #304156;
  color: #fff;
  transition: width 0.3s ease;
  overflow: hidden;
}

.logo-wrapper {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-bottom: 1px solid #3a4a5b;
}

.logo {
  font-size: 18px;
  font-weight: bold;
  color: #fff;
}

.logo-icon {
  font-size: 24px;
  color: #fff;
}

.collapse-btn {
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: #bfcbd9;
  border-bottom: 1px solid #3a4a5b;
  transition: all 0.3s;
}

.collapse-btn:hover {
  background-color: #263445;
  color: #409eff;
}

.el-main {
  background: #f0f2f5;
  padding: 0;
}

.header {
  height: 60px;
  background: #fff;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  box-shadow: 0 1px 4px rgba(0, 21, 41, 0.08);
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
}

.username {
  font-size: 14px;
  color: #303133;
}

.content {
  padding: 20px;
  min-height: calc(100vh - 60px);
}

/* 移动端样式 */
.mobile-header {
  height: 50px;
  background: #304156;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 15px;
  color: #fff;
}

.mobile-content {
  padding: 15px;
  min-height: calc(100vh - 50px);
  background: #f0f2f5;
}
</style>

<style>
/* 移动端抽屉样式 - 需要全局样式覆盖 el-drawer 内边距 */
.mobile-drawer .el-drawer__body {
  padding: 0 !important;
  background-color: #304156;
}
</style>