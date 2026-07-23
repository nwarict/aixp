<template>
  <div>
    <h1 class="text-h4 mb-6">الذكاء الاصطناعي</h1>
    <v-row>
      <v-col cols="12" md="8">
        <v-card>
          <v-card-title>محادثة AI</v-card-title>
          <v-card-text>
            <div class="chat-container" style="height: 400px; overflow-y: auto;">
              <div v-for="(msg, index) in chatMessages" :key="index" class="mb-4">
                <div :class="['d-flex', msg.role === 'user' ? 'justify-end' : 'justify-start']">
                  <v-card :color="msg.role === 'user' ? 'primary' : 'grey-lighten-3'" class="pa-3" max-width="80%">
                    <div>{{ msg.content }}</div>
                  </v-card>
                </div>
              </div>
            </div>
            <v-divider class="my-4"></v-divider>
            <v-text-field
              v-model="userMessage"
              label="اكتب رسالتك..."
              append-inner-icon="mdi-send"
              @click:append-inner="sendMessage"
              @keyup.enter="sendMessage"
              :loading="aiLoading"
              hide-details
            ></v-text-field>
          </v-card-text>
        </v-card>
      </v-col>
      <v-col cols="12" md="4">
        <v-card>
          <v-card-title>إعدادات AI</v-card-title>
          <v-card-text>
            <v-select v-model="aiSettings.model" :items="['llama3.1:8b', 'llama3.1:70b', 'gpt-4', 'gpt-3.5-turbo']" label="النموذج"></v-select>
            <v-slider v-model="aiSettings.temperature" label="الإبداعية" min="0" max="1" step="0.1" thumb-label></v-slider>
            <v-text-field v-model="aiSettings.max_tokens" label="الحد الأقصى للرموز" type="number"></v-text-field>
            <v-switch v-model="aiSettings.use_knowledge" label="استخدام قاعدة المعرفة"></v-switch>
            <v-btn color="primary" block @click="saveSettings" :loading="saving">حفظ الإعدادات</v-btn>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const chatMessages = ref([])
const userMessage = ref('')
const aiLoading = ref(false)
const saving = ref(false)
const aiSettings = ref({
  model: 'llama3.1:8b',
  temperature: 0.7,
  max_tokens: 2048,
  use_knowledge: true
})

async function sendMessage() {
  if (!userMessage.value.trim()) return

  chatMessages.value.push({ role: 'user', content: userMessage.value })
  const message = userMessage.value
  userMessage.value = ''
  aiLoading.value = true

  try {
    const response = await axios.post('/api/v1/ai/chat', {
      message: message,
      use_knowledge: aiSettings.value.use_knowledge,
      temperature: aiSettings.value.temperature,
      max_tokens: aiSettings.value.max_tokens,
      model: aiSettings.value.model
    })
    chatMessages.value.push({ role: 'assistant', content: response.data.response })
  } catch (error) {
    chatMessages.value.push({ role: 'assistant', content: 'عذراً، حدث خطأ في معالجة طلبك.' })
  } finally {
    aiLoading.value = false
  }
}

async function saveSettings() {
  saving.value = true
  try {
    await axios.put('/api/v1/ai/config', aiSettings.value)
    alert('تم حفظ الإعدادات')
  } catch (error) {
    alert('خطأ: ' + (error.response?.data?.detail || error.message))
  } finally {
    saving.value = false
  }
}

onMounted(() => {
  chatMessages.value.push({ role: 'assistant', content: 'مرحباً! أنا مساعد AI-XP. كيف يمكنني مساعدتك اليوم؟' })
})
</script>
