/**
 * 图片生成 API 客户端（实现方式参考 video 接口，参数平铺）
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api'

export interface CreateImageParams {
  /** 完整请求体（参数平铺）。若提供则以此为基础，仅用 prompt/image 覆盖对应键 */
  body?: Record<string, unknown>
  /** 未传 body 时使用：必填提示词 */
  prompt?: string
  model?: string
  negative_prompt?: string
  image?: string
  extra_body?: Record<string, unknown>
}

/** 常见响应：data[].url 或 data[].b64_json，或顶层 url */
export interface CreateImageResponse {
  data?: Array<{ url?: string; b64_json?: string }>
  url?: string
  created?: number
  raw?: string
  [key: string]: unknown
}

/**
 * 提交图片生成请求（文生图/图生图），参数平铺转发
 */
export async function createImage(
  params: CreateImageParams
): Promise<CreateImageResponse> {
  let body: Record<string, unknown>
  if (params.body && Object.keys(params.body).length > 0) {
    body = { ...params.body }
  } else {
    body = {
      prompt: params.prompt ?? '',
      negative_prompt: params.negative_prompt,
      image: params.image,
      extra_body: params.extra_body
    }
    if (params.model != null) body.model = params.model
  }
  if (params.prompt != null) body.prompt = params.prompt
  if (params.image != null) body.image = params.image
  if (typeof body.prompt !== 'string' || !(body.prompt as string).trim()) {
    body.prompt = body.prompt || '生成图片'
  }

  const response = await fetch(`${API_BASE_URL}/images/generations`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body)
  })
  if (!response.ok) {
    const err = await response.json().catch(() => ({}))
    throw new Error(
      (err as { detail?: string })?.detail
        ? String((err as { detail: string }).detail)
        : '图片生成失败'
    )
  }
  return response.json()
}

/**
 * 从上游响应中解析出图片 URL 或 base64 数据 URL
 */
export function getImageUrlFromResponse(res: CreateImageResponse): string | null {
  if (typeof res.url === 'string' && res.url) return res.url
  const list = res.data
  if (Array.isArray(list) && list.length > 0) {
    const first = list[0]
    if (first?.url) return first.url
    if (first?.b64_json) return `data:image/png;base64,${first.b64_json}`
  }
  return null
}
