<template>
  <div class="detection">
    <el-row :gutter="20">
      <!-- Upload Section -->
      <el-col :span="24" v-if="!detectionResult">
        <el-card>
          <template #header>
            <h3>{{ $t('detection.uploadTitle') }}</h3>
          </template>

          <el-upload
            class="upload-area"
            drag
            :auto-upload="false"
            :on-change="handleFileChange"
            :limit="1"
            accept="image/*"
          >
            <el-icon class="el-icon--upload"><upload-filled /></el-icon>
            <div class="el-upload__text">
              {{ $t('detection.dropOrClick') }}
            </div>
            <template #tip>
              <div class="el-upload__tip">
                {{ $t('detection.supportedFormats') }}
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
                {{ $t('dashboard.startDetection') }}
              </el-button>
              <el-button size="large" @click="resetUpload">{{ $t('common.cancel') }}</el-button>
            </div>
          </div>
        </el-card>
      </el-col>

      <!-- Detection Results -->
      <el-col :span="24" v-if="detectionResult">
        <el-card>
          <template #header>
            <div class="card-header">
              <h3>{{ $t('detection.resultsTitle') }}</h3>
              <el-button @click="resetUpload">{{ $t('detection.newDetection') }}</el-button>
            </div>
          </template>

          <el-row :gutter="20">
            <!-- Original & Heatmap -->
            <el-col :span="12">
              <h4>{{ $t('detection.originalImage') }}</h4>
              <div class="xray-box">
                <el-image
                  :src="getImageUrl(detectionResult.image_path)"
                  fit="contain"
                  style="width: 100%; height: 100%;"
                />
              </div>
            </el-col>
            <el-col :span="12">
              <h4>{{ $t('detection.heatmap') }}</h4>
              <div class="xray-box heatmap-box">
                <div class="scanner-line"></div>
                <el-image
                  :src="getImageUrl(detectionResult.heatmap_path)"
                  fit="contain"
                  style="width: 100%; height: 100%;"
                />
              </div>
            </el-col>
          </el-row>

          <!-- Analysis Report -->
          <el-divider />
          <h3>{{ $t('detection.analysisReport') }}</h3>

          <el-descriptions :column="2" border style="margin-top: 20px">
            <el-descriptions-item :label="$t('detection.verdict')">
              <el-tag
                :type="getVerdictType(detectionResult)"
                size="large"
                class="font-mono font-bold"
              >
                {{ detectionResult.analysis_report.verdict }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item :label="$t('detection.riskLevel')">
              <el-tag
                :type="getVerdictType(detectionResult)"
                size="large"
                class="font-mono font-bold"
              >
                {{ detectionResult.analysis_report.risk_level }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item :label="$t('detection.fakeProbability')">
              <span class="font-mono">{{ (detectionResult.fake_probability * 100).toFixed(2) }}%</span>
            </el-descriptions-item>
            <el-descriptions-item :label="$t('common.confidence')">
              <span class="font-mono">{{ (detectionResult.confidence * 100).toFixed(2) }}%</span>
            </el-descriptions-item>
          </el-descriptions>

          <el-card style="margin-top: 20px" shadow="never">
            <h4>{{ $t('detection.summary') }}</h4>
            <p>{{ detectionResult.analysis_report.summary }}</p>
          </el-card>

          <el-card style="margin-top: 20px" shadow="never">
            <h4>{{ $t('detection.detailedAnalysis') }}</h4>
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
            <h4>{{ $t('detection.recommendations') }}</h4>
            <ul>
              <li v-for="(rec, index) in detectionResult.analysis_report.recommendations" :key="index">
                {{ rec }}
              </li>
            </ul>
          </el-card>

          <!-- Trusted Certification -->
          <el-divider />
          <h3>{{ $t('detection.trustedCert') }}</h3>

          <el-card style="margin-top: 20px" class="cert-card">
            <el-descriptions :column="1" border>
              <el-descriptions-item :label="$t('common.certId')">
                <el-tag type="info" class="font-mono">{{ detectionResult.cert_id }}</el-tag>
              </el-descriptions-item>
              <el-descriptions-item :label="$t('detection.sha256')">
                <code class="font-mono" style="font-size: 12px">{{ detectionResult.sha256 }}</code>
              </el-descriptions-item>
              <el-descriptions-item :label="$t('detection.phash')">
                <code class="font-mono" style="font-size: 12px">{{ detectionResult.phash }}</code>
              </el-descriptions-item>
              <el-descriptions-item :label="$t('detection.signature')">
                <code class="font-mono" style="font-size: 12px; word-break: break-all">
                  {{ detectionResult.cert_signature }}
                </code>
              </el-descriptions-item>
            </el-descriptions>

            <div style="margin-top: 20px; text-align: center">
              <el-button
                type="success"
                :loading="verifying"
                @click="verifyCertification"
              >{{ $t('detection.verifyCert') }}</el-button>
              <el-button @click="viewTraceability">{{ $t('detection.viewTraceability') }}</el-button>
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

// "只有在检测出 Deepfake 且 Risk level 极高时 才大面积亮起"
const getVerdictType = (result) => {
  const { is_fake, analysis_report } = result
  if (is_fake && analysis_report.risk_level === 'High') {
    return 'danger'
  }
  if (!is_fake) {
    return 'success'
  }
  return 'warning'
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

/* Hardcore Upload Area */
:deep(.el-upload-dragger) {
  border: 1px dashed var(--el-border-color-light);
  background: var(--el-bg-color-page);
  border-radius: 4px;
  transition: all 0.3s;
}
:deep(.el-upload-dragger:hover) {
  border-color: var(--el-color-primary);
  background: var(--el-bg-color);
}

.upload-area {
  text-align: center;
}

/* X-ray style image viewer */
.xray-box {
  background: #000;
  border-radius: 4px;
  min-height: 300px;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
  border: 1px solid #333;
}

/* Heatmap with Scanner Line */
.heatmap-box {
  position: relative;
}
.scanner-line {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 2px;
  background: rgba(0, 255, 255, 0.6);
  box-shadow: 0 0 10px rgba(0, 255, 255, 0.8), 0 0 20px rgba(0, 255, 255, 0.4);
  animation: scan 3s linear infinite;
  z-index: 10;
}

@keyframes scan {
  0% { top: 0; opacity: 0; }
  10% { opacity: 1; }
  90% { opacity: 1; }
  100% { top: 100%; opacity: 0; }
}

.analysis-item {
  margin-bottom: 20px;
}

.analysis-item span {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: #4B5563;
}

.cert-card {
  background: #FFFFFF;
}

code {
  background: #F5F7FA;
  padding: 4px 8px;
  border-radius: 4px;
  color: #1F2937;
  border: 1px solid var(--el-border-color-light);
}

.font-bold {
  font-weight: bold;
}
</style>
