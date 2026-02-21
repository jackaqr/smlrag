/**
 * 视频生成 API 客户端
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api'

export interface CreateVideoTaskParams {
  prompt: string
  model?: string
  aspect_ratio?: string
  seconds?: number
  image?: string
  /** 额外参数，与 prompt 同级平铺到请求体 */
  extraParams?: Record<string, unknown>
}

/** 查询任务响应：进行中 / 完成 / 失败，见 API 文档 */
export interface VideoTaskResponse {
  id?: string
  task_id?: string
  /** queued | in_progress | completed | failed */
  status?: string
  created_at?: string
  completed_at?: string
  model?: string
  /** 仅完成时返回，有效期 1 小时 */
  video_url?: string
  usage?: {
    seconds?: number
    video_count?: number
    size?: string
  }
  /** 仅失败时返回 */
  error?: string
  raw_response?: Record<string, unknown>
  [key: string]: unknown
}

/**
 * 提交视频生成任务（文生视频或图生视频）
 */
export async function createVideoTask(
  params: CreateVideoTaskParams
): Promise<VideoTaskResponse> {
  const body: Record<string, unknown> = {
    prompt: params.prompt,
    aspect_ratio: params.aspect_ratio ?? '16:9',
    seconds: params.seconds ?? 5
  }
  if (params.model != null) body.model = params.model
  if (params.image != null) body.image = params.image
  if (params.extraParams && Object.keys(params.extraParams).length > 0) {
    Object.assign(body, params.extraParams)
  }

  const response = await fetch(`${API_BASE_URL}/videos`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body)
  })
  if (!response.ok) {
    const err = await response.json().catch(() => ({}))
    throw new Error(
      (err as { detail?: string })?.detail
        ? String((err as { detail: string }).detail)
        : '提交视频任务失败'
    )
  }
  return response.json()
}

/**
 * 查询视频任务结果（轮询用）
 * @param taskId 创建任务时返回的 id
 * @param provider 可选，供应商名称（如 火山方舟），任务不在本地缓存时指定可加快查询
 */
export async function getVideoTaskResult(
  taskId: string,
  provider?: string
): Promise<VideoTaskResponse> {
  const url = new URL(`${API_BASE_URL}/videos/${taskId}`)
  if (provider) url.searchParams.set('provider', provider)
  const response = await fetch(url.toString(), { cache: 'no-store' })
  if (!response.ok) {
    const err = await response.json().catch(() => ({}))
    throw new Error(
      (err as { detail?: string })?.detail
        ? String((err as { detail: string }).detail)
        : '查询视频任务失败'
    )
  }
  return response.json()
}
