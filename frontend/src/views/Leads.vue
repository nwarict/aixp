<template>
  <div>
    <h1 class="text-h4 mb-6">العملاء المحتملون</h1>
    <v-card>
      <v-card-title class="d-flex justify-space-between">
        <span>قائمة العملاء المحتملين</span>
        <v-btn color="primary" prepend-icon="mdi-plus" @click="showDialog = true">جديد</v-btn>
      </v-card-title>
      <v-card-text>
        <v-data-table :headers="headers" :items="leads" :loading="loading">
          <template v-slot:item.status="{ item }">
            <v-chip :color="getStatusColor(item.status)" size="small">{{ item.status }}</v-chip>
          </template>
          <template v-slot:item.priority="{ item }">
            <v-chip :color="getPriorityColor(item.priority)" size="small">{{ item.priority }}</v-chip>
          </template>
          <template v-slot:item.value="{ item }">
            {{ item.value }} {{ item.currency }}
          </template>
        </v-data-table>
      </v-card-text>
    </v-card>

    <v-dialog v-model="showDialog" max-width="600">
      <v-card>
        <v-card-title>عميل محتمل جديد</v-card-title>
        <v-card-text>
          <v-text-field v-model="newLead.title" label="العنوان" required></v-text-field>
          <v-textarea v-model="newLead.description" label="الوصف"></v-textarea>
          <v-select v-model="newLead.status" :items="['new', 'qualified', 'proposal', 'negotiation', 'won', 'lost']" label="الحالة"></v-select>
          <v-select v-model="newLead.priority" :items="['low', 'medium', 'high', 'urgent']" label="الأولوية"></v-select>
          <v-text-field v-model="newLead.value" label="القيمة" type="number"></v-text-field>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn text @click="showDialog = false">إلغاء</v-btn>
          <v-btn color="primary" @click="createLead" :loading="saving">حفظ</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const leads = ref([])
const loading = ref(false)
const showDialog = ref(false)
const saving = ref(false)
const newLead = ref({ title: '', description: '', status: 'new', priority: 'medium', value: 0 })

const headers = [
  { title: 'العنوان', key: 'title' },
  { title: 'الحالة', key: 'status' },
  { title: 'الأولوية', key: 'priority' },
  { title: 'القيمة', key: 'value' },
  { title: 'المصدر', key: 'source' },
]

function getStatusColor(status) {
  const colors = { new: 'grey', qualified: 'info', proposal: 'primary', negotiation: 'warning', won: 'success', lost: 'error' }
  return colors[status] || 'grey'
}

function getPriorityColor(priority) {
  const colors = { low: 'success', medium: 'warning', high: 'orange', urgent: 'error' }
  return colors[priority] || 'grey'
}

async function loadLeads() {
  loading.value = true
  try {
    const response = await axios.get('/api/v1/leads')
    leads.value = response.data
  } catch (error) {
    console.error('Failed to load leads:', error)
  } finally {
    loading.value = false
  }
}

async function createLead() {
  saving.value = true
  try {
    await axios.post('/api/v1/leads', newLead.value)
    showDialog.value = false
    newLead.value = { title: '', description: '', status: 'new', priority: 'medium', value: 0 }
    await loadLeads()
  } catch (error) {
    alert('خطأ: ' + (error.response?.data?.detail || error.message))
  } finally {
    saving.value = false
  }
}

onMounted(loadLeads)
</script>
