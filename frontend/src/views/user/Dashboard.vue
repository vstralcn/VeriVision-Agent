<template>
  <div class="dashboard">
    <el-row :gutter="20">
      <el-col :span="24">
        <el-card class="welcome-card">
          <h2>🔍 Deepfake Detection Platform</h2>
          <p>{{ $t('dashboard.subtitle') }}</p>
          <el-button type="primary" size="large" @click="goToDetection">
            {{ $t('dashboard.startDetection') }}
          </el-button>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :span="24">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>{{ $t('dashboard.recentDetections') }}</span>
              <el-button text @click="goToDetection">{{ $t('dashboard.viewAll') }}</el-button>
            </div>
          </template>

          <el-table
            v-loading="loading"
            :data="recentDetections"
            style="width: 100%"
          >
            <el-table-column prop="id" label="ID" width="80" />
            <el-table-column :label="$t('common.image')" width="100">
              <template #default="{ row }">
                <el-image
                  :src="getImageUrl(row.image_path)"
                  fit="cover"
                  style="width: 60px; height: 60px; border-radius: 4px"
                />
              </template>
            </el-table-column>
            <el-table-column :label="$t('common.result')" width="120">
              <template #default="{ row }">
                <el-tag :type="row.is_fake ? 'danger' : 'success'">
                  {{ row.is_fake ? $t('common.fake') : $t('common.real') }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column :label="$t('common.confidence')" width="150">
              <template #default="{ row }">
                <el-progress
                  :percentage="Math.round(row.confidence * 100)"
                  :color="row.is_fake ? '#F56C6C' : '#67C23A'"
                />
              </template>
            </el-table-column>
            <el-table-column :label="$t('common.certId')" prop="cert_id" />
            <el-table-column :label="$t('common.date')" width="180">
              <template #default="{ row }">
                {{ formatDate(row.created_at) }}
              </template>
            </el-table-column>
            <el-table-column :label="$t('common.actions')" width="150">
              <template #default="{ row }">
                <el-button
                  size="small"
                  @click="viewTraceability(row.id)"
                >
                  {{ $t('common.viewDetails') }}
                </el-button>
              </template>
            </el-table-column>
          </el-table>

          <el-empty v-if="!loading && recentDetections.length === 0" :description="$t('dashboard.noDetections')" />
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { detectionAPI } from '@/api'
import { ElMessage } from 'element-plus'

const router = useRouter()
const loading = ref(false)
const recentDetections = ref([])

const fetchRecentDetections = async () => {
  loading.value = true
  try {
    recentDetections.value = await detectionAPI.getRecent(5)
  } catch (error) {
    ElMessage.error('Failed to load recent detections')
  } finally {
    loading.value = false
  }
}

const getImageUrl = (path) => {
  return detectionAPI.getImageUrl(path)
}

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleString()
}

const goToDetection = () => {
  router.push('/detection')
}

const viewTraceability = (id) => {
  router.push(`/traceability/${id}`)
}

onMounted(() => {
  fetchRecentDetections()
})
</script>

<style scoped>
.dashboard {
  max-width: 1400px;
  margin: 0 auto;
}

.welcome-card {
  text-align: center;
  padding: 40px 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.welcome-card h2 {
  margin: 0 0 10px 0;
  font-size: 32px;
}

.welcome-card p {
  margin: 0 0 30px 0;
  font-size: 16px;
  opacity: 0.9;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
