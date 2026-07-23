<template>
  <div>
    <h1 class="text-h4 mb-6">الصفقات</h1>
    <v-card>
      <v-card-title class="d-flex justify-space-between">
        <span>قائمة الصفقات</span>
        <v-btn color="primary" prepend-icon="mdi-plus" @click="showDialog = true">صفقة جديدة</v-btn>
      </v-card-title>
      <v-card-text>
        <v-row>
          <v-col cols="12" md="4">
            <v-text-field v-model="search" label="بحث" prepend-inner-icon="mdi-magnify" density="compact"></v-text-field>
          </v-col>
          <v-col cols="12" md="3">
            <v-select v-model="stageFilter" :items="['all', 'discovery', 'proposal', 'negotiation', 'closed']" label="المرحلة" density="compact"></v-select>
          </v-col>
        </v-row>
        <v-data-table :headers="headers" :items="filteredDeals" :loading="loading">
          <template v-slot:item.status="{ item }">
            <v-chip :color="getStatusColor(item.status)" size="small">{{ item.status }}</v-chip>
          </template>
          <template v-slot:item.stage="{ item }">
            <v-chip :color="getStageColor(item.stage)" size="small">{{ item.stage }}</v-chip>
          </template>
          <template v-slot:item.value="{ item }">
            {{ item.value }} {{ item.currency }}
          </template>
          <template v-slot:item.actions="{ item }">
            <v-btn icon="mdi-pencil" size="small" variant="text" @click="editDeal(item)"></v-btn>
            <v-btn icon="mdi-delete" size="small" variant="text" color="error" @click="deleteDeal(item)"></v-btn>
          </template>
        </v-data-table>
      </v-card-text>
    </v-card>

    <v-dialog v-model="showDialog" max-width="600">
      <v-card>
        <v-card-title>صفقة جديدة</v-card-title>
        <v-card-text>
          <v-text-field v-model="newDeal.title" label="العنوان" required></v-text-field>
          <v-textarea v-model="newDeal.description" label="الوصف"></v-textarea>
          <v-select v-model="newDeal.stage" :items="['discovery', 'proposal', 'negotiation', 'closed']" label="المرحلة"></v-select>
          <v-text-field v-model="newDeal.value" label="القيمة" type="number"></v-text-field>
          <v-text-field v-model="newDeal.probability" label="نسبة النجاح %" type="number"></v-text-field>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn text @click="showDialog = false">إلغاء</v-btn>
          <v-btn color="primary" @click="createDeal" :loading="saving">حفظ</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'

const deals = ref([])
const loading = ref(false)
const search = ref('')
const stageFilter = ref('all')
const showDialog = ref(false)
const saving = ref(false)
const newDeal = ref({ title: '', description: '', stage: 'discovery', value: 0, probability: 0, currency: 'SAR' })

const headers = [
  { title: 'العنوان', key: 'title' },
  { title: 'المرحلة', key: 'stage' },
  { title: 'الحالة', key: 'status' },
  { title: 'القيمة', key: 'value' },
  { title: 'النسبة', key: 'probability' },
  { title: 'الإجراءات', key: 'actions', sortable: false },
]

const filteredDeals = computed(() => {
  let result = deals.value
  if (search.value) {
    result = result.filter(d => d.title?.includes(search.value) || d.description?.includes(search.value))
  }
  if (stageFilter.value !== 'all') {
    result = result.filter(d => d.stage === stageFilter.value)
  }
  return result
})

function getStatusColor(status) {
  const colors = { draft: 'grey', active: 'primary', won: 'success', lost: 'error', cancelled: 'warning' }
  return colors[status] || 'grey'
}

function getStageColor(stage) {
  const colors = { discovery: 'info', proposal: 'primary', negotiation: 'warning', closed: 'success' }
  return colors[stage] || 'grey'
}

async function loadDeals() {
  loading.value = true
  try {
    const response = await axios.get('/api/v1/deals')
    deals.value = response.data
  } catch (error) {
    console.error('Failed to load deals:', error)
  } finally {
    loading.value = false
  }
}

async function createDeal() {
  saving.value = true
  try {
    await axios.post('/api/v1/deals', newDeal.value)
    showDialog.value = false
    newDeal.value = { title: '', description: '', stage: 'discovery', value: 0, probability: 0, currency: 'SAR' }
    await loadDeals()
  } catch (error) {
    alert('خطأ: ' + (error.response?.data?.detail || error.message))
  } finally {
    saving.value = false
  }
}

async function editDeal(deal) {
  console.log('Edit deal:', deal)
}

async function deleteDeal(deal) {
  if (!confirm('هل أنت متأكد من حذف هذه الصفقة؟')) return
  try {
    await axios.delete(`/api/v1/deals/${deal.id}`)
    await loadDeals()
  } catch (error) {
    alert('خطأ في الحذف: ' + (error.response?.data?.detail || error.message))
  }
}

onMounted(loadDeals)
</script>
