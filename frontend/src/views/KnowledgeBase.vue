<template>
  <div>
    <h1 class="text-h4 mb-6">قاعدة المعرفة</h1>
    <v-card>
      <v-card-title class="d-flex justify-space-between">
        <span>المقالات</span>
        <v-btn color="primary" prepend-icon="mdi-plus" @click="showDialog = true">مقال جديد</v-btn>
      </v-card-title>
      <v-card-text>
        <v-row>
          <v-col cols="12" md="4">
            <v-text-field v-model="search" label="بحث" prepend-inner-icon="mdi-magnify" density="compact"></v-text-field>
          </v-col>
        </v-row>
        <v-data-table :headers="headers" :items="filteredArticles" :loading="loading">
          <template v-slot:item.is_published="{ item }">
            <v-chip :color="item.is_published ? 'success' : 'grey'" size="small">
              {{ item.is_published ? 'منشور' : 'مسودة' }}
            </v-chip>
          </template>
        </v-data-table>
      </v-card-text>
    </v-card>

    <v-dialog v-model="showDialog" max-width="700">
      <v-card>
        <v-card-title>مقال جديد</v-card-title>
        <v-card-text>
          <v-text-field v-model="newArticle.title" label="العنوان" required></v-text-field>
          <v-select v-model="newArticle.content_type" :items="['article', 'faq', 'document', 'snippet']" label="النوع"></v-select>
          <v-text-field v-model="newArticle.category" label="الفئة"></v-text-field>
          <v-textarea v-model="newArticle.content" label="المحتوى" rows="6"></v-textarea>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn text @click="showDialog = false">إلغاء</v-btn>
          <v-btn color="primary" @click="createArticle" :loading="saving">حفظ</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'

const articles = ref([])
const loading = ref(false)
const search = ref('')
const showDialog = ref(false)
const saving = ref(false)
const newArticle = ref({ title: '', content: '', content_type: 'article', category: '', language: 'ar' })

const headers = [
  { title: 'العنوان', key: 'title' },
  { title: 'النوع', key: 'content_type' },
  { title: 'الفئة', key: 'category' },
  { title: 'الحالة', key: 'is_published' },
  { title: 'المشاهدات', key: 'view_count' },
]

const filteredArticles = computed(() => {
  if (!search.value) return articles.value
  return articles.value.filter(a => 
    a.title?.includes(search.value) ||
    a.content?.includes(search.value)
  )
})

async function loadArticles() {
  loading.value = true
  try {
    const response = await axios.get('/api/v1/knowledge-base')
    articles.value = response.data
  } catch (error) {
    console.error('Failed to load articles:', error)
  } finally {
    loading.value = false
  }
}

async function createArticle() {
  saving.value = true
  try {
    await axios.post('/api/v1/knowledge-base', newArticle.value)
    showDialog.value = false
    newArticle.value = { title: '', content: '', content_type: 'article', category: '', language: 'ar' }
    await loadArticles()
  } catch (error) {
    alert('خطأ: ' + (error.response?.data?.detail || error.message))
  } finally {
    saving.value = false
  }
}

onMounted(loadArticles)
</script>
