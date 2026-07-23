import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../store'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/Login.vue'),
    meta: { public: true }
  },
  {
    path: '/',
    name: 'Layout',
    component: () => import('../components/Layout/AppLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        name: 'Dashboard',
        component: () => import('../views/Dashboard.vue')
      },
      {
        path: 'conversations',
        name: 'Conversations',
        component: () => import('../views/Conversations.vue')
      },
      {
        path: 'customers',
        name: 'Customers',
        component: () => import('../views/Customers.vue')
      },
      {
        path: 'contacts',
        name: 'Contacts',
        component: () => import('../views/Contacts.vue')
      },
      {
        path: 'leads',
        name: 'Leads',
        component: () => import('../views/Leads.vue')
      },
      {
        path: 'deals',
        name: 'Deals',
        component: () => import('../views/Deals.vue')
      },
      {
        path: 'tasks',
        name: 'Tasks',
        component: () => import('../views/Tasks.vue')
      },
      {
        path: 'notes',
        name: 'Notes',
        component: () => import('../views/Notes.vue')
      },
      {
        path: 'campaigns',
        name: 'Campaigns',
        component: () => import('../views/Campaigns.vue')
      },
      {
        path: 'automations',
        name: 'Automations',
        component: () => import('../views/Automations.vue')
      },
      {
        path: 'knowledge',
        name: 'KnowledgeBase',
        component: () => import('../views/KnowledgeBase.vue')
      },
      {
        path: 'ai',
        name: 'AI',
        component: () => import('../views/AI.vue')
      },
      {
        path: 'connectors',
        name: 'Connectors',
        component: () => import('../views/Connectors.vue')
      },
      {
        path: 'uploads',
        name: 'Uploads',
        component: () => import('../views/Uploads.vue')
      },
      {
        path: 'settings',
        name: 'Settings',
        component: () => import('../views/Settings.vue')
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()

  if (to.meta.requiresAuth && !authStore.token) {
    next('/login')
  } else if (to.path === '/login' && authStore.token) {
    next('/')
  } else {
    next()
  }
})

export default router
