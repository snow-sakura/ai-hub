/** 配置中心 API */
import request from '@/shared/api/request'

// ── AI 模型配置 ──────────────────────────

export interface ModelConfigItem {
  id: string
  provider: string
  model_name: string
  api_key: string
  api_base_url: string
  temperature: number
  max_tokens: number
  enabled: boolean
  sort_order: number
  created_at: string
  updated_at: string
}

export interface ModelConfigCreateData {
  provider: string
  model_name?: string
  api_key?: string
  api_base_url?: string
  temperature?: number
  max_tokens?: number
  enabled?: boolean
  sort_order?: number
}

export function listModels() {
  return request.get<any, { code: number; data: ModelConfigItem[] }>('/config/models')
}

export function getModel(modelId: string) {
  return request.get<any, { code: number; data: ModelConfigItem }>(`/config/models/${modelId}`)
}

export function createModel(data: ModelConfigCreateData) {
  return request.post<any, { code: number; data: ModelConfigItem }>('/config/models', data)
}

export function updateModel(modelId: string, data: Partial<ModelConfigCreateData>) {
  return request.put<any, { code: number; data: ModelConfigItem }>(`/config/models/${modelId}`, data)
}

export function deleteModel(modelId: string) {
  return request.delete<any, { code: number; message: string }>(`/config/models/${modelId}`)
}

// ── 提示词配置 ──────────────────────────

export interface PromptConfigItem {
  id: string
  name: string
  stage: string
  content: string
  enabled: boolean
  description: string
  created_at: string
  updated_at: string
}

export interface PromptConfigCreateData {
  name: string
  stage?: string
  content: string
  enabled?: boolean
  description?: string
}

export function listPrompts() {
  return request.get<any, { code: number; data: PromptConfigItem[] }>('/config/prompts')
}

export function getPrompt(promptId: string) {
  return request.get<any, { code: number; data: PromptConfigItem }>(`/config/prompts/${promptId}`)
}

export function createPrompt(data: PromptConfigCreateData) {
  return request.post<any, { code: number; data: PromptConfigItem }>('/config/prompts', data)
}

export function updatePrompt(promptId: string, data: Partial<PromptConfigCreateData>) {
  return request.put<any, { code: number; data: PromptConfigItem }>(`/config/prompts/${promptId}`, data)
}

export function deletePrompt(promptId: string) {
  return request.delete<any, { code: number; message: string }>(`/config/prompts/${promptId}`)
}

// ── 生成行为配置 ──────────────────────────

export interface BehaviorConfigItem {
  key: string
  value: string
  description: string
  updated_at: string
}

export function listBehaviors() {
  return request.get<any, { code: number; data: BehaviorConfigItem[] }>('/config/behaviors')
}

export function upsertBehavior(key: string, value: string, description?: string) {
  return request.put<any, { code: number; data: BehaviorConfigItem }>('/config/behaviors', { key, value, description })
}

export function deleteBehavior(key: string) {
  return request.delete<any, { code: number; message: string }>(`/config/behaviors/${key}`)
}

// ── AI 聊天室配置 ──────────────────────────

export interface ChatConfigItem {
  model_provider: string
  model_name: string
  system_prompt: string
  max_history: number
  enable_rag: boolean
  rag_top_k: number
  enable_web_search: boolean
  temperature: number
  updated_at: string
}

export function getChatConfig() {
  return request.get<any, { code: number; data: ChatConfigItem }>('/config/chat')
}

export function updateChatConfig(data: Partial<ChatConfigItem>) {
  return request.put<any, { code: number; data: ChatConfigItem }>('/config/chat', data)
}

// ── UI 环境配置 ──────────────────────────

export interface UiEnvConfigItem {
  id: string
  name: string
  base_url: string
  browser_type: string
  headless: boolean
  viewport_width: number
  viewport_height: number
  timeout_ms: number
  screenshot_on_failure: boolean
  created_at: string
  updated_at: string
}

export interface UiEnvConfigCreateData {
  name: string
  base_url?: string
  browser_type?: string
  headless?: boolean
  viewport_width?: number
  viewport_height?: number
  timeout_ms?: number
  screenshot_on_failure?: boolean
}

export function listUiEnvs() {
  return request.get<any, { code: number; data: UiEnvConfigItem[] }>('/config/ui-envs')
}

export function getUiEnv(envId: string) {
  return request.get<any, { code: number; data: UiEnvConfigItem }>(`/config/ui-envs/${envId}`)
}

export function createUiEnv(data: UiEnvConfigCreateData) {
  return request.post<any, { code: number; data: UiEnvConfigItem }>('/config/ui-envs', data)
}

export function updateUiEnv(envId: string, data: Partial<UiEnvConfigCreateData>) {
  return request.put<any, { code: number; data: UiEnvConfigItem }>(`/config/ui-envs/${envId}`, data)
}

export function deleteUiEnv(envId: string) {
  return request.delete<any, { code: number; message: string }>(`/config/ui-envs/${envId}`)
}

// ── APP 环境配置 ──────────────────────────

export interface AppEnvConfigItem {
  id: string
  name: string
  platform: string
  app_package: string
  app_activity: string
  device_serial: string
  appium_url: string
  timeout_ms: number
  screenshot_on_failure: boolean
  created_at: string
  updated_at: string
}

export interface AppEnvConfigCreateData {
  name: string
  platform?: string
  app_package?: string
  app_activity?: string
  device_serial?: string
  appium_url?: string
  timeout_ms?: number
  screenshot_on_failure?: boolean
}

export function listAppEnvs() {
  return request.get<any, { code: number; data: AppEnvConfigItem[] }>('/config/app-envs')
}

export function getAppEnv(envId: string) {
  return request.get<any, { code: number; data: AppEnvConfigItem }>(`/config/app-envs/${envId}`)
}

export function createAppEnv(data: AppEnvConfigCreateData) {
  return request.post<any, { code: number; data: AppEnvConfigItem }>('/config/app-envs', data)
}

export function updateAppEnv(envId: string, data: Partial<AppEnvConfigCreateData>) {
  return request.put<any, { code: number; data: AppEnvConfigItem }>(`/config/app-envs/${envId}`, data)
}

export function deleteAppEnv(envId: string) {
  return request.delete<any, { code: number; message: string }>(`/config/app-envs/${envId}`)
}
