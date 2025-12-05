<template>
  <div class="view-container">
    <div class="view-header">
      <h1>📋 Audit Logs</h1>
      <p class="view-subtitle">Track user sessions and API activity</p>
    </div>

    <!-- Filter Section -->
    <div class="card">
      <div class="card-header">
        <h2>🔍 Filters</h2>
        <button @click="toggleFilters" class="btn btn-secondary">
          {{ showFilters ? 'Hide Filters' : 'Show Filters' }}
        </button>
      </div>

      <div v-if="showFilters" class="card-body">
        <div class="form-grid">
          <div class="form-group">
            <label for="action">Action</label>
            <input
              id="action"
              v-model="filters.action"
              type="text"
              placeholder="e.g., LOGIN, UPLOAD_RECEIPT"
              class="form-control"
            />
          </div>

          <div class="form-group">
            <label for="username">Username</label>
            <input
              id="username"
              v-model="filters.username"
              type="text"
              placeholder="Filter by username"
              class="form-control"
            />
          </div>

          <div class="form-group">
            <label for="startDate">Start Date</label>
            <input
              id="startDate"
              v-model="filters.startDate"
              type="datetime-local"
              class="form-control"
            />
          </div>

          <div class="form-group">
            <label for="endDate">End Date</label>
            <input
              id="endDate"
              v-model="filters.endDate"
              type="datetime-local"
              class="form-control"
            />
          </div>

          <div class="form-group">
            <label for="success">Status</label>
            <select id="success" v-model="filters.success" class="form-control">
              <option value="">All</option>
              <option value="true">Success</option>
              <option value="false">Failed</option>
            </select>
          </div>

          <div class="form-group">
            <label for="limit">Results per page</label>
            <select id="limit" v-model.number="filters.limit" class="form-control">
              <option :value="25">25</option>
              <option :value="50">50</option>
              <option :value="100">100</option>
              <option :value="200">200</option>
            </select>
          </div>
        </div>

        <div class="button-group">
          <button @click="loadAuditLogs" class="btn btn-primary" :disabled="loading">
            {{ loading ? 'Loading...' : 'Apply Filters' }}
          </button>
          <button @click="clearFilters" class="btn btn-secondary">Clear Filters</button>
          <button @click="exportLogs('csv')" class="btn btn-accent" :disabled="loading">
            📥 Export CSV
          </button>
        </div>
      </div>
    </div>

    <!-- Statistics Cards -->
    <div class="stats-grid" v-if="statistics">
      <div class="stat-card">
        <div class="stat-icon">📊</div>
        <div class="stat-content">
          <div class="stat-value">{{ statistics.total_logs }}</div>
          <div class="stat-label">Total Logs</div>
        </div>
      </div>

      <div class="stat-card success">
        <div class="stat-icon">✅</div>
        <div class="stat-content">
          <div class="stat-value">{{ statistics.successful_actions }}</div>
          <div class="stat-label">Successful Actions</div>
        </div>
      </div>

      <div class="stat-card danger">
        <div class="stat-icon">❌</div>
        <div class="stat-content">
          <div class="stat-value">{{ statistics.failed_actions }}</div>
          <div class="stat-label">Failed Actions</div>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon">👥</div>
        <div class="stat-content">
          <div class="stat-value">{{ statistics.unique_users }}</div>
          <div class="stat-label">Unique Users</div>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon">📈</div>
        <div class="stat-content">
          <div class="stat-value">{{ statistics.success_rate.toFixed(2) }}%</div>
          <div class="stat-label">Success Rate</div>
        </div>
      </div>
    </div>

    <!-- Error Message -->
    <div v-if="errorMessage" class="alert alert-danger">
      {{ errorMessage }}
    </div>

    <!-- Loading State -->
    <div v-if="loading && !logs.length" class="loading-container">
      <div class="spinner"></div>
      <p>Loading audit logs...</p>
    </div>

    <!-- Audit Logs Table -->
    <div v-else-if="logs.length" class="card">
      <div class="card-header">
        <h2>📝 Audit Log Entries</h2>
        <span class="badge">{{ logs.length }} logs</span>
      </div>

      <div class="table-responsive">
        <table class="table">
          <thead>
            <tr>
              <th>Timestamp</th>
              <th>User</th>
              <th>Action</th>
              <th>Resource</th>
              <th>Status</th>
              <th>IP Address</th>
              <th>Details</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="log in logs" :key="log.id" :class="{ 'row-error': !log.success }">
              <td class="timestamp">{{ formatTimestamp(log.timestamp) }}</td>
              <td>
                <div class="user-info">
                  <strong>{{ log.username || 'N/A' }}</strong>
                  <span class="user-role" v-if="log.user_role">{{ log.user_role }}</span>
                </div>
              </td>
              <td>
                <span class="action-badge" :class="getActionClass(log.action)">
                  {{ log.action }}
                </span>
              </td>
              <td>
                <div v-if="log.resource_type" class="resource-info">
                  <div>{{ log.resource_type }}</div>
                  <small v-if="log.resource_id">#{{ log.resource_id }}</small>
                </div>
                <span v-else class="text-muted">—</span>
              </td>
              <td>
                <span :class="log.success ? 'badge-success' : 'badge-danger'">
                  {{ log.success ? '✓ Success' : '✗ Failed' }}
                </span>
                <div v-if="log.status_code" class="status-code">{{ log.status_code }}</div>
              </td>
              <td class="ip-address">{{ log.ip_address || 'N/A' }}</td>
              <td>
                <button @click="viewDetails(log)" class="btn-link">
                  View Details
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Pagination -->
      <div class="pagination" v-if="logs.length === filters.limit">
        <button
          @click="loadMoreLogs"
          class="btn btn-secondary"
          :disabled="loading"
        >
          Load More
        </button>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else class="empty-state">
      <div class="empty-icon">📭</div>
      <h3>No audit logs found</h3>
      <p>Try adjusting your filters or check back later.</p>
    </div>

    <!-- Details Modal -->
    <div v-if="selectedLog" class="modal-overlay" @click.self="closeDetails">
      <div class="modal-content">
        <div class="modal-header">
          <h2>Log Details</h2>
          <button @click="closeDetails" class="modal-close">✕</button>
        </div>

        <div class="modal-body">
          <div class="detail-grid">
            <div class="detail-item">
              <label>ID</label>
              <span>{{ selectedLog.id }}</span>
            </div>
            <div class="detail-item">
              <label>Timestamp</label>
              <span>{{ formatTimestamp(selectedLog.timestamp) }}</span>
            </div>
            <div class="detail-item">
              <label>User ID</label>
              <span>{{ selectedLog.user_id || 'N/A' }}</span>
            </div>
            <div class="detail-item">
              <label>Username</label>
              <span>{{ selectedLog.username || 'N/A' }}</span>
            </div>
            <div class="detail-item">
              <label>Role</label>
              <span>{{ selectedLog.user_role || 'N/A' }}</span>
            </div>
            <div class="detail-item">
              <label>Action</label>
              <span>{{ selectedLog.action }}</span>
            </div>
            <div class="detail-item">
              <label>Resource Type</label>
              <span>{{ selectedLog.resource_type || 'N/A' }}</span>
            </div>
            <div class="detail-item">
              <label>Resource ID</label>
              <span>{{ selectedLog.resource_id || 'N/A' }}</span>
            </div>
            <div class="detail-item">
              <label>Method</label>
              <span>{{ selectedLog.method || 'N/A' }}</span>
            </div>
            <div class="detail-item">
              <label>Endpoint</label>
              <span class="monospace">{{ selectedLog.endpoint || 'N/A' }}</span>
            </div>
            <div class="detail-item">
              <label>IP Address</label>
              <span>{{ selectedLog.ip_address || 'N/A' }}</span>
            </div>
            <div class="detail-item">
              <label>Status Code</label>
              <span>{{ selectedLog.status_code || 'N/A' }}</span>
            </div>
            <div class="detail-item">
              <label>Success</label>
              <span :class="selectedLog.success ? 'text-success' : 'text-danger'">
                {{ selectedLog.success ? '✓ Yes' : '✗ No' }}
              </span>
            </div>
            <div class="detail-item">
              <label>Session ID</label>
              <span class="monospace small">{{ selectedLog.session_id || 'N/A' }}</span>
            </div>
          </div>

          <div v-if="selectedLog.error_message" class="detail-section">
            <label>Error Message</label>
            <pre class="error-message">{{ selectedLog.error_message }}</pre>
          </div>

          <div v-if="selectedLog.user_agent" class="detail-section">
            <label>User Agent</label>
            <pre class="user-agent">{{ selectedLog.user_agent }}</pre>
          </div>

          <div v-if="selectedLog.metadata" class="detail-section">
            <label>Metadata</label>
            <pre class="metadata">{{ JSON.stringify(selectedLog.metadata, null, 2) }}</pre>
          </div>
        </div>

        <div class="modal-footer">
          <button @click="closeDetails" class="btn btn-secondary">Close</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()
