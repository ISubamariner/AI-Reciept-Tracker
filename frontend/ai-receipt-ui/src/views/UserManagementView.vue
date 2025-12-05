<!-- UserManagementView.vue -->
<!-- Vue.js component for user management (Admin panel) -->
<!-- Place this in: frontend/ai-receipt-ui/src/views/UserManagementView.vue -->

<template>
  <div class="user-management-container">
    <h1>User Management</h1>

    <!-- Create User Form -->
    <div class="card" v-if="isAdmin">
      <h2>Create New User</h2>
      <form @submit.prevent="createUser" class="user-form">
        <div class="form-group">
          <label>Username:</label>
          <input v-model="newUser.username" required />
        </div>
        <div class="form-group">
          <label>Email:</label>
          <input v-model="newUser.email" type="email" required />
        </div>
        <div class="form-group">
          <label>Password:</label>
          <input v-model="newUser.password" type="password" required />
        </div>
        <div class="form-group">
          <label>Role:</label>
          <select v-model="newUser.role">
            <option value="BASIC_USER">Basic User</option>
            <option value="RECEIPT_LOGGER">Receipt Logger</option>
            <option value="SYSTEM_ADMIN">System Admin</option>
          </select>
        </div>
        <button type="submit" class="btn-primary">Create User</button>
      </form>
    </div>

    <!-- Users List -->
    <div class="card">
      <h2>Users</h2>
      <div class="filters">
        <label>
          <input type="checkbox" v-model="includeInactive" @change="loadUsers" />
          Include Inactive Users
        </label>
      </div>

      <div v-if="loading" class="loading">Loading...</div>

      <div v-else-if="error" class="error">{{ error }}</div>

      <table v-else class="users-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Username</th>
            <th>Email</th>
            <th>Role</th>
            <th>Status</th>
            <th v-if="isAdmin">Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="user in users" :key="user.id" :class="{ inactive: !user.is_active }">
            <td>{{ user.id }}</td>
            <td>{{ user.username }}</td>
            <td>{{ user.email }}</td>
            <td>{{ user.role }}</td>
            <td>
              <span :class="user.is_active ? 'badge-active' : 'badge-inactive'">
                {{ user.is_active ? 'Active' : 'Inactive' }}
              </span>
            </td>
            <td v-if="isAdmin" class="actions">
              <button @click="editUser(user)" class="btn-small btn-info">Edit</button>
              <button @click="changeRole(user)" class="btn-small btn-warning">Change Role</button>
              <button @click="resetPassword(user)" class="btn-small btn-secondary">Reset Password</button>
              <button
                v-if="user.is_active"
                @click="deactivateUser(user)"
                class="btn-small btn-danger"
                :disabled="user.id === currentUserId">
                Deactivate
              </button>
              <button
                v-else
                @click="reactivateUser(user)"
                class="btn-small btn-success">
                Reactivate
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Edit User Modal -->
    <div v-if="editingUser" class="modal">
      <div class="modal-content">
        <h3>Edit User</h3>
        <form @submit.prevent="updateUser">
          <div class="form-group">
            <label>Username:</label>
            <input v-model="editingUser.username" required />
          </div>
          <div class="form-group">
            <label>Email:</label>
            <input v-model="editingUser.email" type="email" required />
          </div>
          <div class="modal-actions">
            <button type="submit" class="btn-primary">Update</button>
            <button type="button" @click="editingUser = null" class="btn-secondary">Cancel</button>
          </div>
        </form>
      </div>
    </div>

    <!-- Change Role Modal -->
    <div v-if="changingRoleUser" class="modal">
      <div class="modal-content">
        <h3>Change User Role</h3>
        <form @submit.prevent="updateRole">
          <div class="form-group">
            <label>User: {{ changingRoleUser.username }}</label>
          </div>
          <div class="form-group">
            <label>New Role:</label>
            <select v-model="newRole" required>
              <option value="BASIC_USER">Basic User</option>
              <option value="RECEIPT_LOGGER">Receipt Logger</option>
              <option value="SYSTEM_ADMIN">System Admin</option>
            </select>
          </div>
          <div class="modal-actions">
            <button type="submit" class="btn-primary">Change Role</button>
            <button type="button" @click="changingRoleUser = null" class="btn-secondary">Cancel</button>
          </div>
        </form>
      </div>
    </div>

    <!-- Reset Password Modal -->
    <div v-if="resettingPasswordUser" class="modal">
      <div class="modal-content">
        <h3>Reset Password</h3>
        <form @submit.prevent="doResetPassword">
          <div class="form-group">
            <label>User: {{ resettingPasswordUser.username }}</label>
          </div>
          <div class="form-group">
            <label>New Password:</label>
            <input v-model="resetPasswordValue" type="password" required />
          </div>
          <div class="modal-actions">
            <button type="submit" class="btn-primary">Reset Password</button>
            <button type="button" @click="resettingPasswordUser = null" class="btn-secondary">Cancel</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, computed } from 'vue'
