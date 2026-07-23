<template>
  <div>
    <h1 class="text-h4 mb-6">الحملات التسويقية</h1>
    <v-card>
      <v-card-title class="d-flex justify-space-between">
        <span>قائمة الحملات</span>
        <v-btn color="primary" prepend-icon="mdi-plus" @click="showDialog = true">حملة جديدة</v-btn>
      </v-card-title>
      <v-card-text>
        <v-data-table :headers="headers" :items="campaigns" :loading="loading">
          <template v-slot:item.status="{ item }">
            <v-chip :color="getStatusColor(item.status)" size="small">{{ item.status }}</v-chip>
          </template>
          <template v-slot:item.channel="{ item }">
            <v-icon :icon="getChannelIcon(item.channel)" class="me-2"></v-icon>
            {{ item.channel }}
          </template>
        </v-data-table>
      </v-card-text>
    </v-card>

    <v-dialog v-model="showDialog" max-width="700">
      <v-card>
        <v-card-title>حملة جديدة</v-card-title>
        <v-card-text>
          <v-text-field v-model="newCampaign.name" label="اسم الحملة" required></v-text-field>
          <v-textarea v-model="newCampaign.description" label="الوصف"></v-textarea>
          <v-select v-model="newCampaign.channel" :items="['email', 'whatsapp', 'telegram', 'sms']" label="القناة"></v-select>
          <v-select v-model="newCampaign.audience_type" :items="['all', 'segment', 'manual']" label="الجمهور"></v-select>
          <v-textarea v-model="newCampaign.content" label="المحتوى"></v-textarea>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn text @click="showDialog = false">إلغاء</v-btn>
          <v-btn color="primary" @click="createCampaign" :loading="saving">حفظ</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const campaigns = ref([])
const loading = ref(false)
const showDialog = ref(false)
const saving = ref(false)
const newCampaign = ref({ name: '', description: '', channel: 'email', audience_type: 'all', content: '' })

const headers = [
  { title: 'الاسم', key: 'name' },
  { title: 'القناة', key: 'channel' },
  { title: 'الحالة', key: 'status' },
  { title: 'المستلمين', key: 'total_recipients' },
  { title: 'المرسل', key: 'sent_count' },
]

function getStatusColor(status) {
  const colors = { draft: 'grey', scheduled: 'info', running: 'warning', completed: 'success', cancelled: 'error' }
  return colors[status] || 'grey'
}

function getChannelIcon(channel) {
  const icons = { email: 'mdi-email', whatsapp: 'mdi-whatsapp', telegram: 'mdi-send', sms: 'mdi-message' }
  return icons[channel] || 'mdi-bullhorn'
}

async function loadCampaigns() {
  loading.value = true
  try {
    const response = await axios.get('/api/v1/campaigns')
    campaigns.value = response.data
  } catch (error) {
    console.error('Failed to load campaigns:', error)
  } finally {
    loading.value = false
  }
}

async function createCampaign() {
  saving.value = true
  try {
    await axios.post('/api/v1/campaigns', newCampaign.value)
    showDialog.value = false
    newCampaign.value = { name: '', description: '', channel: 'email', audience_type: 'all', content: '' }
    await loadCampaigns()
  } catch (error) {
    alert('خطأ: ' + (error.response?.data?.detail || error.message))
  } finally {
    saving.value = false
  }
}

onMounted(loadCampaigns)
</script>
