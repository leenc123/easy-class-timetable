import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '@/stores/user'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/',
    component: () => import('@/layouts/MainLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        name: 'Dashboard',
        component: () => import('@/views/Dashboard.vue')
      },
      {
        path: 'organizations',
        name: 'Organizations',
        component: () => import('@/views/Organizations.vue'),
        meta: { roles: ['super_admin'] }
      },
      {
        path: 'classrooms',
        name: 'Classrooms',
        component: () => import('@/views/Classrooms.vue')
      },
      {
        path: 'teachers',
        name: 'Teachers',
        component: () => import('@/views/Teachers.vue')
      },
      {
        path: 'students',
        name: 'Students',
        component: () => import('@/views/Students.vue')
      },
      {
        path: 'courses',
        name: 'Courses',
        component: () => import('@/views/Courses.vue')
      },
      {
        path: 'cycles',
        name: 'Cycles',
        component: () => import('@/views/Cycles.vue')
      },
      {
        path: 'schedule',
        name: 'Schedule',
        component: () => import('@/views/Schedule.vue')
      },
      {
        path: 'checkins',
        name: 'Checkins',
        component: () => import('@/views/Checkins.vue')
      },
      {
        path: 'users',
        name: 'Users',
        component: () => import('@/views/Users.vue')
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach((to, from, next) => {
  const userStore = useUserStore()

  if (to.meta.requiresAuth !== false && !userStore.isLoggedIn) {
    next('/login')
  } else if (to.meta.roles && !to.meta.roles.includes(userStore.user?.role)) {
    next('/')
  } else {
    next()
  }
})

export default router