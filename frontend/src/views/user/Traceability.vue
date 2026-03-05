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
            <h4>{{ $t('common.image') }}</h4>
            <div class="image-viewer">
              <el-image
                :src="getImageUrl(detection.image_path)"
                fit="contain"
                style="width: 100%; border-radius: 4px"
              />
            </div>
          </el-col>
          <el-col :span="12">
            <h4>Detection Information</h4>
            <el-descriptions :column="1" border>
              <el-descriptions-item label="Detection ID">
                <span class="font-mono">{{ detection.id }}</span>
              </el-descriptions-item>
              <el-descriptions-item :label="$t('common.result')">
                <el-tag :type="detection.is_fake ? 'danger' : 'success'">
                  {{ detection.is_fake ? $t('common.fake') : $t('common.real') }}
                </el-tag>
              </el-descriptions-item>
              <el-descriptions-item :label="$t('common.confidence')">
                <span class="font-mono">{{ (detection.confidence * 100).toFixed(2) }}%</span>
              </el-descriptions-item>
              <el-descriptions-item :label="$t('common.certId')">
                <el-tag type="info" class="font-mono">{{ detection.cert_id }}</el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="SHA256">
                <code class="font-mono" style="font-size: 11px; word-break: break-all">
                  {{ detection.sha256 }}
                </code>
              </el-descriptions-item>
              <el-descriptions-item label="pHash">
                <code class="font-mono" style="font-size: 11px">{{ detection.phash }}</code>
              </el-descriptions-item>
              <el-descriptions-item label="Created At">
                <span class="font-mono">{{ formatDate(detection.created_at) }}</span>
              </el-descriptions-item>
            </el-descriptions>
          </el-col>
        </el-row>

        <!-- Trace Timeline -->
        <el-divider />
        <h3>📜 Fingerprint Record Timeline</h3>

        <el-timeline style="margin-top: 20px" class="commit-timeline">
          <el-timeline-item
            v-for="record in traceRecords"
            :key="record.id"
            :timestamp="formatDate(record.created_at)"
            placement="top"
            :type="getTimelineType(record.action)"
            class="font-mono"
          >
            <el-card shadow="never" class="trace-card">
              <h4 class="action-title">{{ formatAction(record.action) }}</h4>
              <p class="record-desc">{{ record.description }}</p>
              
              <div v-if="record.metadata" class="metadata-section">
                <el-collapse v-model="activeCollapses" @change="handleChange">
                  <el-collapse-item title="View Cryptographic Signature / Metadata" :name="record.id">
                    <pre class="code-block font-mono">{{ JSON.stringify(record.metadata, null, 2) }}</pre>
                  </el-collapse-item>
                </el-collapse>
              </div>
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
const activeCollapses = ref([])

const handleChange = (val) => {
  // val is an array of active names
}

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
    'detected': 'danger', // making detection red or danger looks more hardcore
    'verified': 'success'
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

.image-viewer {
  background: #000;
  border-radius: 4px;
  min-height: 200px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 10px;
}

/* Timeline Customization */
.commit-timeline {
  padding-left: 10px;
}

.trace-card {
  border: 1px solid var(--el-border-color-light);
  background: var(--el-bg-color);
  margin-top: 10px;
}

.action-title {
  margin: 0 0 10px 0;
  color: #111827;
  font-weight: 600;
}

.record-desc {
  margin: 0 0 15px 0;
  color: #4B5563;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
}

.metadata-section {
  margin-top: 15px;
}

/* el-collapse overwrite */
:deep(.el-collapse) {
  border-top: none;
  border-bottom: none;
}
:deep(.el-collapse-item__header) {
  border-bottom: none;
  background-color: var(--el-bg-color-page);
  padding: 0 10px;
  border-radius: 4px;
  height: 36px;
  line-height: 36px;
  font-size: 13px;
  color: #4B5563;
}
:deep(.el-collapse-item__wrap) {
  border-bottom: none;
  background-color: transparent;
}
:deep(.el-collapse-item__content) {
  padding-bottom: 0;
}

/* Code Block */
.code-block {
  background: #1F2937;
  color: #E5E7EB;
  padding: 15px;
  border-radius: 4px;
  overflow-x: auto;
  margin-top: 8px;
  font-size: 12px;
  line-height: 1.5;
  border: 1px solid #374151;
}

code {
  background: #F5F7FA;
  padding: 2px 6px;
  border-radius: 4px;
  border: 1px solid var(--el-border-color-light);
}
</style>
