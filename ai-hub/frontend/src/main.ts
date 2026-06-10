import { createApp } from 'vue'
import { createPinia } from 'pinia'
import piniaPluginPersistedstate from 'pinia-plugin-persistedstate'
import router from './shared/router'
import App from './App.vue'
import './assets/styles/global.css'

const app = createApp(App)

// 【新增】全局错误处理
app.config.errorHandler = (err, instance, info) => {
  console.error('[Vue] 全局错误:', err, '组件:', instance, '信息:', info)
}

// 全局未捕获的 Promise rejection
window.addEventListener('unhandledrejection', (event) => {
  console.error('[Global] 未处理的 Promise rejection:', event.reason)
})

const pinia = createPinia()
pinia.use(piniaPluginPersistedstate)
app.use(pinia)
app.use(router)
app.mount('#app')