const API_URL = import.meta.env.VITE_API_BASE_URL

const logs = ref([])
const statistics = ref(null)
const loading = ref(false)
const errorMessage = ref('')
const showFilters = ref(false)
const selectedLog = ref(null)

const filters = ref({
  action: '',
  username: '',
  startDate: '',
  endDate: '',
  success: '',
  limit: 50,
  offset: 0
})

const toggleFilters = () => {
  showFilters.value = !showFilters.value
}

const clearFilters = () => {
  filters.value = {
    action: '',
    username: '',
    startDate: '',
    endDate: '',
    success: '',
    limit: 50,
    offset: 0
  }
  loadAuditLogs()
}

const loadAuditLogs = async () => {
  loading.value = true
  errorMessage.value = ''

  try {
    const params = new URLSearchParams()

    if (filters.value.action) params.append('action', filters.value.action)
    if (filters.value.startDate) params.append('start_date', new Date(filters.value.startDate).toISOString())
    if (filters.value.endDate) params.append('end_date', new Date(filters.value.endDate).toISOString())
    if (filters.value.success !== '') params.append('success', filters.value.success)
    params.append('limit', filters.value.limit)
    params.append('offset', filters.value.offset)

    const response = await axios.get(`${API_URL}/audit/logs?${params.toString()}`, {
      headers: {
        Authorization: `Bearer ${authStore.token}`
      }
    })

    logs.value = response.data.logs
  } catch (error) {
    errorMessage.value = error.response?.data?.message || 'Failed to load audit logs'
    console.error('Error loading audit logs:', error)
  } finally {
    loading.value = false
  }
}

