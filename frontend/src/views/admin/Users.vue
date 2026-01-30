<template>
  <div class="user-management">
    <el-card>
      <template #header>
        <h3>👥 User Management</h3>
      </template>

      <el-table
        v-loading="loading"
        :data="users"
        style="width: 100%"
      >
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="email" label="Email" width="250" />
        <el-table-column prop="nickname" label="Nickname" width="150" />
        <el-table-column label="Role" width="120">
          <template #default="{ row }">
            <el-tag :type="row.role === 'admin' ? 'danger' : 'info'">
              {{ row.role }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="Status" width="120">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'danger'">
              {{ row.is_active ? 'Active' : 'Inactive' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="detection_count" label="Detections" width="120" />
        <el-table-column label="Created At" width="180">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="Actions" width="200">
          <template #default="{ row }">
            <el-button
              :type="row.is_active ? 'warning' : 'success'"
              size="small"
              @click="toggleUserStatus(row)"
            >
              {{ row.is_active ? 'Disable' : 'Enable' }}
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
        @current-change="loadUsers"
      />
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { adminAPI } from '@/api'
import { ElMessage, ElMessageBox } from 'element-plus'

const loading = ref(false)
const users = ref([])
const currentPage = ref(1)
const pageSize = ref(50)
const total = ref(0)

const loadUsers = async () => {
  loading.value = true
  try {
    const skip = (currentPage.value - 1) * pageSize.value
    const data = await adminAPI.getUsers(skip, pageSize.value)
    users.value = data
    total.value = data.length
  } catch (error) {
    ElMessage.error('Failed to load users')
  } finally {
    loading.value = false
  }
}

const toggleUserStatus = async (user) => {
  const action = user.is_active ? 'disable' : 'enable'

  try {
    await ElMessageBox.confirm(
      `Are you sure you want to ${action} user ${user.email}?`,
      'Confirm',
      {
        confirmButtonText: 'Yes',
        cancelButtonText: 'Cancel',
        type: 'warning'
      }
    )

    await adminAPI.toggleUserActive(user.id)
    ElMessage.success(`User ${action}d successfully`)
    loadUsers()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(`Failed to ${action} user`)
    }
  }
}

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleString()
}

onMounted(() => {
  loadUsers()
})
</script>

<style scoped>
.user-management {
  max-width: 1400px;
  margin: 0 auto;
}
</style>
