<template>
  <div>
    <h1 class="text-h4 mb-6">الإعدادات</h1>
    <v-row>
      <v-col cols="12" md="6">
        <v-card>
          <v-card-title>إعدادات المنظمة</v-card-title>
          <v-card-text>
            <v-text-field v-model="tenantSettings.name" label="اسم المنظمة"></v-text-field>
            <v-select v-model="tenantSettings.language" :items="['ar', 'en']" label="اللغة"></v-select>
            <v-text-field v-model="tenantSettings.timezone" label="المنطقة الزمنية"></v-text-field>
            <v-text-field v-model="tenantSettings.currency" label="العملة"></v-text-field>
            <v-btn color="primary" @click="saveTenantSettings" :loading="saving">حفظ</v-btn>
          </v-card-text>
        </v-card>
      </v-col>
      <v-col cols="12" md="6">
        <v-card>
          <v-card-title>إعدادات الأمان</v-card-title>
          <v-card-text>
            <v-text-field v-model="securitySettings.current_password" label="كلمة المرور الحالية" type="password"></v-text-field>
            <v-text-field v-model="securitySettings.new_password" label="كلمة المرور الجديدة" type="password"></v-text-field>
            <v-text-field v-model="securitySettings.confirm_password" label="تأكيد كلمة المرور" type="password"></v-text-field>
            <v-btn color="primary" @click="changePassword" :loading="changingPassword">تغيير كلمة المرور</v-btn>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const tenantSettings = ref({
  name: '',
  language: 'ar',
  timezone: 'Asia/Riyadh',
  currency: 'SAR'
})
const securitySettings = ref({
  current_password: '',
  new_password: '',
  confirm_password: ''
})
const saving = ref(false)
const changingPassword = ref(false)

async function saveTenantSettings() {
  saving.value = true
  try {
    await axios.put('/api/v1/admin/tenant', tenantSettings.value)
    alert('تم حفظ الإعدادات')
  } catch (error) {
    alert('خطأ: ' + (error.response?.data?.detail || error.message))
  } finally {
    saving.value = false
  }
}

async function changePassword() {
  if (securitySettings.value.new_password !== securitySettings.value.confirm_password) {
    alert('كلمات المرور غير متطابقة')
    return
  }
  changingPassword.value = true
  try {
    await axios.post('/api/v1/auth/change-password', {
      current_password: securitySettings.value.current_password,
      new_password: securitySettings.value.new_password
    })
    alert('تم تغيير كلمة المرور')
    securitySettings.value = { current_password: '', new_password: '', confirm_password: '' }
  } catch (error) {
    alert('خطأ: ' + (error.response?.data?.detail || error.message))
  } finally {
    changingPassword.value = false
  }
}

onMounted(async () => {
  try {
    const response = await axios.get('/api/v1/auth/me')
    if (response.data.tenant) {
      tenantSettings.value = { ...tenantSettings.value, ...response.data.tenant.settings }
    }
  } catch (error) {
    console.error('Failed to load settings:', error)
  }
})
</script>