const loadStatistics = async () => {
  try {
    const response = await axios.get(`${API_URL}/audit/statistics?period=month`, {
      headers: {
        Authorization: `Bearer ${authStore.token}`
      }
    })

    statistics.value = response.data.statistics
  } catch (error) {
    console.error('Error loading statistics:', error)
  }
}

const loadMoreLogs = () => {
  filters.value.offset += filters.value.limit
  loadAuditLogs()
}

const exportLogs = async (format) => {
  try {
    const params = new URLSearchParams()
    params.append('format', format)

    if (filters.value.action) params.append('action', filters.value.action)
    if (filters.value.startDate) params.append('start_date', new Date(filters.value.startDate).toISOString())
    if (filters.value.endDate) params.append('end_date', new Date(filters.value.endDate).toISOString())
    if (filters.value.success !== '') params.append('success', filters.value.success)
    params.append('limit', 1000)

    const response = await axios.get(`${API_URL}/audit/export?${params.toString()}`, {
      headers: {
        Authorization: `Bearer ${authStore.token}`
      },
      responseType: format === 'csv' ? 'blob' : 'json'
    })

    if (format === 'csv') {
      const url = window.URL.createObjectURL(new Blob([response.data]))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', `audit_logs_${new Date().toISOString().split('T')[0]}.csv`)
      document.body.appendChild(link)
      link.click()
      link.remove()
    }
  } catch (error) {
    errorMessage.value = 'Failed to export logs'
    console.error('Error exporting logs:', error)
  }
}

const viewDetails = (log) => {
  selectedLog.value = log
}

const closeDetails = () => {
  selectedLog.value = null
}

const formatTimestamp = (timestamp) => {
  if (!timestamp) return 'N/A'
  return new Date(timestamp).toLocaleString()
}

const getActionClass = (action) => {
  if (action.includes('LOGIN')) return 'action-auth'
  if (action.includes('UPLOAD') || action.includes('CREATE')) return 'action-create'
  if (action.includes('DELETE')) return 'action-delete'
  if (action.includes('UPDATE')) return 'action-update'
  return 'action-default'
}

onMounted(() => {
  loadAuditLogs()
  loadStatistics()
})
</script>

<style scoped>
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin-bottom: 2rem;
}

.stat-card {
  background: white;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  padding: 1.5rem;
  display: flex;
  align-items: center;
  gap: 1rem;
  transition: all 0.3s ease;
}

