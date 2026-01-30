<template>
  <div class="detection">
    <el-row :gutter="20">
      <!-- Upload Section -->
      <el-col :span="24" v-if="!detectionResult">
        <el-card>
          <template #header>
            <h3>Upload Image for Detection</h3>
          </template>

          <el-upload
            class="upload-demo"
            drag
            :auto-upload="false"
            :on-change="handleFileChange"
            :limit="1"
            accept="image/*"
          >
            <el-icon class="el-icon--upload"><upload-filled /></el-icon>
            <div class="el-upload__text">
              Drop image here or <em>click to upload</em>
            </div>
            <template #tip>
              <div class="el-upload__tip">
                Supported formats: JPG, PNG, GIF (Max 10MB)
              </div>
            </template>
          </el-upload>

          <div v-if="selectedFile" style="margin-top: 20px; text-align: center">
            <el-image
              :src="previewUrl"
              fit="contain"
              style="max-width: 400px; max-height: 400px; border-radius: 8px"
            />
            <div style="margin-top: 20px">
              <el-button
                type="primary"
                size="large"
                :loading="detecting"
                @click="startDetection"
              >
                Start Detection
              </el-button>
              <el-button size="large" @click="resetUpload">
                Cancel
              </el-button>
            </div>
          </div>
        </el-card>
      </el-col>

      <!-- Detection Results -->
      <el-col :span="24" v-if="detectionResult">
        <el-card>
          <template #header>
            <div class="card-header">
              <h3>Detection Results</h3>
              <el-button @click="resetUpload">New Detection</el-button>
            </div>
          </template>

          <el-row :gutter="20">
            <!-- Original & Heatmap -->
            <el-col :span="12">
              <h4>Original Image</h4>
              <el-image
                :src="getImageUrl(detectionResult.image_path)"
                fit="contain"
                style="width: 100%; border-radius: 8px"
              />
            </el-col>
            <el-col :span="12">
              <h4>Detection Heatmap</h4>
              <el-image
                :src="getImageUrl(detectionResult.heatmap_path)"
                fit="contain"
                style="width: 100%; border-radius: 8px"
              />
            </el-col>
          </el-row>

          <!-- Analysis Report -->
          <el-divider />
          <h3>📊 Intelligent Analysis Report</h3>

          <el-descriptions :column="2" border style="margin-top: 20px">
            <el-descriptions-item label="Verdict">
              <el-tag
                :type="detectionResult.is_fake ? 'danger' : 'success'"
                size="large"
              >
                {{ detectionResult.analysis_report.verdict }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="Risk Level">
              <el-tag
                :type="getRiskLevelType(detectionResult.analysis_report.risk_level)"
                size="large"
              >
                {{ detectionResult.analysis_report.risk_level }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="Fake Probability">
              {{ (detectionResult.fake_probability * 100).toFixed(2) }}%
            </el-descriptions-item>
            <el-descriptions-item label="Confidence">
              {{ (detectionResult.confidence * 100).toFixed(2) }}%
            </el-descriptions-item>
          </el-descriptions>

          <el-card style="margin-top: 20px" shadow="never">
            <h4>Summary</h4>
            <p>{{ detectionResult.analysis_report.summary }}</p>
          </el-card>

          <el-card style="margin-top: 20px" shadow="never">
            <h4>Detailed Analysis</h4>
            <el-row :gutter="20">
              <el-col :span="12" v-for="(value, key) in detectionResult.analysis_report.analysis" :key="key">
                <div class="analysis-item">
                  <span>{{ formatAnalysisKey(key) }}</span>
                  <el-progress
                    :percentage="Math.round(value * 100)"
                    :color="getProgressColor(value)"
                  />
                </div>
              </el-col>
            </el-row>
          </el-card>

          <el-card style="margin-top: 20px" shadow="never">
            <h4>Recommendations</h4>
            <ul>
              <li v-for="(rec, index) in detectionResult.analysis_report.recommendations" :key="index">
                {{ rec }}
              </li>
            </ul>
          </el-card>

          <!-- Trusted Certification -->
          <el-divider />
          <h3>🔐 Trusted Certification</h3>

          <el-card style="margin-top: 20px" class="cert-card">
            <el-descriptions :column="1" border>
              <el-descriptions-item label="Certification ID">
                <el-tag type="info">{{ detectionResult.cert_id }}</el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="SHA256 Hash">
                <code style="font-size: 12px">{{ detectionResult.sha256 }}</code>
              </el-descriptions-item>
              <el-descriptions-item label="Perceptual Hash">
                <code style="font-size: 12px">{{ detectionResult.phash }}</code>
              </el-descriptions-item>
              <el-descriptions-item label="Signature">
                <code style="font-size: 12px; word-break: break-all">
                  {{ detectionResult.cert_signature }}
                </code>
              </el-descriptions-item>
            </el-descriptions>

            <div style="margin-top: 20px; text-align: center">
              <el-button
                type="success"
                :loading="verifying"
                @click="verifyCertification"
              >
                Verify Certification
              </el-button>
              <el-button @click="viewTraceability">
                View Traceability
              </el-button>
            </div>
          </el-card>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { detectionAPI } from '@/api'
import { ElMessage } from 'element-plus'
import { UploadFilled } from '@element-plus/icons-vue'

const router = useRouter()

const selectedFile = ref(null)
const previewUrl = ref('')
const detecting = ref(false)
const verifying = ref(false)
const detectionResult = ref(null)

const handleFileChange = (file) => {
  selectedFile.value = file.raw
  previewUrl.value = URL.createObjectURL(file.raw)
}

const startDetection = async () => {
  if (!selectedFile.value) {
    ElMessage.warning('Please select an image first')
    return
  }

  detecting.value = true
  try {
    const result = await detectionAPI.uploadAndDetect(selectedFile.value)
    detectionResult.value = result
    ElMessage.success('Detection completed successfully')
  } catch (error) {
    ElMessage.error('Detection failed')
  } finally {
    detecting.value = false
  }
}

const resetUpload = () => {
  selectedFile.value = null
  previewUrl.value = ''
  detectionResult.value = null
}

const getImageUrl = (path) => {
  return detectionAPI.getImageUrl(path)
}

const getRiskLevelType = (level) => {
  const types = {
    'Low': 'success',
    'Medium': 'warning',
    'High': 'danger'
  }
  return types[level] || 'info'
}

const getProgressColor = (value) => {
  if (value < 0.3) return '#67C23A'
  if (value < 0.6) return '#E6A23C'
  return '#F56C6C'
}

const formatAnalysisKey = (key) => {
  return key.split('_').map(word =>
    word.charAt(0).toUpperCase() + word.slice(1)
  ).join(' ')
}

const verifyCertification = async () => {
  verifying.value = true
  try {
    const result = await detectionAPI.verifyCertification(detectionResult.value.id)
    if (result.is_valid) {
      ElMessage.success('Certification verified successfully')
    } else {
      ElMessage.error('Certification verification failed')
    }
  } catch (error) {
    ElMessage.error('Verification failed')
  } finally {
    verifying.value = false
  }
}

const viewTraceability = () => {
  router.push(`/traceability/${detectionResult.value.id}`)
}
</script>

<style scoped>
.detection {
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

.upload-demo {
  text-align: center;
}

.analysis-item {
  margin-bottom: 20px;
}

.analysis-item span {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
}

.cert-card {
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
}

code {
  background: #f4f4f5;
  padding: 2px 6px;
  border-radius: 4px;
}
</style>
