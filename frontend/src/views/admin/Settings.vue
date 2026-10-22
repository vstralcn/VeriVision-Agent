<template>
  <div class="settings-container">
    <el-card class="settings-card">
      <template #header>
        <div class="card-header">
          <span>{{ $t('settings.title') }}</span>
          <el-tag :type="form.enabled ? 'success' : 'info'" size="small">
            {{ form.enabled ? $t('settings.enabled') : $t('settings.disabled') }}
          </el-tag>
        </div>
      </template>

      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="160px"
        v-loading="loading"
      >
        <!-- Enable toggle -->
        <el-form-item :label="$t('settings.enableLLM')">
          <el-switch v-model="form.enabled" />
          <span class="field-hint">{{ $t('settings.enableHint') }}</span>
        </el-form-item>

        <el-divider />

        <!-- Provider -->
        <el-form-item :label="$t('settings.provider')" prop="provider">
          <el-radio-group v-model="form.provider" @change="onProviderChange">
            <el-radio-button value="openai">OpenAI / {{ $t('settings.compatible') }}</el-radio-button>
            <el-radio-button value="anthropic">Anthropic</el-radio-button>
          </el-radio-group>
        </el-form-item>

        <!-- API Base URL (OpenAI only) -->
        <el-form-item
          v-if="form.provider === 'openai'"
          :label="$t('settings.apiBaseUrl')"
          prop="api_base_url"
        >
          <el-input v-model="form.api_base_url" placeholder="https://api.openai.com/v1" style="width: 420px" />
          <div class="field-hint">{{ $t('settings.apiBaseUrlHint') }}</div>
          <div class="preset-list">
            <el-tag
              v-for="preset in urlPresets"
              :key="preset.url"
              class="preset-tag"
              size="small"
              @click="form.api_base_url = preset.url"
            >
              {{ preset.label }}
            </el-tag>
          </div>
        </el-form-item>

        <!-- API Key -->
        <el-form-item :label="$t('settings.apiKey')" prop="api_key">
          <el-input
            v-model="form.api_key"
            :type="showKey ? 'text' : 'password'"
            :placeholder="maskedKey || $t('settings.apiKeyPlaceholder')"
            style="width: 420px"
            autocomplete="new-password"
          >
            <template #suffix>
              <el-icon class="key-toggle" @click="showKey = !showKey">
                <View v-if="!showKey" />
                <Hide v-else />
              </el-icon>
            </template>
          </el-input>
          <div class="field-hint">{{ $t('settings.apiKeyHint') }}</div>
        </el-form-item>

        <!-- Model -->
        <el-form-item :label="$t('settings.model')" prop="model">
          <el-autocomplete
            v-model="form.model"
            :fetch-suggestions="queryModels"
            :placeholder="$t('settings.modelPlaceholder')"
            style="width: 300px"
          />
          <div class="preset-list">
            <el-tag
              v-for="m in modelPresets[form.provider] || []"
              :key="m"
              class="preset-tag"
              size="small"
              @click="form.model = m"
            >
              {{ m }}
            </el-tag>
          </div>
        </el-form-item>

        <el-divider />

        <!-- Max Tokens -->
        <el-form-item :label="$t('settings.maxTokens')">
          <el-slider
            v-model="form.max_tokens"
            :min="64"
            :max="4096"
            :step="64"
            show-input
            style="width: 380px"
          />
        </el-form-item>

        <!-- Temperature -->
        <el-form-item :label="$t('settings.temperature')">
          <el-slider
            v-model="form.temperature"
            :min="0"
            :max="2"
            :step="0.05"
            :precision="2"
            show-input
            style="width: 380px"
          />
        </el-form-item>

        <el-divider />

        <!-- Action buttons -->
        <el-form-item>
          <el-button type="primary" :loading="saving" @click="handleSave">
            {{ $t('common.save') }}
          </el-button>
          <el-button :loading="testing" @click="handleTest">
            {{ $t('settings.testConnection') }}
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- Test result -->
    <el-card v-if="testResult" class="test-result-card">
      <template #header>{{ $t('settings.testResult') }}</template>
      <el-alert
        :title="testResult.message"
        :type="testResult.success ? 'success' : 'error'"
        :description="testResult.response_preview || ''"
        show-icon
        :closable="false"
      />
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { View, Hide } from '@element-plus/icons-vue'
import { adminAPI } from '@/api/index'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

