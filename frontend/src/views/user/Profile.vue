<template>
  <div class="profile">
    <el-row :gutter="20">
      <el-col :span="12">
        <el-card>
          <template #header>
            <h3>👤 Personal Information</h3>
          </template>

          <el-form :model="form" label-width="120px">
            <el-form-item label="Email">
              <el-input v-model="user.email" disabled />
            </el-form-item>

            <el-form-item label="Role">
              <el-tag :type="user.role === 'admin' ? 'danger' : 'info'">
                {{ user.role }}
              </el-tag>
            </el-form-item>

            <el-form-item label="Nickname">
              <el-input v-model="form.nickname" placeholder="Enter nickname" />
            </el-form-item>

            <el-form-item label="Account Status">
              <el-tag :type="user.is_active ? 'success' : 'danger'">
                {{ user.is_active ? 'Active' : 'Inactive' }}
              </el-tag>
            </el-form-item>

            <el-form-item label="Created At">
              <span>{{ formatDate(user.created_at) }}</span>
            </el-form-item>

            <el-form-item>
              <el-button type="primary" :loading="saving" @click="updateProfile">
                Save Changes
              </el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>

      <el-col :span="12">
        <el-card>
          <template #header>
            <h3>📊 Statistics</h3>
          </template>

          <el-statistic title="Total Detections" :value="stats.totalDetections" />
          <el-divider />
          <el-statistic title="Fake Images Detected" :value="stats.fakeCount" />
          <el-divider />
          <el-statistic title="Real Images" :value="stats.realCount" />
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :span="24">
        <el-card>
          <template #header>
            <div class="card-header">
              <h3>📜 Detection History</h3>
              <el-pagination
                v-model:current-page="currentPage"
                :page-size="pageSize"
                :total="total"
                layout="prev, pager, next"
                @current-change="loadHistory"
              />
            </div>
          </template>

          <el-table
            v-loading="loading"
            :data="history"
            style="width: 100%"
          >
            <el-table-column prop="id" label="ID" width="80" />
            <el-table-column label="Image" width="100">
              <template #default="{ row }">
                <el-image
                  :src="getImageUrl(row.image_path)"
                  fit="cover"
                  style="width: 60px; height: 60px; border-radius: 4px"
                />
              </template>
            </el-table-column>
            <el-table-column label="Result" width="120">
              <template #default="{ row }">
                <el-tag :type="row.is_fake ? 'danger' : 'success'">
                  {{ row.is_fake ? 'Fake' : 'Real' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="Confidence" width="150">
              <template #default="{ row }">
                <el-progress
                  :percentage="Math.round(row.confidence * 100)"
                  :color="row.is_fake ? '#F56C6C' : '#67C23A'"
                />
              </template>
            </el-table-column>
            <el-table-column label="Cert ID" prop="cert_id" />
            <el-table-column label="Date" width="180">
              <template #default="{ row }">
                {{ formatDate(row.created_at) }}
              </template>
            </el-table-column>
            <el-table-column label="Actions" width="150">
              <template #default="{ row }">
                <el-button
                  size="small"
                  @click="viewTraceability(row.id)"
                >
                  View Details
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { userAPI, detectionAPI } from '@/api'
import { ElMessage } from 'element-plus'

const router = useRouter()
const authStore = useAuthStore()

const user = computed(() => authStore.user)
const saving = ref(false)
const loading = ref(false)

const form = reactive({
  nickname: ''
})

const history = ref([])
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)

const stats = reactive({
  totalDetections: 0,
  fakeCount: 0,
  realCount: 0
})

const loadProfile = async () => {
  try {
    const profile = await userAPI.getProfile()
    form.nickname = profile.nickname || ''
  } catch (error) {
    ElMessage.error('Failed to load profile')
  }
}

const updateProfile = async () => {
  saving.value = true
  try {
    await userAPI.updateProfile({ nickname: form.nickname })
    await authStore.fetchUser()
    ElMessage.success('Profile updated successfully')
  } catch (error) {
    ElMessage.error('Failed to update profile')
  } finally {
    saving.value = false
  }
}

const loadHistory = async () => {
  loading.value = true
  try {
    const skip = (currentPage.value - 1) * pageSize.value
    const data = await detectionAPI.getHistory(skip, pageSize.value)
    history.value = data

    // Calculate stats
    stats.totalDetections = data.length
    stats.fakeCount = data.filter(d => d.is_fake).length
    stats.realCount = data.filter(d => !d.is_fake).length
    total.value = data.length
  } catch (error) {
    ElMessage.error('Failed to load history')
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

const viewTraceability = (id) => {
  router.push(`/traceability/${id}`)
}

onMounted(() => {
  loadProfile()
  loadHistory()
})
</script>

<style scoped>
.profile {
  max-width: 1400px;
  margin: 0 auto;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header h3 {
  margin: 0;
}
</style>
