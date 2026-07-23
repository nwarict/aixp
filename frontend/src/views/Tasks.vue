<template>
  <div>
    <h1 class="text-h4 mb-6">المهام</h1>
    <v-card>
      <v-card-title class="d-flex justify-space-between">
        <span>قائمة المهام</span>
        <v-btn color="primary" prepend-icon="mdi-plus" @click="showDialog = true">مهمة جديدة</v-btn>
      </v-card-title>
      <v-card-text>
        <v-row>
          <v-col cols="12" md="4">
            <v-text-field v-model="search" label="بحث" prepend-inner-icon="mdi-magnify" density="compact"></v-text-field>
          </v-col>
          <v-col cols="12" md="3">
            <v-select v-model="statusFilter" :items="['all', 'todo', 'in_progress', 'done']" label="الحالة" density="compact"></v-select>
          </v-col>
        </v-row>
        <v-data-table :headers="headers" :items="filteredTasks" :loading="loading">
          <template v-slot:item.status="{ item }">
            <v-chip :color="getStatusColor(item.status)" size="small">{{ item.status }}</v-chip>
          </template>
          <template v-slot:item.priority="{ item }">
            <v-chip :color="getPriorityColor(item.priority)" size="small">{{ item.priority }}</v-chip>
          </template>
          <template v-slot:item.actions="{ item }">
            <v-btn icon="mdi-check" size="small" variant="text" color="success" @click="completeTask(item)" v-if="item.status !== 'done'"></v-btn>
            <v-btn icon="mdi-pencil" size="small" variant="text" @click="editTask(item)"></v-btn>
            <v-btn icon="mdi-delete" size="small" variant="text" color="error" @click="deleteTask(item)"></v-btn>
          </template>
        </v-data-table>
      </v-card-text>
    </v-card>

    <v-dialog v-model="showDialog" max-width="600">
      <v-card>
        <v-card-title>مهمة جديدة</v-card-title>
        <v-card-text>
          <v-text-field v-model="newTask.title" label="العنوان" required></v-text-field>
          <v-textarea v-model="newTask.description" label="الوصف"></v-textarea>
          <v-select v-model="newTask.priority" :items="['low', 'medium', 'high', 'urgent']" label="الأولوية"></v-select>
          <v-text-field v-model="newTask.due_date" label="تاريخ الاستحقاق" type="date"></v-text-field>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn text @click="showDialog = false">إلغاء</v-btn>
          <v-btn color="primary" @click="createTask" :loading="saving">حفظ</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'

const tasks = ref([])
const loading = ref(false)
const search = ref('')
const statusFilter = ref('all')
const showDialog = ref(false)
const saving = ref(false)
const newTask = ref({ title: '', description: '', priority: 'medium', due_date: '' })

const headers = [
  { title: 'العنوان', key: 'title' },
  { title: 'الحالة', key: 'status' },
  { title: 'الأولوية', key: 'priority' },
  { title: 'تاريخ الاستحقاق', key: 'due_date' },
  { title: 'الإجراءات', key: 'actions', sortable: false },
]

const filteredTasks = computed(() => {
  let result = tasks.value
  if (search.value) {
    result = result.filter(t => t.title?.includes(search.value))
  }
  if (statusFilter.value !== 'all') {
    result = result.filter(t => t.status === statusFilter.value)
  }
  return result
})

function getStatusColor(status) {
  const colors = { todo: 'grey', in_progress: 'warning', done: 'success' }
  return colors[status] || 'grey'
}

function getPriorityColor(priority) {
  const colors = { low: 'success', medium: 'warning', high: 'orange', urgent: 'error' }
  return colors[priority] || 'grey'
}

async function loadTasks() {
  loading.value = true
  try {
    const response = await axios.get('/api/v1/tasks')
    tasks.value = response.data
  } catch (error) {
    console.error('Failed to load tasks:', error)
  } finally {
    loading.value = false
  }
}

async function createTask() {
  saving.value = true
  try {
    await axios.post('/api/v1/tasks', newTask.value)
    showDialog.value = false
    newTask.value = { title: '', description: '', priority: 'medium', due_date: '' }
    await loadTasks()
  } catch (error) {
    alert('خطأ: ' + (error.response?.data?.detail || error.message))
  } finally {
    saving.value = false
  }
}

async function completeTask(task) {
  try {
    await axios.put(`/api/v1/tasks/${task.id}`, { status: 'done', completed_at: new Date().toISOString() })
    await loadTasks()
  } catch (error) {
    alert('خطأ: ' + (error.response?.data?.detail || error.message))
  }
}

async function editTask(task) {
  console.log('Edit task:', task)
}

async function deleteTask(task) {
  if (!confirm('هل أنت متأكد من حذف هذه المهمة؟')) return
  try {
    await axios.delete(`/api/v1/tasks/${task.id}`)
    await loadTasks()
  } catch (error) {
    alert('خطأ في الحذف: ' + (error.response?.data?.detail || error.message))
  }
}

onMounted(loadTasks)
</script>