const loading = ref(false)
const saving = ref(false)
const testing = ref(false)
const showKey = ref(false)
const maskedKey = ref('')
const testResult = ref(null)
const formRef = ref(null)

const form = ref({
  provider: 'openai',
  api_base_url: 'https://api.openai.com/v1',
  api_key: '',
  model: 'gpt-4o-mini',
  enabled: false,
  max_tokens: 512,
  temperature: 0.3,
})

const rules = {
  provider: [{ required: true, message: t('settings.providerRequired'), trigger: 'change' }],
  model: [{ required: true, message: t('settings.modelRequired'), trigger: 'blur' }],
}

const urlPresets = [
  { label: 'OpenAI', url: 'https://api.openai.com/v1' },
  { label: 'Azure OpenAI', url: 'https://{resource}.openai.azure.com/openai/deployments/{deployment}' },
  { label: 'OpenRouter', url: 'https://openrouter.ai/api/v1' },
  { label: 'Groq', url: 'https://api.groq.com/openai/v1' },
  { label: 'Ollama', url: 'http://localhost:11434/v1' },
  { label: 'LM Studio', url: 'http://localhost:1234/v1' },
]

const modelPresets = {
  openai: ['gpt-4o', 'gpt-4o-mini', 'gpt-4-turbo', 'gpt-3.5-turbo'],
  anthropic: ['claude-opus-4-6', 'claude-sonnet-4-6', 'claude-haiku-4-5-20251001'],
}

const queryModels = (query, cb) => {
  const presets = modelPresets[form.value.provider] || []
  const results = query
    ? presets.filter(m => m.toLowerCase().includes(query.toLowerCase()))
    : presets
  cb(results.map(m => ({ value: m })))
}

const onProviderChange = (val) => {
  if (val === 'anthropic') {
    form.value.api_base_url = ''
    form.value.model = 'claude-haiku-4-5-20251001'
  } else {
    form.value.api_base_url = 'https://api.openai.com/v1'
    form.value.model = 'gpt-4o-mini'
  }
}

const loadConfig = async () => {
  loading.value = true
  try {
    const data = await adminAPI.getLLMConfig()
    form.value.provider = data.provider
    form.value.api_base_url = data.api_base_url
    form.value.model = data.model
    form.value.enabled = data.enabled
    form.value.max_tokens = data.max_tokens
    form.value.temperature = data.temperature
    maskedKey.value = data.api_key_masked
  } catch (e) {
    ElMessage.error(t('settings.loadFailed'))
  } finally {
    loading.value = false
  }
}

const handleSave = async () => {
  await formRef.value.validate()
  saving.value = true
  try {
    const payload = {
      provider: form.value.provider,
      api_base_url: form.value.api_base_url,
      model: form.value.model,
      enabled: form.value.enabled,
      max_tokens: form.value.max_tokens,
      temperature: form.value.temperature,
    }
    if (form.value.api_key) {
      payload.api_key = form.value.api_key
    }
    const data = await adminAPI.updateLLMConfig(payload)
    maskedKey.value = data.api_key_masked
    form.value.api_key = ''
    ElMessage.success(t('settings.saveSuccess'))
  } catch (e) {
    ElMessage.error(t('settings.saveFailed'))
  } finally {
    saving.value = false
  }
}

const handleTest = async () => {
  testing.value = true
  testResult.value = null
  try {
    testResult.value = await adminAPI.testLLMConfig()
    if (testResult.value.success) {
      ElMessage.success(t('settings.testSuccess'))
    } else {
      ElMessage.error(t('settings.testFailed'))
    }
  } catch (e) {
    testResult.value = { success: false, message: e.message || t('settings.testFailed') }
    ElMessage.error(t('settings.testFailed'))
  } finally {
    testing.value = false
  }
}

onMounted(loadConfig)
</script>

<style scoped>
.settings-container {
  max-width: 780px;
}

.settings-card {
  margin-bottom: 16px;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 12px;
  font-weight: 600;
  font-size: 15px;
}

.field-hint {
  color: #909399;
  font-size: 12px;
  margin-top: 4px;
  line-height: 1.4;
}

.preset-list {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-top: 6px;
}

.preset-tag {
  cursor: pointer;
}

.preset-tag:hover {
  opacity: 0.8;
}

.key-toggle {
  cursor: pointer;
  color: #909399;
}

.test-result-card {
  margin-top: 16px;
}
</style>
