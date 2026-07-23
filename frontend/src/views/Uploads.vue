<template>
  <div>
    <h1 class="text-h4 mb-6">الملفات</h1>
    <v-card>
      <v-card-title class="d-flex justify-space-between">
        <span>قائمة الملفات</span>
        <v-btn color="primary" prepend-icon="mdi-upload" @click="showUpload = true">رفع ملف</v-btn>
      </v-card-title>
      <v-card-text>
        <v-file-input
          v-model="selectedFile"
          label="اختر ملف"
          prepend-icon="mdi-paperclip"
          @change="uploadFile"
          v-if="showUpload"
        ></v-file-input>
        <v-data-table :headers="headers" :items="uploads" :loading="loading">
          <template v-slot:item.size="{ item }">
            {{ formatSize(item.size) }}
          </template>
          <template v-slot:item.actions="{ item }">
            <v-btn icon="mdi-download" size="small" variant="text" @click="downloadFile(item)"></v-btn>
            <v-btn icon="mdi-delete" size="small" variant="text" color="error" @click="deleteFile(item)"></v-btn>
          </template>
        </v-data-table>
      </v-card-text>
    </v-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const uploads = ref([])
const loading = ref(false)
const showUpload = ref(false)
const selectedFile = ref(null)

const headers = [
  { title: 'الاسم', key: 'filename' },
  { title: 'الحجم', key: 'size' },
  { title: 'النوع', key: 'content_type' },
  { title: 'التاريخ', key: 'created_at' },
  { title: 'الإجراءات', key: 'actions', sortable: false },
]

function formatSize(bytes) {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

async function loadUploads() {
  loading.value = true
  try {
    const response = await axios.get('/api/v1/uploads')
    uploads.value = response.data
  } catch (error) {
    console.error('Failed to load uploads:', error)
  } finally {
    loading.value = false
  }
}

async function uploadFile() {
  if (!selectedFile.value) return
  const formData = new FormData()
  formData.append('file', selectedFile.value)

  try {
    await axios.post('/api/v1/uploads', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    selectedFile.value = null
    showUpload.value = false
    await loadUploads()
  } catch (error) {
    alert('خطأ في الرفع: ' + (error.response?.data?.detail || error.message))
  }
}

function downloadFile(file) {
  window.open(file.url, '_blank')
}

async function deleteFile(file) {
  if (!confirm('هل أنت متأكد من الحذف؟')) return
  try {
    await axios.delete(`/api/v1/uploads/${file.id}`)
    await loadUploads()
  } catch (error) {
    alert('خطأ في الحذف: ' + (error.response?.data?.detail || error.message))
  }
}

onMounted(loadUploads)
</script>
