<template>
  <div class="admin-dashboard">
    <el-row :gutter="20">
      <el-col :span="6">
        <el-card class="stat-card">
          <el-statistic title="Today's Detections" :value="stats.today_detection_count">
            <template #prefix>
              <el-icon><Camera /></el-icon>
            </template>
          </el-statistic>
        </el-card>
      </el-col>

      <el-col :span="6">
        <el-card class="stat-card">
          <el-statistic title="Today's Fake Count" :value="stats.today_fake_count">
            <template #prefix>
              <el-icon color="red"><Warning /></el-icon>
            </template>
          </el-statistic>
        </el-card>
      </el-col>

      <el-col :span="6">
        <el-card class="stat-card">
          <el-statistic title="Today's Fake Ratio" :value="(stats.today_fake_ratio * 100).toFixed(2)" suffix="%">
            <template #prefix>
              <el-icon><PieChart /></el-icon>
            </template>
          </el-statistic>
        </el-card>
      </el-col>

      <el-col :span="6">
        <el-card class="stat-card">
          <el-statistic title="Total Users" :value="stats.total_users">
            <template #prefix>
              <el-icon><User /></el-icon>
            </template>
          </el-statistic>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :span="12">
        <el-card>
          <template #header>
            <h3>📊 Detection Statistics</h3>
          </template>
          <el-statistic title="Total Detections" :value="stats.total_detections" />
          <el-divider />
          <div class="progress-item">
            <span>Fake Detection Rate</span>
            <el-progress
              :percentage="Math.round(stats.today_fake_ratio * 100)"
              :color="getProgressColor(stats.today_fake_ratio)"
            />
          </div>
        </el-card>
      </el-col>

      <el-col :span="12">
        <el-card>
          <template #header>
            <h3>🎯 Quick Actions</h3>
          </template>
          <el-space direction="vertical" style="width: 100%">
            <el-button type="primary" style="width: 100%" @click="goToUsers">
              <el-icon><User /></el-icon>
              Manage Users
            </el-button>
            <el-button type="success" style="width: 100%" @click="goToAudit">
              <el-icon><Document /></el-icon>
              View Audit Logs
            </el-button>
            <el-button type="info" style="width: 100%" @click="refreshStats">
              <el-icon><Refresh /></el-icon>
              Refresh Statistics
            </el-button>
          </el-space>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :span="24">
        <el-card>
          <template #header>
            <h3>📈 System Overview</h3>
          </template>
          <el-descriptions :column="3" border>
            <el-descriptions-item label="Today's Detections">
              {{ stats.today_detection_count }}
            </el-descriptions-item>
            <el-descriptions-item label="Today's Fake Images">
              {{ stats.today_fake_count }}
            </el-descriptions-item>
            <el-descriptions-item label="Today's Real Images">
              {{ stats.today_detection_count - stats.today_fake_count }}
            </el-descriptions-item>
            <el-descriptions-item label="Total Users">
              {{ stats.total_users }}
            </el-descriptions-item>
            <el-descriptions-item label="Total Detections">
              {{ stats.total_detections }}
            </el-descriptions-item>
            <el-descriptions-item label="Fake Ratio">
              {{ (stats.today_fake_ratio * 100).toFixed(2) }}%
            </el-descriptions-item>
          </el-descriptions>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { adminAPI } from '@/api'
import { ElMessage } from 'element-plus'
import { Camera, Warning, PieChart, User, Document, Refresh } from '@element-plus/icons-vue'

const router = useRouter()

const stats = ref({
  today_detection_count: 0,
  today_fake_count: 0,
  today_fake_ratio: 0,
  total_users: 0,
  total_detections: 0
})

const loadStats = async () => {
  try {
    stats.value = await adminAPI.getDashboardStats()
  } catch (error) {
    ElMessage.error('Failed to load statistics')
  }
}

const getProgressColor = (ratio) => {
  if (ratio < 0.3) return '#67C23A'
  if (ratio < 0.6) return '#E6A23C'
  return '#F56C6C'
}

const goToUsers = () => {
  router.push('/admin/users')
}

const goToAudit = () => {
  router.push('/admin/audit')
}

const refreshStats = () => {
  loadStats()
  ElMessage.success('Statistics refreshed')
}

onMounted(() => {
  loadStats()
})
</script>

<style scoped>
.admin-dashboard {
  max-width: 1400px;
  margin: 0 auto;
}

.stat-card {
  text-align: center;
}

.progress-item {
  margin-top: 20px;
}

.progress-item span {
  display: block;
  margin-bottom: 10px;
  font-weight: 500;
}
</style>
