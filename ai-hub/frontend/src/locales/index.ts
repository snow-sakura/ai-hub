import { ref, computed } from 'vue'
import zhCNMessages from './zh-CN/index'
import enUSMessages from './en-US/index'

export type LocaleType = 'zh-CN' | 'en-US'

const messagesMap: Record<string, Record<string, any>> = {
  'zh-CN': zhCNMessages,
  'en-US': enUSMessages,
}

// 从 localStorage 读取语言偏好，默认中文
const savedLocale = (localStorage.getItem('app-locale') as LocaleType) || 'zh-CN'

/** 当前语言响应式 ref */
export const locale = ref<LocaleType>(savedLocale)

/** 切换语言并持久化 */
export function setLocale(lang: LocaleType) {
  locale.value = lang
  localStorage.setItem('app-locale', lang)
}

/** 获取当前语言 */
export function getCurrentLocale(): LocaleType {
  return locale.value
}

/**
 * 通过点号路径获取翻译值，如 "common.loading"
 * 支持参数插值 {0} {1} 或 {name}
 */
export function t(key: string, params?: Record<string, string | number> | (string | number)[]): string {
  const keys = key.split('.')
  const lang = locale.value
  let obj: any = messagesMap[lang] || messagesMap['zh-CN']
  for (const k of keys) {
    if (obj && typeof obj === 'object' && k in obj) {
      obj = obj[k]
    } else {
      // fallback 到中文
      let fallback: any = messagesMap['zh-CN']
      for (const fk of keys) {
        if (fallback && typeof fallback === 'object' && fk in fallback) {
          fallback = fallback[fk]
        } else {
          return key // 找不到返回 key
        }
      }
      if (typeof fallback === 'string') {
        return interpolate(fallback, params)
      }
      return key
    }
  }
  if (typeof obj === 'string') {
    return interpolate(obj, params)
  }
  return key
}

/** 参数插值 */
function interpolate(str: string, params?: Record<string, string | number> | (string | number)[]): string {
  if (!params) return str
  if (Array.isArray(params)) {
    return str.replace(/\{(\d+)\}/g, (_, idx) => String(params[+idx] ?? `{${idx}}`))
  }
  return str.replace(/\{(\w+)\}/g, (_, key) => String(params[key] ?? `{${key}}`))
}

/** Vue composable — 在 <script setup> 中使用 */
export function useI18n() {
  return {
    locale,
    t,
    setLocale,
    getCurrentLocale,
  }
}

export default { locale, t, setLocale, getCurrentLocale }
