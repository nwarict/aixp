<template>
  <div>
    <h1 class="text-h4 mb-6">المحادثات</h1>

    <v-row>
      <v-col cols="12" md="4">
        <v-card>
          <v-card-title class="d-flex justify-space-between">
            <span>قائمة المحادثات</span>
            <v-btn icon="mdi-plus" size="small" color="primary" @click="showNewConversation = true"></v-btn>
          </v-card-title>
          <v-card-text>
            <v-text-field
              v-model="search"
              label="بحث"
              prepend-inner-icon="mdi-magnify"
              density="compact"
            ></v-text-field>
            <v-list>
              <v-list-item
                v-for="conv in filteredConversations"
                :key="conv.id"
                @click="selectConversation(conv)"
                :active="selectedConversation?.id === conv.id"
              >
                <template v-slot:prepend>
                  <v-icon :icon="getChannelIcon(conv.channel)" :color="getChannelColor(conv.channel)"></v-icon>
                </template>
                <v-list-item-title>{{ conv.subject || 'بدون عنوان' }}</v-list-item-title>
                <v-list-item-subtitle>
                  <v-chip size="x-small" :color="getStatusColor(conv.status)">{{ conv.status }}</v-chip>
                </v-list-item-subtitle>
              </v-list-item>
            </v-list>
          </v-card-text>
        </v-card>
      </v-col>

      <v-col cols="12" md="8" v-if="selectedConversation">
        <v-card height="70vh">
          <v-card-title class="d-flex justify-space-between align-center">
            <div>
              {{ selectedConversation.subject || 'محادثة' }}
              <v-chip size="small" class="ms-2" :color="selectedConversation.ai_enabled ? 'success' : 'grey'">
                {{ selectedConversation.ai_enabled ? 'AI مفعل' : 'AI معطل' }}
              </v-chip>
            </div>
            <div>
              <v-btn icon="mdi-robot" size="small" @click="triggerAI" :loading="aiLoading"></v-btn>
              <v-btn icon="mdi-close" size="small" @click="selectedConversation = null"></v-btn>
            </div>
          </v-card-title>
          <v-divider></v-divider>
          <v-card-text class="overflow-y-auto" style="height: calc(70vh - 140px);">
            <div v-for="msg in messages" :key="msg.id" class="mb-4">
              <div :class="['d-flex', msg.sender_type === 'customer' ? 'justify-start' : 'justify-end']">
                <v-card :color="msg.sender_type === 'customer' ? 'grey-lighten-3' : 'primary'" class="pa-3" max-width="70%">
                  <div class="text-caption text-grey mb-1">{{ getSenderLabel(msg) }}</div>
                  <div>{{ msg.content }}</div>
                  <div class="text-caption text-grey mt-1">{{ formatDate(msg.created_at) }}</div>
                </v-card>
              </div>
            </div>
          </v-card-text>
          <v-divider></v-divider>
          <v-card-actions>
            <v-text-field
              v-model="newMessage"
              label="رسالة..."
              append-inner-icon="mdi-send"
              @click:append-inner="sendMessage"
              @keyup.enter="sendMessage"
              density="compact"
              hide-details
            ></v-text-field>
          </v-card-actions>
        </v-card>
      </v-col>
    </v-row>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import axios from 'axios'

const conversations = ref([])
const selectedConversation = ref(null)
const messages = ref([])
const search = ref('')
const newMessage = ref('')
const aiLoading = ref(false)
const showNewConversation = ref(false)

const filteredConversations = computed(() => {
  if (!search.value) return conversations.value
  return conversations.value.filter(c => 
    (c.subject || '').includes(search.value) ||
    c.channel.includes(search.value)
  )
})

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

function getSenderLabel(msg) {
  const labels = { customer: 'عميل', agent: 'موظف', ai: 'AI', system: 'نظام' }
  return labels[msg.sender_type] || msg.sender_type
}

function formatDate(date) {
  return new Date(date).toLocaleString('ar-SA')
}

async function loadConversations() {
  try {
    const response = await axios.get('/api/v1/conversations')
    conversations.value = response.data
  } catch (error) {
    console.error('Failed to load conversations:', error)
  }
}

async function selectConversation(conv) {
  selectedConversation.value = conv
  await loadMessages(conv.id)
}

async function loadMessages(conversationId) {
  try {
    const response = await axios.get(`/api/v1/conversations/${conversationId}/messages`)
    messages.value = response.data.reverse()
  } catch (error) {
    console.error('Failed to load messages:', error)
  }
}

async function sendMessage() {
  if (!newMessage.value.trim()) return
  try {
    await axios.post(`/api/v1/conversations/${selectedConversation.value.id}/messages`, {
      content: newMessage.value,
      content_type: 'text'
    })
    newMessage.value = ''
    await loadMessages(selectedConversation.value.id)
  } catch (error) {
    console.error('Failed to send message:', error)
  }
}

async function triggerAI() {
  aiLoading.value = true
  try {
    await axios.post(`/api/v1/conversations/${selectedConversation.value.id}/ai-response`)
    await loadMessages(selectedConversation.value.id)
  } catch (error) {
    console.error('Failed to trigger AI:', error)
  } finally {
    aiLoading.value = false
  }
}

onMounted(loadConversations)
</script>