.stat-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.stat-card.success {
  border-left: 4px solid var(--success-color);
}

.stat-card.danger {
  border-left: 4px solid var(--danger-color);
}

.stat-icon {
  font-size: 2rem;
}

.stat-content {
  flex: 1;
}

.stat-value {
  font-size: 1.75rem;
  font-weight: bold;
  color: var(--text-primary);
}

.stat-label {
  color: var(--text-secondary);
  font-size: 0.875rem;
  margin-top: 0.25rem;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1rem;
  margin-bottom: 1rem;
}

.timestamp {
  white-space: nowrap;
  font-size: 0.875rem;
  color: var(--text-secondary);
}

.user-info {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.user-role {
  font-size: 0.75rem;
  color: var(--text-secondary);
  background: var(--bg-subtle);
  padding: 0.125rem 0.5rem;
  border-radius: 12px;
  width: fit-content;
}

.action-badge {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  border-radius: 4px;
  font-size: 0.875rem;
  font-weight: 500;
  white-space: nowrap;
}

.action-auth {
  background: #e3f2fd;
  color: #1976d2;
}

.action-create {
  background: #e8f5e9;
  color: #388e3c;
}

.action-delete {
  background: #ffebee;
  color: #d32f2f;
}

.action-update {
  background: #fff3e0;
  color: #f57c00;
}

.action-default {
  background: var(--bg-subtle);
  color: var(--text-primary);
}

.resource-info {
  display: flex;
  flex-direction: column;
  gap: 0.125rem;
}

.resource-info small {
  color: var(--text-secondary);
  font-size: 0.75rem;
}

.badge-success {
  background: var(--success-color);
  color: white;
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.875rem;
  font-weight: 500;
}

.badge-danger {
  background: var(--danger-color);
  color: white;
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.875rem;
  font-weight: 500;
}

.status-code {
  font-size: 0.75rem;
  color: var(--text-secondary);
  margin-top: 0.25rem;
}

.ip-address {
  font-family: 'Courier New', monospace;
  font-size: 0.875rem;
  color: var(--text-secondary);
}

.btn-link {
  background: none;
  border: none;
  color: var(--primary-color);
  text-decoration: underline;
  cursor: pointer;
  padding: 0;
  font-size: 0.875rem;
}

.btn-link:hover {
  color: var(--primary-dark);
}

.row-error {
  background-color: #fff5f5 !important;
}

.pagination {
  padding: 1rem;
  text-align: center;
  border-top: 1px solid var(--border-color);
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 1rem;
}

.modal-content {
  background: white;
  border-radius: 8px;
  max-width: 800px;
  width: 100%;
  max-height: 90vh;
  overflow: auto;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid var(--border-color);
}

.modal-header h2 {
  margin: 0;
}

.modal-close {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: var(--text-secondary);
  padding: 0;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
}

.modal-close:hover {
  background: var(--bg-subtle);
  color: var(--text-primary);
}

.modal-body {
  padding: 1.5rem;
}

.modal-footer {
  padding: 1rem 1.5rem;
  border-top: 1px solid var(--border-color);
  display: flex;
  justify-content: flex-end;
}

.detail-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.detail-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.detail-item label {
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  color: var(--text-secondary);
  letter-spacing: 0.5px;
}

.detail-item span {
  color: var(--text-primary);
  word-break: break-word;
}

.detail-section {
  margin-bottom: 1.5rem;
}

.detail-section label {
  display: block;
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--text-secondary);
  margin-bottom: 0.5rem;
}

.detail-section pre {
  background: var(--bg-subtle);
  padding: 1rem;
  border-radius: 4px;
  font-size: 0.875rem;
  overflow-x: auto;
  margin: 0;
}

.monospace {
  font-family: 'Courier New', monospace;
  font-size: 0.875rem;
}

.monospace.small {
  font-size: 0.75rem;
}

.text-success {
  color: var(--success-color);
  font-weight: 600;
}

.text-danger {
  color: var(--danger-color);
  font-weight: 600;
}

.text-muted {
  color: var(--text-secondary);
}

.error-message,
.user-agent,
.metadata {
  color: var(--text-primary);
  white-space: pre-wrap;
  word-break: break-word;
}

@media (max-width: 768px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }

  .form-grid {
    grid-template-columns: 1fr;
  }

  .detail-grid {
    grid-template-columns: 1fr;
  }
}
</style>
