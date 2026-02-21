/**
 * 配置 API 客户端（模型配置、界面设置）
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api'

export interface ModelParamsEntry {
  params?: Record<string, unknown>
}

export interface ModelModalityConfig {
  default_model?: string
  params?: Record<string, unknown>
  /** 各模型单独参数，key 为模型 id */
  models?: Record<string, ModelParamsEntry>
}

export interface ConfigModel {
  text?: ModelModalityConfig
  image?: ModelModalityConfig
  video?: ModelModalityConfig
}

export interface ConfigUI {
  theme?: string
  sidebar_collapsed?: boolean
  [key: string]: unknown
}

export interface AppConfig {
  model: ConfigModel
  ui: ConfigUI
}

/**
 * 获取当前配置（未保存项为后端默认值）
 */
export async function getConfig(): Promise<AppConfig> {
  const response = await fetch(`${API_BASE_URL}/config`, { cache: 'no-store' })
  if (!response.ok) throw new Error('获取配置失败')
  return response.json()
}

/**
 * 更新配置（只传需要更新的 model / ui，与现有配置合并）
 */
export async function updateConfig(update: {
  model?: ConfigModel
  ui?: ConfigUI
}): Promise<AppConfig> {
  const response = await fetch(`${API_BASE_URL}/config`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(update)
  })
  if (!response.ok) {
    const err = await response.json().catch(() => ({}))
    throw new Error((err as { detail?: string })?.detail ?? '保存配置失败')
  }
  return response.json()
}
