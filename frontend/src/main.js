import { createApp } from 'vue'
import { createPinia } from 'pinia'
import { createI18n } from 'vue-i18n'
import App from './App.vue'
import router from './router'
import vuetify from './plugins/vuetify'

import '@mdi/font/css/materialdesignicons.css'

const messages = {
  ar: {
    app: {
      title: 'AI-XP',
      subtitle: 'منصة تجربة العملاء الذكية'
    },
    nav: {
      dashboard: 'لوحة التحكم',
      conversations: 'المحادثات',
      customers: 'العملاء',
      leads: 'العملاء المحتملون',
      campaigns: 'الحملات',
      automations: 'الأتمتة',
      knowledge: 'قاعدة المعرفة',
      ai: 'الذكاء الاصطناعي',
      connectors: 'الموصلات',
      settings: 'الإعدادات'
    },
    common: {
      search: 'بحث',
      create: 'إنشاء',
      edit: 'تعديل',
      delete: 'حذف',
      save: 'حفظ',
      cancel: 'إلغاء',
      confirm: 'تأكيد',
      close: 'إغلاق',
      loading: 'جاري التحميل...',
      noData: 'لا توجد بيانات',
      actions: 'إجراءات'
    },
    auth: {
      login: 'تسجيل الدخول',
      email: 'البريد الإلكتروني',
      password: 'كلمة المرور',
      rememberMe: 'تذكرني',
      forgotPassword: 'نسيت كلمة المرور؟'
    }
  },
  en: {
    app: {
      title: 'AI-XP',
      subtitle: 'AI Customer Experience Platform'
    },
    nav: {
      dashboard: 'Dashboard',
      conversations: 'Conversations',
      customers: 'Customers',
      leads: 'Leads',
      campaigns: 'Campaigns',
      automations: 'Automations',
      knowledge: 'Knowledge Base',
      ai: 'AI',
      connectors: 'Connectors',
      settings: 'Settings'
    },
    common: {
      search: 'Search',
      create: 'Create',
      edit: 'Edit',
      delete: 'Delete',
      save: 'Save',
      cancel: 'Cancel',
      confirm: 'Confirm',
      close: 'Close',
      loading: 'Loading...',
      noData: 'No data available',
      actions: 'Actions'
    },
    auth: {
      login: 'Login',
      email: 'Email',
      password: 'Password',
      rememberMe: 'Remember me',
      forgotPassword: 'Forgot password?'
    }
  }
}

const i18n = createI18n({
  locale: 'ar',
  fallbackLocale: 'en',
  messages
})

const app = createApp(App)

app.use(createPinia())
app.use(router)
app.use(vuetify)
app.use(i18n)

app.mount('#app')
