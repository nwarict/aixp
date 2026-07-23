<template>
  <v-app>
    <v-container class="fill-height" fluid>
      <v-row align="center" justify="center">
        <v-col cols="12" sm="8" md="4">
          <v-card class="elevation-12">
            <v-card-title class="text-center pt-4">
              <h2 class="text-h4 font-weight-bold">AI-XP</h2>
              <p class="text-subtitle-1 text-grey">منصة تجربة العملاء الذكية</p>
            </v-card-title>
            <v-card-text>
              <v-form @submit.prevent="handleLogin" ref="form">
                <v-text-field
                  v-model="email"
                  label="البريد الإلكتروني"
                  prepend-inner-icon="mdi-email"
                  type="email"
                  required
                  :rules="[v => !!v || 'البريد الإلكتروني مطلوب']"
                ></v-text-field>
                <v-text-field
                  v-model="password"
                  label="كلمة المرور"
                  prepend-inner-icon="mdi-lock"
                  type="password"
                  required
                  :rules="[v => !!v || 'كلمة المرور مطلوبة']"
                ></v-text-field>
                <v-btn
                  type="submit"
                  color="primary"
                  block
                  size="large"
                  :loading="loading"
                  class="mt-4"
                >
                  تسجيل الدخول
                </v-btn>
              </v-form>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>
    </v-container>
  </v-app>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../store'

const email = ref('')
const password = ref('')
const loading = ref(false)
const router = useRouter()
const authStore = useAuthStore()

async function handleLogin() {
  loading.value = true
  try {
    await authStore.login(email.value, password.value)
    router.push('/')
  } catch (error) {
    alert('خطأ في تسجيل الدخول: ' + (error.response?.data?.detail || error.message))
  } finally {
    loading.value = false
  }
}
</script>
