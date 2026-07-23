<template>
  <div>
    <h1 class="text-h4 mb-6">جهات الاتصال</h1>
    <v-card>
      <v-card-title class="d-flex justify-space-between">
        <span>قائمة جهات الاتصال</span>
        <v-btn color="primary" prepend-icon="mdi-plus" @click="showDialog = true">جهة اتصال جديدة</v-btn>
      </v-card-title>
      <v-card-text>
        <v-row>
          <v-col cols="12" md="4">
            <v-text-field v-model="search" label="بحث" prepend-inner-icon="mdi-magnify" density="compact"></v-text-field>
          </v-col>
        </v-row>
        <v-data-table :headers="headers" :items="filteredContacts" :loading="loading">
          <template v-slot:item.type="{ item }">
            <v-icon :icon="getTypeIcon(item.type)" class="me-2"></v-icon>
            {{ item.type }}
          </template>
          <template v-slot:item.is_primary="{ item }">
            <v-icon :icon="item.is_primary ? 'mdi-check-circle' : 'mdi-circle-outline'" :color="item.is_primary ? 'success' : 'grey'"></v-icon>
          </template>
          <template v-slot:item.actions="{ item }">
            <v-btn icon="mdi-delete" size="small" variant="text" color="error" @click="deleteContact(item)"></v-btn>
          </template>
        </v-data-table>
      </v-card-text>
    </v-card>

    <v-dialog v-model="showDialog" max-width="500">
      <v-card>
        <v-card-title>جهة اتصال جديدة</v-card-title>
        <v-card-text>
          <v-text-field v-model="newContact.customer_id" label="معرف العميل" required></v-text-field>
          <v-select v-model="newContact.type" :items="['email', 'phone', 'whatsapp', 'telegram', 'address']" label="النوع"></v-select>
          <v-text-field v-model="newContact.value" label="القيمة" required></v-text-field>
          <v-text-field v-model="newContact.label" label="التسمية" value="primary"></v-text-field>
          <v-switch v-model="newContact.is_primary" label="رئيسي"></v-switch>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn text @click="showDialog = false">إلغاء</v-btn>
          <v-btn color="primary" @click="createContact" :loading="saving">حفظ</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'

const contacts = ref([])
const loading = ref(false)
const search = ref('')
const showDialog = ref(false)
const saving = ref(false)
const newContact = ref({ customer_id: '', type: 'email', value: '', label: 'primary', is_primary: false })

const headers = [
  { title: 'النوع', key: 'type' },
  { title: 'القيمة', key: 'value' },
  { title: 'التسمية', key: 'label' },
  { title: 'رئيسي', key: 'is_primary' },
  { title: 'الإجراءات', key: 'actions', sortable: false },
]

const filteredContacts = computed(() => {
  if (!search.value) return contacts.value
  return contacts.value.filter(c => c.value?.includes(search.value) || c.type?.includes(search.value))
})

function getTypeIcon(type) {
  const icons = { email: 'mdi-email', phone: 'mdi-phone', whatsapp: 'mdi-whatsapp', telegram: 'mdi-send', address: 'mdi-map-marker' }
  return icons[type] || 'mdi-contact'
}

async function loadContacts() {
  loading.value = true
  try {
    const response = await axios.get('/api/v1/contacts')
    contacts.value = response.data
  } catch (error) {
    console.error('Failed to load contacts:', error)
  } finally {
    loading.value = false
  }
}

async function createContact() {
  saving.value = true
  try {
    await axios.post('/api/v1/contacts', newContact.value)
    showDialog.value = false
    newContact.value = { customer_id: '', type: 'email', value: '', label: 'primary', is_primary: false }
    await loadContacts()
  } catch (error) {
    alert('خطأ: ' + (error.response?.data?.detail || error.message))
  } finally {
    saving.value = false
  }
}

async function deleteContact(contact) {
  if (!confirm('هل أنت متأكد من الحذف؟')) return
  try {
    await axios.delete(`/api/v1/contacts/${contact.id}`)
    await loadContacts()
  } catch (error) {
    alert('خطأ في الحذف: ' + (error.response?.data?.detail || error.message))
  }
}

onMounted(loadContacts)
</script>
