<template>
  <el-image v-bind="$attrs" :src="sourceUrl">
    <template #placeholder>
      <div class="media-state">Loading...</div>
    </template>
    <template #error>
      <div class="media-state">Unavailable</div>
    </template>
  </el-image>
</template>

<script setup>
import { onBeforeUnmount, ref, watch } from 'vue'
import { detectionAPI } from '@/api'

defineOptions({ inheritAttrs: false })

const props = defineProps({
  detectionId: {
    type: Number,
    required: true
  },
  kind: {
    type: String,
    default: 'image',
    validator: value => ['image', 'heatmap'].includes(value)
  }
})

const sourceUrl = ref('')
let objectUrl = ''

const releaseObjectUrl = () => {
  if (objectUrl) {
    URL.revokeObjectURL(objectUrl)
    objectUrl = ''
  }
}

const loadImage = async () => {
  releaseObjectUrl()
  sourceUrl.value = ''
  try {
    const blob = await detectionAPI.getMedia(props.detectionId, props.kind)
    objectUrl = URL.createObjectURL(blob)
    sourceUrl.value = objectUrl
  } catch {
    sourceUrl.value = ''
  }
}

watch(
  () => [props.detectionId, props.kind],
  loadImage,
  { immediate: true }
)

onBeforeUnmount(releaseObjectUrl)
</script>

<style scoped>
.media-state {
  display: grid;
  width: 100%;
  height: 100%;
  min-height: 48px;
  place-items: center;
  color: #909399;
  font-size: 12px;
  background: #f5f7fa;
}
</style>