import { useAuthStore } from '@/stores/auth'

export default {
  name: 'UserManagementView',
  setup() {
    const authStore = useAuthStore()
    const users = ref([])
    const loading = ref(false)
    const error = ref(null)
    const includeInactive = ref(false)

    const newUser = ref({
      username: '',
      email: '',
      password: '',
      role: 'BASIC_USER'
    })

    const editingUser = ref(null)
    const changingRoleUser = ref(null)
    const newRole = ref('')
    const resettingPasswordUser = ref(null)
    const resetPasswordValue = ref('')

    const currentUserId = computed(() => authStore.user?.id)
    const isAdmin = computed(() => authStore.user?.role === 'System Admin')

    const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api'

    const getHeaders = () => ({
      'Authorization': `Bearer ${authStore.token}`,
      'Content-Type': 'application/json'
    })

    const loadUsers = async () => {
      loading.value = true
      error.value = null
      try {
        const url = `${API_URL}/users?include_inactive=${includeInactive.value}`
        const response = await fetch(url, {
          headers: getHeaders()
        })

        if (!response.ok) {
          throw new Error('Failed to load users')
        }

        const data = await response.json()
        users.value = data.users
      } catch (err) {
        error.value = err.message
      } finally {
        loading.value = false
      }
    }

    const createUser = async () => {
      try {
        const response = await fetch(`${API_URL}/users`, {
          method: 'POST',
          headers: getHeaders(),
          body: JSON.stringify(newUser.value)
        })

        if (!response.ok) {
          const data = await response.json()
          throw new Error(data.message || 'Failed to create user')
        }

        // Reset form
        newUser.value = {
          username: '',
          email: '',
          password: '',
          role: 'BASIC_USER'
        }

        // Reload users
        await loadUsers()
        alert('User created successfully!')
      } catch (err) {
        alert(`Error: ${err.message}`)
      }
    }

    const editUser = (user) => {
      editingUser.value = { ...user }
    }

    const updateUser = async () => {
      try {
        const response = await fetch(`${API_URL}/users/${editingUser.value.id}`, {
          method: 'PUT',
          headers: getHeaders(),
          body: JSON.stringify({
            username: editingUser.value.username,
            email: editingUser.value.email
          })
        })

        if (!response.ok) {
          const data = await response.json()
          throw new Error(data.message || 'Failed to update user')
        }

        editingUser.value = null
        await loadUsers()
        alert('User updated successfully!')
      } catch (err) {
        alert(`Error: ${err.message}`)
      }
    }

    const changeRole = (user) => {
      changingRoleUser.value = user
      newRole.value = user.role
    }

    const updateRole = async () => {
      try {
        const response = await fetch(`${API_URL}/users/${changingRoleUser.value.id}/role`, {
          method: 'PUT',
          headers: getHeaders(),
          body: JSON.stringify({ role: newRole.value })
        })

        if (!response.ok) {
          const data = await response.json()
          throw new Error(data.message || 'Failed to change role')
        }

        changingRoleUser.value = null
        await loadUsers()
        alert('Role changed successfully!')
      } catch (err) {
        alert(`Error: ${err.message}`)
      }
    }

    const resetPassword = (user) => {
      resettingPasswordUser.value = user
      resetPasswordValue.value = ''
    }

    const doResetPassword = async () => {
      try {
        const response = await fetch(`${API_URL}/users/${resettingPasswordUser.value.id}/reset-password`, {
          method: 'POST',
          headers: getHeaders(),
          body: JSON.stringify({ new_password: resetPasswordValue.value })
        })

        if (!response.ok) {
          const data = await response.json()
          throw new Error(data.message || 'Failed to reset password')
        }

        resettingPasswordUser.value = null
        resetPasswordValue.value = ''
        alert('Password reset successfully!')
      } catch (err) {
        alert(`Error: ${err.message}`)
      }
    }

    const deactivateUser = async (user) => {
      if (!confirm(`Are you sure you want to deactivate ${user.username}?`)) {
        return
      }

      try {
        const response = await fetch(`${API_URL}/users/${user.id}/deactivate`, {
          method: 'POST',
          headers: getHeaders()
        })

        if (!response.ok) {
          const data = await response.json()
          throw new Error(data.message || 'Failed to deactivate user')
        }

        await loadUsers()
        alert('User deactivated successfully!')
      } catch (err) {
        alert(`Error: ${err.message}`)
      }
    }

    const reactivateUser = async (user) => {
      try {
        const response = await fetch(`${API_URL}/users/${user.id}/reactivate`, {
          method: 'POST',
          headers: getHeaders()
        })

        if (!response.ok) {
          const data = await response.json()
          throw new Error(data.message || 'Failed to reactivate user')
        }

        await loadUsers()
        alert('User reactivated successfully!')
      } catch (err) {
        alert(`Error: ${err.message}`)
      }
    }

    onMounted(() => {
      if (!isAdmin.value) {
        error.value = 'You do not have permission to access this page'
        return
      }
      loadUsers()
    })

    return {
      users,
      loading,
      error,
      includeInactive,
      newUser,
      editingUser,
      changingRoleUser,
      newRole,
      resettingPasswordUser,
      resetPasswordValue,
      currentUserId,
      isAdmin,
      loadUsers,
      createUser,
      editUser,
      updateUser,
      changeRole,
      updateRole,
      resetPassword,
      doResetPassword,
      deactivateUser,
      reactivateUser
    }
  }
}
</script>

