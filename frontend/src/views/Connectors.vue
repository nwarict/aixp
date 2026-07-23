<template>
  <div>
    <h1 class="text-h4 mb-6">الموصلات</h1>
    <v-row>
      <v-col cols="12" md="4" v-for="connector in connectors" :key="connector.type">
        <v-card>
          <v-card-title class="d-flex align-center">
            <v-icon :icon="getConnectorIcon(connector.type)" size="32" class="me-3" :color="connector.status === 'active' ? 'success' : 'grey'"></v-icon>
            {{ connector.name }}
          </v-card-title>
          <v-card-text>
            <v-chip :color="connector.status === 'active' ? 'success' : 'grey'" size="small">{{ connector.status }}</v-chip>
            <div class="mt-2 text-caption">{{ connector.description }}</div>
            <div class="mt-2 text-caption">الرسائل: {{ connector.message_count || 0 }}</div>
          </v-card-text>
          <v-card-actions>
            <v-btn size="small" variant="text" @click="configureConnector(connector)">إعدادات</v-btn>
            <v-btn size="small" variant="text" :color="connector.status === 'active' ? 'error' : 'success'" @click="toggleConnector(connector)">
              {{ connector.status === 'active' ? 'تعطيل' : 'تفعيل' }}
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-col>
    </v-row>

    <v-dialog v-model="showDialog" max-width="600">
      <v-card>
        <v-card-title>إعدادات {{ selectedConnector?.name }}</v-card-title>
        <v-card-text>
          <v-text-field v-model="config.name" label="الاسم"></v-text-field>
          <v-textarea v-model="config.config_json" label="الإعدادات (JSON)" rows="4"></v-textarea>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn text @click="showDialog = false">إلغاء</v-btn>
          <v-btn color="primary" @click="saveConfig" :loading="saving">حفظ</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const connectors = ref([
  { type: 'whatsapp', name: 'WhatsApp', description: 'ربط مع WhatsApp Business API', status: 'inactive', message_count: 0 },
  { type: 'telegram', name: 'Telegram', description: 'ربط مع Telegram Bot', status: 'inactive', message_count: 0 },
  { type: 'email', name: 'Email', description: 'ربط مع SMTP server', status: 'inactive', message_count: 0 },
  { type: 'messenger', name: 'Messenger', description: 'ربط مع Facebook Messenger', status: 'inactive', message_count: 0 },
  { type: 'wordpress', name: 'WordPress', description: 'ربط مع WordPress site', status: 'inactive', message_count: 0 },
  { type: 'webhook', name: 'Webhook', description: 'Webhook عام', status: 'inactive', message_count: 0 },
])
const loading = ref(false)
const showDialog = ref(false)
const saving = ref(false)
const selectedConnector = ref(null)
const config = ref({ name: '', config_json: '{}' })

function getConnectorIcon(type) {
  const icons = {
    whatsapp: 'mdi-whatsapp',
    telegram: 'mdi-send',
    email: 'mdi-email',
    messenger: 'mdi-facebook-messenger',
    wordpress: 'mdi-wordpress',
    webhook: 'mdi-webhook'
  }
  return icons[type] || 'mdi-connection'
}

async function loadConnectors() {
  try {
    const response = await axios.get('/api/v1/connectors')
    if (response.data && response.data.length > 0) {
      connectors.value = response.data
    }
  } catch (error) {
    console.error('Failed to load connectors:', error)
  }
}

function configureConnector(connector) {
  selectedConnector.value = connector
  config.value = { name: connector.name, config_json: JSON.stringify(connector.config || {}, null, 2) }
  showDialog.value = true
}

async function saveConfig() {
  saving.value = true
  try {
    const configData = JSON.parse(config.value.config_json)
    await axios.post('/api/v1/connectors', {
      name: config.value.name,
      type: selectedConnector.value.type,
      provider: selectedConnector.value.type,
      config: configData
    })
    showDialog.value = false
    await loadConnectors()
  } catch (error) {
    alert('خطأ: ' + (error.response?.data?.detail || error.message))
  } finally {
    saving.value = false
  }
}

async function toggleConnector(connector) {
  try {
    const newStatus = connector.status === 'active' ? 'inactive' : 'active'
    await axios.put(`/api/v1/connectors/${connector.id}`, { status: newStatus })
    await loadConnectors()
  } catch (error) {
    alert('خطأ: ' + (error.response?.data?.detail || error.message))
  }
}

onMounted(loadConnectors)
</script>
