<template>
  <div>
    <h1 class="text-h4 mb-6">الأتمتة</h1>
    <v-card>
      <v-card-title class="d-flex justify-space-between">
        <span>قائمة قواعد الأتمتة</span>
        <v-btn color="primary" prepend-icon="mdi-plus" @click="showDialog = true">قاعدة جديدة</v-btn>
      </v-card-title>
      <v-card-text>
        <v-data-table :headers="headers" :items="automations" :loading="loading">
          <template v-slot:item.status="{ item }">
            <v-chip :color="item.status === 'active' ? 'success' : 'grey'" size="small">{{ item.status }}</v-chip>
          </template>
          <template v-slot:item.trigger_type="{ item }">
            <v-icon :icon="getTriggerIcon(item.trigger_type)" class="me-2"></v-icon>
            {{ item.trigger_type }}
          </template>
          <template v-slot:item.actions="{ item }">
            <v-btn icon="mdi-play" size="small" variant="text" color="success" @click="runAutomation(item)"></v-btn>
            <v-btn icon="mdi-pencil" size="small" variant="text" @click="editAutomation(item)"></v-btn>
            <v-btn icon="mdi-delete" size="small" variant="text" color="error" @click="deleteAutomation(item)"></v-btn>
          </template>
        </v-data-table>
      </v-card-text>
    </v-card>

    <v-dialog v-model="showDialog" max-width="700">
      <v-card>
        <v-card-title>قاعدة أتمتة جديدة</v-card-title>
        <v-card-text>
          <v-text-field v-model="newAutomation.name" label="الاسم" required></v-text-field>
          <v-textarea v-model="newAutomation.description" label="الوصف"></v-textarea>
          <v-select v-model="newAutomation.trigger_type" :items="['message_received', 'lead_created', 'deal_won', 'task_due', 'campaign_sent']" label="المحفز"></v-select>
          <v-textarea v-model="newAutomation.actions_json" label="الإجراءات (JSON)" rows="4" hint='مثال: [{"type": "send_email", "to": "admin@example.com"}]'></v-textarea>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn text @click="showDialog = false">إلغاء</v-btn>
          <v-btn color="primary" @click="createAutomation" :loading="saving">حفظ</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const automations = ref([])
const loading = ref(false)
const showDialog = ref(false)
const saving = ref(false)
const newAutomation = ref({ name: '', description: '', trigger_type: 'message_received', actions_json: '[]' })

const headers = [
  { title: 'الاسم', key: 'name' },
  { title: 'المحفز', key: 'trigger_type' },
  { title: 'الحالة', key: 'status' },
  { title: 'التنفيذات', key: 'execution_count' },
  { title: 'الإجراءات', key: 'actions', sortable: false },
]

function getTriggerIcon(trigger) {
  const icons = {
    message_received: 'mdi-chat',
    lead_created: 'mdi-target',
    deal_won: 'mdi-handshake',
    task_due: 'mdi-calendar-clock',
    campaign_sent: 'mdi-bullhorn'
  }
  return icons[trigger] || 'mdi-lightning-bolt'
}

async function loadAutomations() {
  loading.value = true
  try {
    const response = await axios.get('/api/v1/automations')
    automations.value = response.data
  } catch (error) {
    console.error('Failed to load automations:', error)
  } finally {
    loading.value = false
  }
}

async function createAutomation() {
  saving.value = true
  try {
    const actions = JSON.parse(newAutomation.value.actions_json)
    await axios.post('/api/v1/automations', {
      name: newAutomation.value.name,
      description: newAutomation.value.description,
      trigger_type: newAutomation.value.trigger_type,
      actions: actions
    })
    showDialog.value = false
    newAutomation.value = { name: '', description: '', trigger_type: 'message_received', actions_json: '[]' }
    await loadAutomations()
  } catch (error) {
    alert('خطأ: ' + (error.response?.data?.detail || error.message))
  } finally {
    saving.value = false
  }
}

async function runAutomation(automation) {
  try {
    await axios.post(`/api/v1/automations/${automation.id}/run`)
    alert('تم تشغيل الأتمتة')
    await loadAutomations()
  } catch (error) {
    alert('خطأ: ' + (error.response?.data?.detail || error.message))
  }
}

async function editAutomation(automation) {
  console.log('Edit automation:', automation)
}

async function deleteAutomation(automation) {
  if (!confirm('هل أنت متأكد من الحذف؟')) return
  try {
    await axios.delete(`/api/v1/automations/${automation.id}`)
    await loadAutomations()
  } catch (error) {
    alert('خطأ في الحذف: ' + (error.response?.data?.detail || error.message))
  }
}

onMounted(loadAutomations)
</script>
