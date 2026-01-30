<template>
  <el-container class="layout-container">
    <el-aside width="200px">
      <div class="logo">
        <h3>🔍 Deepfake Detector</h3>
      </div>
      <el-menu
        :default-active="activeMenu"
        router
        background-color="#304156"
        text-color="#bfcbd9"
        active-text-color="#409EFF"
      >
        <el-menu-item index="/">
          <el-icon><HomeFilled /></el-icon>
          <span>Dashboard</span>
        </el-menu-item>
        <el-menu-item index="/detection">
          <el-icon><Camera /></el-icon>
          <span>Detection</span>
        </el-menu-item>
        <el-menu-item index="/traceability">
          <el-icon><Connection /></el-icon>
          <span>Traceability</span>
        </el-menu-item>
        <el-menu-item index="/profile">
          <el-icon><User /></el-icon>
          <span>Profile</span>
        </el-menu-item>
        <el-menu-item v-if="authStore.isAdmin" index="/admin">
          <el-icon><Setting /></el-icon>
          <span>Admin Panel</span>
        </el-menu-item>
      </el-menu>
    </el-aside>

    <el-container>
      <el-header>
        <div class="header-content">
          <span class="welcome">Welcome, {{ authStore.user?.nickname || authStore.user?.email }}</span>
          <el-button type="danger" @click="handleLogout">Logout</el-button>
        </div>
      </el-header>

      <el-main>
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { ElMessageBox } from 'element-plus'
import { HomeFilled, Camera, Connection, User, Setting } from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const activeMenu = computed(() => route.path)

const handleLogout = async () => {
  await ElMessageBox.confirm('Are you sure you want to logout?', 'Confirm', {
    confirmButtonText: 'Yes',
    cancelButtonText: 'Cancel',
    type: 'warning'
  })

  authStore.logout()
  router.push('/login')
}
</script>

<style scoped>
.layout-container {
  min-height: 100vh;
}

.el-aside {
  background-color: #304156;
  color: #fff;
}

.logo {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #2b3a4a;
}

.logo h3 {
  margin: 0;
  color: #fff;
  font-size: 16px;
}

.el-header {
  background-color: #fff;
  box-shadow: 0 1px 4px rgba(0, 21, 41, 0.08);
  display: flex;
  align-items: center;
}

.header-content {
  width: 100%;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.welcome {
  font-size: 14px;
  color: #606266;
}

.el-main {
  background-color: #f0f2f5;
  padding: 20px;
}
</style>
