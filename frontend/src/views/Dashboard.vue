<template>
  <div>
    <h1 class="text-h4 mb-6">لوحة التحكم</h1>

    <v-row>
      <v-col cols="12" md="3" v-for="stat in stats" :key="stat.title">
        <v-card>
          <v-card-text>
            <div class="d-flex align-center">
              <v-icon :icon="stat.icon" size="40" :color="stat.color" class="me-4"></v-icon>
              <div>
                <div class="text-h6">{{ stat.value }}</div>
                <div class="text-caption text-grey">{{ stat.title }}</div>
              </div>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <v-row class="mt-6">
      <v-col cols="12" md="8">
        <v-card>
          <v-card-title>المحادثات النشطة</v-card-title>
          <v-card-text>
            <v-list>
              <v-list-item
                v-for="conv in recentConversations"
                :key="conv.id"
                :to="`/conversations`"
              >
                <template v-slot:prepend>
                  <v-icon :icon="getChannelIcon(conv.channel)" :color="getChannelColor(conv.channel)"></v-icon>
                </template>
                <v-list-item-title>{{ conv.subject || 'بدون عنوان' }}</v-list-item-title>
                <v-list-item-subtitle>
                  <v-chip size="small" :color="getStatusColor(conv.status)">{{ conv.status }}</v-chip>
                </v-list-item-subtitle>
              </v-list-item>
            </v-list>
          </v-card-text>
        </v-card>
      </v-col>

      <v-col cols="12" md="4">
        <v-card>
          <v-card-title>القنوات</v-card-title>
          <v-card-text>
            <v-list>
              <v-list-item v-for="ch in channelStats" :key="ch.channel">
                <v-list-item-title>{{ ch.channel }}</v-list-item-title>
                <template v-slot:append>
                  <v-chip>{{ ch.count }}</v-chip>
                </template>
              </v-list-item>
            </v-list>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const stats = ref([
  { title: 'العملاء', value: 0, icon: 'mdi-account-group', color: 'primary' },
  { title: 'المحادثات', value: 0, icon: 'mdi-chat', color: 'success' },
  { title: 'النشطة', value: 0, icon: 'mdi-chat-processing', color: 'warning' },
  { title: 'الحملات', value: 0, icon: 'mdi-bullhorn', color: 'info' },
])

const recentConversations = ref([])
const channelStats = ref([])

function getChannelIcon(channel) {
  const icons = { whatsapp: 'mdi-whatsapp', telegram: 'mdi-send', email: 'mdi-email', website: 'mdi-web' }
  return icons[channel] || 'mdi-chat'
}

function getChannelColor(channel) {
  const colors = { whatsapp: 'green', telegram: 'blue', email: 'red', website: 'purple' }
  return colors[channel] || 'grey'
}

function getStatusColor(status) {
  const colors = { active: 'success', waiting: 'warning', resolved: 'info', closed: 'grey' }
  return colors[status] || 'grey'
}

onMounted(async () => {
  try {
    const response = await axios.get('/api/v1/admin/dashboard')
    const data = response.data
    stats.value[0].value = data.stats.customers
    stats.value[1].value = data.stats.conversations
    stats.value[2].value = data.stats.active_conversations
    stats.value[3].value = data.stats.campaigns
    recentConversations.value = data.recent_conversations
    channelStats.value = data.channel_stats
  } catch (error) {
    console.error('Failed to load dashboard:', error)
  }
})
</script>
