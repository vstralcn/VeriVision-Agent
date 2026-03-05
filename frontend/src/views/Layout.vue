<template>
  <el-container class="layout-container">
    <el-aside width="200px">
      <div class="logo">
        <h3>🔍 {{ $t('login.title') }}</h3>
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
          <span>{{ $t('menu.dashboard') }}</span>
        </el-menu-item>
        <el-menu-item index="/detection">
          <el-icon><Camera /></el-icon>
          <span>{{ $t('menu.detection') }}</span>
        </el-menu-item>
        <el-menu-item index="/traceability">
          <el-icon><Connection /></el-icon>
          <span>{{ $t('menu.traceability') }}</span>
        </el-menu-item>
        <el-menu-item index="/profile">
          <el-icon><User /></el-icon>
          <span>{{ $t('menu.profile') }}</span>
        </el-menu-item>
        <el-menu-item v-if="authStore.isAdmin" index="/admin">
          <el-icon><Setting /></el-icon>
          <span>{{ $t('menu.adminPanel') }}</span>
        </el-menu-item>
      </el-menu>
    </el-aside>

    <el-container>
      <el-header>
        <div class="header-content">
          <span class="welcome">{{ $t('common.welcome') }}, {{ authStore.user?.nickname || authStore.user?.email }}</span>
          <div class="header-right">
            <el-dropdown @command="handleLanguageChange" class="lang-dropdown">
              <span class="el-dropdown-link">
                {{ currentLang }}
                <el-icon class="el-icon--right"><arrow-down /></el-icon>
              </span>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="zh">中文</el-dropdown-item>
                  <el-dropdown-item command="en">English</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
            <el-button type="danger" @click="handleLogout">{{ $t('common.logout') }}</el-button>
          </div>
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
import { useI18n } from 'vue-i18n'
import { ElMessageBox } from 'element-plus'
import { HomeFilled, Camera, Connection, User, Setting, ArrowDown } from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const { t, locale } = useI18n()

const activeMenu = computed(() => route.path)
const currentLang = computed(() => locale.value === 'zh' ? '中文' : 'English')

const handleLanguageChange = (lang) => {
  locale.value = lang
  localStorage.setItem('locale', lang)
}

const handleLogout = async () => {
  await ElMessageBox.confirm(t('common.logoutConfirm'), t('common.confirm'), {
    confirmButtonText: t('common.yes'),
    cancelButtonText: t('common.cancel'),
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
  text-align: center;
  padding: 0 10px;
  line-height: 1.2;
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

.header-right {
  display: flex;
  align-items: center;
  gap: 20px;
}

.lang-dropdown {
  cursor: pointer;
  color: #606266;
  display: flex;
  align-items: center;
}

.el-dropdown-link {
  display: flex;
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
