<template>
  <v-app>
    <v-navigation-drawer
      v-model="drawer"
      :rail="rail"
      permanent
      location="right"
      @click="rail = false"
    >
      <v-list-item
        prepend-avatar="https://cdn.vuetifyjs.com/images/logos/vuetify-logo-dark.png"
        title="AI-XP"
        nav
      >
        <template v-slot:append>
          <v-btn
            variant="text"
            icon="mdi-chevron-left"
            @click.stop="rail = !rail"
          ></v-btn>
        </template>
      </v-list-item>

      <v-divider></v-divider>

      <v-list density="compact" nav>
        <v-list-item
          v-for="item in menuItems"
          :key="item.path"
          :prepend-icon="item.icon"
          :title="item.title"
          :to="item.path"
          :active="$route.path === item.path"
        ></v-list-item>
      </v-list>

      <template v-slot:append>
        <v-list density="compact" nav>
          <v-list-item
            prepend-icon="mdi-logout"
            title="تسجيل الخروج"
            @click="logout"
          ></v-list-item>
        </v-list>
      </template>
    </v-navigation-drawer>

    <v-app-bar>
      <v-app-bar-title>{{ $t('app.title') }}</v-app-bar-title>
      <v-spacer></v-spacer>
      <v-btn icon="mdi-bell"></v-btn>
      <v-btn icon="mdi-account"></v-btn>
    </v-app-bar>

    <v-main>
      <v-container fluid>
        <router-view />
      </v-container>
    </v-main>
  </v-app>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../store'

const drawer = ref(true)
const rail = ref(false)
const router = useRouter()
const authStore = useAuthStore()

const menuItems = [
  { title: 'لوحة التحكم', path: '/', icon: 'mdi-view-dashboard' },
  { title: 'المحادثات', path: '/conversations', icon: 'mdi-chat' },
  { title: 'العملاء', path: '/customers', icon: 'mdi-account-group' },
  { title: 'جهات الاتصال', path: '/contacts', icon: 'mdi-contacts' },
  { title: 'العملاء المحتملون', path: '/leads', icon: 'mdi-target' },
  { title: 'الصفقات', path: '/deals', icon: 'mdi-handshake' },
  { title: 'المهام', path: '/tasks', icon: 'mdi-checkbox-marked-circle' },
  { title: 'الملاحظات', path: '/notes', icon: 'mdi-note-text' },
  { title: 'الحملات', path: '/campaigns', icon: 'mdi-bullhorn' },
  { title: 'الأتمتة', path: '/automations', icon: 'mdi-robot' },
  { title: 'قاعدة المعرفة', path: '/knowledge', icon: 'mdi-book-open' },
  { title: 'الذكاء الاصطناعي', path: '/ai', icon: 'mdi-brain' },
  { title: 'الموصلات', path: '/connectors', icon: 'mdi-connection' },
  { title: 'الملفات', path: '/uploads', icon: 'mdi-folder' },
  { title: 'الإعدادات', path: '/settings', icon: 'mdi-cog' },
]

function logout() {
  authStore.logout()
  router.push('/login')
}
</script>
