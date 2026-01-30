<template>
  <div class="traceability">
    <el-card>
      <template #header>
        <h3>🔍 Image Traceability Archive</h3>
      </template>

      <!-- Detection Selector -->
      <el-form :inline="true" v-if="!detectionId">
        <el-form-item label="Select Detection">
          <el-select
            v-model="selectedDetectionId"
            placeholder="Choose a detection"
            style="width: 300px"
            @change="loadDetection"
          >
            <el-option
              v-for="detection in detectionList"
              :key="detection.id"
              :label="`ID: ${detection.id} - ${detection.cert_id}`"
              :value="detection.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadDetection">Load</el-button>
        </el-form-item>
      </el-form>

      <!-- Detection Details -->
      <div v-if="detection" v-loading="loading">
        <el-row :gutter="20">
          <el-col :span="12">
            <h4>Image</h4>
            <el-image
              :src="getImageUrl(detection.image_path)"
              fit="contain"
              style="width: 100%; border-radius: 8px"
            />
          </el-col>
          <el-col :span="12">
            <h4>Detection Information</h4>
            <el-descriptions :column="1" border>
              <el-descriptions-item label="Detection ID">
                {{ detection.id }}
              </el-descriptions-item>
              <el-descriptions-item label="Result">
                <el-tag :type="detection.is_fake ? 'danger' : 'success'">
                  {{ detection.is_fake ? 'Fake' : 'Real' }}
                </el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="Confidence">
                {{ (detection.confidence * 100).toFixed(2) }}%
              </el-descriptions-item>
              <el-descriptions-item label="Certification ID">
                <el-tag type="info">{{ detection.cert_id }}</el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="SHA256">
                <code style="font-size: 11px; word-break: break-all">
                  {{ detection.sha256 }}
                </code>
              </el-descriptions-item>
              <el-descriptions-item label="pHash">
                <code style="font-size: 11px">{{ detection.phash }}</code>
              </el-descriptions-item>
              <el-descriptions-item label="Created At">
                {{ formatDate(detection.created_at) }}
              </el-descriptions-item>
            </el-descriptions>
          </el-col>
        </el-row>

        <!-- Trace Timeline -->
        <el-divider />
        <h3>📜 Fingerprint Record Timeline</h3>

        <el-timeline style="margin-top: 20px">
          <el-timeline-item
            v-for="record in traceRecords"
            :key="record.id"
            :timestamp="formatDate(record.created_at)"
            placement="top"
            :type="getTimelineType(record.action)"
          >
            <el-card>
              <h4>{{ formatAction(record.action) }}</h4>
              <p>{{ record.description }}</p>
              <el-tag v-if="record.metadata" size="small" type="info">
                Metadata: {{ JSON.stringify(record.metadata) }}
              </el-tag>
            </el-card>
          </el-timeline-item>
        </el-timeline>

        <el-empty v-if="traceRecords.length === 0" description="No trace records found" />
      </div>

      <el-empty v-if="!detection && !loading" description="Select a detection to view traceability" />
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { detectionAPI } from '@/api'
import { ElMessage } from 'element-plus'

const route = useRoute()

const loading = ref(false)
const detectionId = ref(route.params.id ? parseInt(route.params.id) : null)
const selectedDetectionId = ref(detectionId.value)
const detection = ref(null)
const traceRecords = ref([])
const detectionList = ref([])

const loadDetectionList = async () => {
  try {
    detectionList.value = await detectionAPI.getHistory(0, 50)
  } catch (error) {
    ElMessage.error('Failed to load detection list')
  }
}

const loadDetection = async () => {
  if (!selectedDetectionId.value) {
    ElMessage.warning('Please select a detection')
    return
  }

  loading.value = true
  try {
    detection.value = await detectionAPI.getDetection(selectedDetectionId.value)
    traceRecords.value = await detectionAPI.getTraceRecords(selectedDetectionId.value)
  } catch (error) {
    ElMessage.error('Failed to load detection details')
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

const formatAction = (action) => {
  return action.charAt(0).toUpperCase() + action.slice(1)
}

const getTimelineType = (action) => {
  const types = {
    'uploaded': 'primary',
    'detected': 'success',
    'verified': 'warning'
  }
  return types[action] || 'info'
}

watch(() => route.params.id, (newId) => {
  if (newId) {
    detectionId.value = parseInt(newId)
    selectedDetectionId.value = detectionId.value
    loadDetection()
  }
})

onMounted(() => {
  loadDetectionList()
  if (detectionId.value) {
    loadDetection()
  }
})
</script>

<style scoped>
.traceability {
  max-width: 1400px;
  margin: 0 auto;
}

code {
  background: #f4f4f5;
  padding: 2px 6px;
  border-radius: 4px;
}
</style>
