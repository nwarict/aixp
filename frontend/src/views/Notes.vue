<template>
  <div>
    <h1 class="text-h4 mb-6">الملاحظات</h1>
    <v-card>
      <v-card-title class="d-flex justify-space-between">
        <span>قائمة الملاحظات</span>
        <v-btn color="primary" prepend-icon="mdi-plus" @click="showDialog = true">ملاحظة جديدة</v-btn>
      </v-card-title>
      <v-card-text>
        <v-row>
          <v-col cols="12" md="4">
            <v-text-field v-model="search" label="بحث" prepend-inner-icon="mdi-magnify" density="compact"></v-text-field>
          </v-col>
        </v-row>
        <v-data-table :headers="headers" :items="filteredNotes" :loading="loading">
          <template v-slot:item.is_private="{ item }">
            <v-icon :icon="item.is_private ? 'mdi-lock' : 'mdi-lock-open'" :color="item.is_private ? 'error' : 'success'"></v-icon>
          </template>
          <template v-slot:item.actions="{ item }">
            <v-btn icon="mdi-eye" size="small" variant="text" @click="viewNote(item)"></v-btn>
            <v-btn icon="mdi-delete" size="small" variant="text" color="error" @click="deleteNote(item)"></v-btn>
          </template>
        </v-data-table>
      </v-card-text>
    </v-card>

    <v-dialog v-model="showDialog" max-width="600">
      <v-card>
        <v-card-title>ملاحظة جديدة</v-card-title>
        <v-card-text>
          <v-text-field v-model="newNote.title" label="العنوان"></v-text-field>
          <v-textarea v-model="newNote.content" label="المحتوى" rows="4" required></v-textarea>
          <v-select v-model="newNote.related_type" :items="['customer', 'lead', 'deal', 'task', 'conversation']" label="النوع المرتبط"></v-select>
          <v-text-field v-model="newNote.related_id" label="معرف المرتبط"></v-text-field>
          <v-switch v-model="newNote.is_private" label="خاصة"></v-switch>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn text @click="showDialog = false">إلغاء</v-btn>
          <v-btn color="primary" @click="createNote" :loading="saving">حفظ</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'

const notes = ref([])
const loading = ref(false)
const search = ref('')
const showDialog = ref(false)
const saving = ref(false)
const newNote = ref({ title: '', content: '', related_type: 'customer', related_id: '', is_private: false })

const headers = [
  { title: 'العنوان', key: 'title' },
  { title: 'النوع المرتبط', key: 'related_type' },
  { title: 'خاصة', key: 'is_private' },
  { title: 'الإجراءات', key: 'actions', sortable: false },
]

const filteredNotes = computed(() => {
  if (!search.value) return notes.value
  return notes.value.filter(n => n.title?.includes(search.value) || n.content?.includes(search.value))
})

async function loadNotes() {
  loading.value = true
  try {
    const response = await axios.get('/api/v1/notes')
    notes.value = response.data
  } catch (error) {
    console.error('Failed to load notes:', error)
  } finally {
    loading.value = false
  }
}

async function createNote() {
  saving.value = true
  try {
    await axios.post('/api/v1/notes', newNote.value)
    showDialog.value = false
    newNote.value = { title: '', content: '', related_type: 'customer', related_id: '', is_private: false }
    await loadNotes()
  } catch (error) {
    alert('خطأ: ' + (error.response?.data?.detail || error.message))
  } finally {
    saving.value = false
  }
}

function viewNote(note) {
  alert(note.content)
}

async function deleteNote(note) {
  if (!confirm('هل أنت متأكد من حذف هذه الملاحظة؟')) return
  try {
    await axios.delete(`/api/v1/notes/${note.id}`)
    await loadNotes()
  } catch (error) {
    alert('خطأ في الحذف: ' + (error.response?.data?.detail || error.message))
  }
}

onMounted(loadNotes)
</script>