<style scoped>
.user-management-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.card {
  background: white;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 20px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.user-form {
  display: grid;
  gap: 15px;
  max-width: 500px;
}

.form-group {
  display: flex;
  flex-direction: column;
}

.form-group label {
  margin-bottom: 5px;
  font-weight: 600;
}

.form-group input,
.form-group select {
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.filters {
  margin-bottom: 15px;
}

.users-table {
  width: 100%;
  border-collapse: collapse;
}

.users-table th,
.users-table td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #ddd;
}

.users-table th {
  background-color: #f5f5f5;
  font-weight: 600;
}

.users-table tr.inactive {
  opacity: 0.6;
  background-color: #f9f9f9;
}

.actions {
  display: flex;
  gap: 5px;
  flex-wrap: wrap;
}

.badge-active,
.badge-inactive {
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
}

.badge-active {
  background-color: #d4edda;
  color: #155724;
}

.badge-inactive {
  background-color: #f8d7da;
  color: #721c24;
}

.btn-primary,
.btn-secondary,
.btn-small {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 600;
}

.btn-primary {
  background-color: #007bff;
  color: white;
}

.btn-secondary {
  background-color: #6c757d;
  color: white;
}

.btn-small {
  padding: 4px 8px;
  font-size: 12px;
}

.btn-info {
  background-color: #17a2b8;
  color: white;
}

.btn-warning {
  background-color: #ffc107;
  color: black;
}

.btn-danger {
  background-color: #dc3545;
  color: white;
}

.btn-success {
  background-color: #28a745;
  color: white;
}

button:hover {
  opacity: 0.9;
}

button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0,0,0,0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  padding: 30px;
  border-radius: 8px;
  max-width: 500px;
  width: 90%;
}

.modal-actions {
  display: flex;
  gap: 10px;
  margin-top: 20px;
}

.loading,
.error {
  padding: 20px;
  text-align: center;
}

.error {
  color: #dc3545;
  background-color: #f8d7da;
  border-radius: 4px;
}
</style>
