<template>
  <div class="audit-logs">
    <el-card>
      <template #header>
        <h3>📋 Audit Logs</h3>
      </template>

      <!-- Filters -->
      <el-form :inline="true" :model="filters" class="filter-form">
        <el-form-item label="Action">
          <el-select v-model="filters.action" placeholder="All Actions" clearable style="width: 150px">
            <el-option label="Login" value="login" />
            <el-option label="Detection" value="detection" />
            <el-option label="Admin Action" value="admin_action" />
            <el-option label="Register" value="register" />
          </el-select>
        </el-form-item>

        <el-form-item label="Status">
          <el-select v-model="filters.success" placeholder="All Status" clearable style="width: 150px">
            <el-option label="Success" :value="true" />
            <el-option label="Failed" :value="false" />
          </el-select>
        </el-form-item>

        <el-form-item label="Date Range">
          <el-date-picker
            v-model="dateRange"
            type="datetimerange"
            range-separator="To"
            start-placeholder="Start date"
            end-placeholder="End date"
            style="width: 350px"
          />
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="loadAuditLogs">Search</el-button>
          <el-button @click="resetFilters">Reset</el-button>
        </el-form-item>
      </el-form>

      <!-- Audit Logs Table -->
      <el-table
        v-loading="loading"
        :data="auditLogs"
        style="width: 100%"
      >
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="user_id" label="User ID" width="100" />
        <el-table-column label="Action" width="150">
          <template #default="{ row }">
            <el-tag :type="getActionType(row.action)">
              {{ row.action }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="resource" label="Resource" width="200" />
        <el-table-column label="Status" width="100">
          <template #default="{ row }">
            <el-tag :type="row.success ? 'success' : 'danger'">
              {{ row.success ? 'Success' : 'Failed' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="ip_address" label="IP Address" width="150" />
        <el-table-column label="Created At" width="180">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="Actions" width="150">
          <template #default="{ row }">
            <el-button size="small" @click="viewDetail(row)">
              View Detail
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        v-model:current-page="currentPage"
        :page-size="pageSize"
        :total="total"
        layout="total, prev, pager, next"
        style="margin-top: 20px; text-align: right"
        @current-change="loadAuditLogs"
      />
    </el-card>

    <!-- Detail Dialog -->
    <el-dialog v-model="detailDialogVisible" title="Audit Log Detail" width="600px">
      <el-descriptions :column="1" border v-if="selectedLog">
        <el-descriptions-item label="ID">{{ selectedLog.id }}</el-descriptions-item>
        <el-descriptions-item label="User ID">{{ selectedLog.user_id || 'N/A' }}</el-descriptions-item>
        <el-descriptions-item label="Action">
          <el-tag :type="getActionType(selectedLog.action)">
            {{ selectedLog.action }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="Resource">{{ selectedLog.resource || 'N/A' }}</el-descriptions-item>
        <el-descriptions-item label="Status">
          <el-tag :type="selectedLog.success ? 'success' : 'danger'">
            {{ selectedLog.success ? 'Success' : 'Failed' }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="IP Address">{{ selectedLog.ip_address || 'N/A' }}</el-descriptions-item>
        <el-descriptions-item label="User Agent">{{ selectedLog.user_agent || 'N/A' }}</el-descriptions-item>
        <el-descriptions-item label="Created At">{{ formatDate(selectedLog.created_at) }}</el-descriptions-item>
        <el-descriptions-item label="Detail">
          <pre style="max-height: 300px; overflow: auto; background: #f5f5f5; padding: 10px; border-radius: 4px">{{ JSON.stringify(selectedLog.detail, null, 2) }}</pre>
        </el-descriptions-item>
      </el-descriptions>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { adminAPI } from '@/api'
import { ElMessage } from 'element-plus'

const loading = ref(false)
const auditLogs = ref([])
const currentPage = ref(1)
const pageSize = ref(50)
const total = ref(0)

const filters = reactive({
  action: null,
  success: null
})

const dateRange = ref(null)

const detailDialogVisible = ref(false)
const selectedLog = ref(null)

const loadAuditLogs = async () => {
  loading.value = true
  try {
    const skip = (currentPage.value - 1) * pageSize.value
    const params = {
      skip,
      limit: pageSize.value
    }

    if (filters.action) {
      params.action = filters.action
    }

    if (filters.success !== null) {
      params.success = filters.success
    }

    if (dateRange.value && dateRange.value.length === 2) {
      params.start_date = dateRange.value[0].toISOString()
      params.end_date = dateRange.value[1].toISOString()
    }

    const data = await adminAPI.getAuditLogs(params)
    auditLogs.value = data
    total.value = data.length
  } catch (error) {
    ElMessage.error('Failed to load audit logs')
  } finally {
    loading.value = false
  }
}

const resetFilters = () => {
  filters.action = null
  filters.success = null
  dateRange.value = null
  currentPage.value = 1
  loadAuditLogs()
}

const viewDetail = async (log) => {
  try {
    selectedLog.value = await adminAPI.getAuditLogDetail(log.id)
    detailDialogVisible.value = true
  } catch (error) {
    ElMessage.error('Failed to load audit log detail')
  }
}

const getActionType = (action) => {
  const types = {
    'login': 'primary',
    'detection': 'success',
    'admin_action': 'warning',
    'register': 'info'
  }
  return types[action] || 'info'
}

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleString()
}

onMounted(() => {
  loadAuditLogs()
})
</script>

<style scoped>
.audit-logs {
  max-width: 1400px;
  margin: 0 auto;
}

.filter-form {
  margin-bottom: 20px;
}

pre {
  font-family: 'Courier New', monospace;
  font-size: 12px;
}
</style>
