<template>
  <div class="login-container">
    <div class="lang-switcher">
      <el-dropdown @command="handleLanguageChange">
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
    </div>

    <el-card class="login-card">
      <template #header>
        <div class="card-header">
          <h2>{{ $t('login.title') }}</h2>
          <p>{{ $t('login.subtitle') }}</p>
        </div>
      </template>

      <el-form :model="form" :rules="rules" ref="formRef" label-width="0">
        <el-form-item prop="email">
          <el-input
            v-model="form.email"
            :placeholder="$t('login.email')"
            size="large"
            :prefix-icon="UserIcon"
          />
        </el-form-item>

        <el-form-item prop="password">
          <el-input
            v-model="form.password"
            type="password"
            :placeholder="$t('login.password')"
            size="large"
            :prefix-icon="LockIcon"
            @keyup.enter="handleLogin"
          />
        </el-form-item>

        <el-form-item>
          <el-button
            type="primary"
            size="large"
            style="width: 100%"
            :loading="loading"
            @click="handleLogin"
          >
            {{ $t('login.submit') }}
          </el-button>
        </el-form-item>
      </el-form>

      <el-divider>{{ $t('login.defaultAccounts') }}</el-divider>
      <div class="default-accounts">
        <el-tag type="success">{{ $t('login.admin') }}: admin@example.com / admin123</el-tag>
        <el-tag type="info">{{ $t('login.user') }}: user@example.com / user123</el-tag>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useI18n } from 'vue-i18n'
import { ElMessage } from 'element-plus'
import { User as UserIcon, Lock as LockIcon, ArrowDown } from '@element-plus/icons-vue'

const router = useRouter()
const authStore = useAuthStore()
const { t, locale } = useI18n()

const formRef = ref(null)
const loading = ref(false)

const form = reactive({
  email: '',
  password: ''
})

const currentLang = computed(() => locale.value === 'zh' ? '中文' : 'English')

const handleLanguageChange = (lang) => {
  locale.value = lang
  localStorage.setItem('locale', lang)
}

const rules = computed(() => ({
  email: [
    { required: true, message: t('login.emailRequired'), trigger: 'blur' },
    { type: 'email', message: t('login.emailInvalid'), trigger: 'blur' }
  ],
  password: [
    { required: true, message: t('login.passwordRequired'), trigger: 'blur' }
  ]
}))

const handleLogin = async () => {
  if (!formRef.value) return

  await formRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true
      try {
        const user = await authStore.login(form.email, form.password)
        ElMessage.success(t('login.loginSuccess'))

        // Redirect based on role
        if (user.role === 'admin') {
          router.push('/admin')
        } else {
          router.push('/')
        }
      } catch (error) {
        console.error('Login failed:', error)
      } finally {
        loading.value = false
      }
    }
  })
}
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  position: relative;
}

.lang-switcher {
  position: absolute;
  top: 20px;
  right: 20px;
}

.lang-switcher .el-dropdown-link {
  color: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  font-size: 14px;
}

.login-card {
  width: 400px;
}

.card-header {
  text-align: center;
}

.card-header h2 {
  margin: 0 0 10px 0;
  color: #303133;
}

.card-header p {
  margin: 0;
  color: #909399;
  font-size: 14px;
}

.default-accounts {
  display: flex;
  flex-direction: column;
  gap: 10px;
  font-size: 12px;
}
</style>
