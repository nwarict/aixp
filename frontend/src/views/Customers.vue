<template>
  <div>
    <h1 class="text-h4 mb-6">العملاء</h1>

    <v-card>
      <v-card-title class="d-flex justify-space-between">
        <span>قائمة العملاء</span>
        <v-btn color="primary" prepend-icon="mdi-plus" @click="showDialog = true">
          عميل جديد
        </v-btn>
      </v-card-title>
      <v-card-text>
        <v-row>
          <v-col cols="12" md="4">
            <v-text-field
              v-model="search"
              label="بحث"
              prepend-inner-icon="mdi-magnify"
              density="compact"
            ></v-text-field>
          </v-col>
          <v-col cols="12" md="3">
            <v-select
              v-model="statusFilter"
              :items="['all', 'active', 'inactive', 'blocked']"
              label="الحالة"
              density="compact"
            ></v-select>
          </v-col>
        </v-row>

        <v-data-table
          :headers="headers"
          :items="filteredCustomers"
          :loading="loading"
          class="mt-4"
        >
          <template v-slot:item.status="{ item }">
            <v-chip :color="getStatusColor(item.status)" size="small">{{ item.status }}</v-chip>
          </template>
          <template v-slot:item.actions="{ item }">
            <v-btn icon="mdi-eye" size="small" variant="text" @click="viewCustomer(item)"></v-btn>
            <v-btn icon="mdi-pencil" size="small" variant="text" @click="editCustomer(item)"></v-btn>
            <v-btn icon="mdi-delete" size="small" variant="text" color="error" @click="deleteCustomer(item)"></v-btn>
          </template>
        </v-data-table>
      </v-card-text>
    </v-card>

    <!-- Create Dialog -->
    <v-dialog v-model="showDialog" max-width="600">
      <v-card>
        <v-card-title>عميل جديد</v-card-title>
        <v-card-text>
          <v-text-field v-model="newCustomer.full_name" label="الاسم الكامل" required></v-text-field>
          <v-text-field v-model="newCustomer.email" label="البريد الإلكتروني" type="email"></v-text-field>
          <v-text-field v-model="newCustomer.phone" label="الهاتف"></v-text-field>
          <v-text-field v-model="newCustomer.company" label="الشركة"></v-text-field>
          <v-select v-model="newCustomer.source" :items="['manual', 'website', 'whatsapp', 'telegram', 'email']" label="المصدر"></v-select>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn text @click="showDialog = false">إلغاء</v-btn>
          <v-btn color="primary" @click="createCustomer" :loading="saving">حفظ</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'

const customers = ref([])
const loading = ref(false)
const search = ref('')
const statusFilter = ref('all')
const showDialog = ref(false)
const saving = ref(false)

const newCustomer = ref({
  full_name: '',
  email: '',
  phone: '',
  company: '',
  source: 'manual'
})

const headers = [
  { title: 'الاسم', key: 'full_name' },
  { title: 'البريد', key: 'email' },
  { title: 'الهاتف', key: 'phone' },
  { title: 'الشركة', key: 'company' },
  { title: 'الحالة', key: 'status' },
  { title: 'المصدر', key: 'source' },
  { title: 'الإجراءات', key: 'actions', sortable: false },
]

const filteredCustomers = computed(() => {
  let result = customers.value
  if (search.value) {
    result = result.filter(c => 
      c.full_name?.includes(search.value) ||
      c.email?.includes(search.value) ||
      c.phone?.includes(search.value)
    )
  }
  if (statusFilter.value !== 'all') {
    result = result.filter(c => c.status === statusFilter.value)
  }
  return result
})

function getStatusColor(status) {
  const colors = { active: 'success', inactive: 'warning', blocked: 'error' }
  return colors[status] || 'grey'
}

async function loadCustomers() {
  loading.value = true
  try {
    const response = await axios.get('/api/v1/customers')
    customers.value = response.data
  } catch (error) {
    console.error('Failed to load customers:', error)
  } finally {
    loading.value = false
  }
}

async function createCustomer() {
  saving.value = true
  try {
    await axios.post('/api/v1/customers', newCustomer.value)
    showDialog.value = false
    newCustomer.value = { full_name: '', email: '', phone: '', company: '', source: 'manual' }
    await loadCustomers()
  } catch (error) {
    alert('خطأ: ' + (error.response?.data?.detail || error.message))
  } finally {
    saving.value = false
  }
}

function viewCustomer(customer) {
  console.log('View customer:', customer)
}

function editCustomer(customer) {
  console.log('Edit customer:', customer)
}

async function deleteCustomer(customer) {
  if (!confirm('هل أنت متأكد من حذف هذا العميل؟')) return
  try {
    await axios.delete(`/api/v1/customers/${customer.id}`)
    await loadCustomers()
  } catch (error) {
    alert('خطأ في الحذف: ' + (error.response?.data?.detail || error.message))
  }
}

onMounted(loadCustomers)
</script>
