<script lang="ts">
  import { onMount, tick } from 'svelte'
  import * as chatApi from '$lib/api/chat'
  import * as videoApi from '$lib/api/video'
  import * as imageApi from '$lib/api/image'
  import * as configApi from '$lib/api/config'
  import type { ConfigModel } from '$lib/api/config'
  import type { Message } from '$lib/api/chat'
  import type { VideoTaskResponse } from '$lib/api/video'
  import { activeChatId } from '$lib/stores/chatStore'
  import { log, logError } from '$lib/logger'
  import { markdownToHtml } from '$lib/markdown'
  import mermaid from 'mermaid'

  type DisplayMessage = Message & { placeholder?: boolean }

  type ModelType = 'text' | 'image' | 'video'

  interface ModelItem {
    id: string
    label: string
    type: ModelType
    disabled?: boolean
  }

  const MODALITIES: { id: ModelType; label: string }[] = [
    { id: 'text', label: '文本生成' },
    { id: 'image', label: '图片生成' },
    { id: 'video', label: '视频生成' }
  ]

  const DEFAULT_MODEL_CATEGORIES: { id: string; label: string; models: ModelItem[] }[] = [
    { id: 'text', label: '文本生成', models: [{ id: 'GLM-5', label: 'GLM-5', type: 'text' }] },
    { id: 'image', label: '图片生成', models: [{ id: 'Doubao-Seedream-4.5', label: 'Doubao-Seedream-4.5', type: 'image' }] },
    { id: 'video', label: '视频生成', models: [{ id: '即梦视频生成 3.0 Pro', label: '即梦视频生成 3.0 Pro', type: 'video' }] }
  ]

  function buildModelCategoriesFromConfig(model: ConfigModel | undefined): { id: string; label: string; models: ModelItem[] }[] {
    if (!model) return DEFAULT_MODEL_CATEGORIES
    return MODALITIES.map(({ id: mod, label }) => {
      const m = model[mod as keyof ConfigModel]
      const models = m?.models && Object.keys(m.models).length > 0
        ? Object.keys(m.models).map((modelId) => ({ id: modelId, label: modelId, type: mod as ModelType }))
        : DEFAULT_MODEL_CATEGORIES.find((c) => c.id === mod)?.models ?? []
      return { id: mod, label, models }
    })
  }

  function getDefaultSelectedModel(
    categories: { id: string; label: string; models: ModelItem[] }[],
    model: ConfigModel | undefined
  ): ModelItem {
    const first = categories[0]?.models[0]
    if (!first) return DEFAULT_MODEL_CATEGORIES[0].models[0]
    if (!model) return first
    for (const cat of categories) {
      const mod = model[cat.id as keyof ConfigModel]
      const defaultId = mod?.default_model
      if (defaultId) {
        const found = cat.models.find((item) => item.id === defaultId)
        if (found) return found
      }
    }
    return first
  }

  const POLL_INTERVAL_MS = 2500
  const POLL_MAX_ATTEMPTS = 120

  let modelCategories = $state<{ id: string; label: string; models: ModelItem[] }[]>(DEFAULT_MODEL_CATEGORIES)
  let selectedModel = $state<ModelItem>(DEFAULT_MODEL_CATEGORIES[0].models[0])

  let inputText = $state('')
  let messages = $state<DisplayMessage[]>([])
  let loading = $state(false)
  let sending = $state(false)
  let showModelCard = $state(false)
  let modelCardEl = $state<HTMLDivElement | null>(null)
  let modelButtonEl = $state<HTMLButtonElement | null>(null)
  let messagesContainerEl = $state<HTMLDivElement | null>(null)
  let imageFile = $state<File | null>(null)
  let imagePreview = $state<string | null>(null)
  let videoStatus = $state('')
  let imageStatus = $state('')
  let extraParamsJson = $state('')
  let extraParamsError = $state('')
  /** 创建视频任务后 API 立即返回的任务信息 */
  let lastVideoTaskInfo = $state<VideoTaskResponse | null>(null)
  /** 根据 task_id 查询：输入框与状态 */
  let queryTaskId = $state('')
  let queryingTask = $state(false)
  let queryTaskError = $state('')
  /** 主动输入（JSON/根据任务 ID 查询）区域默认收起 */
  let showParamsPanel = $state(false)

  const isTextMode = $derived(selectedModel.type === 'text')
  const isImageMode = $derived(selectedModel.type === 'image')
  const isVideoMode = $derived(selectedModel.type === 'video')
  const canSendImage = $derived(isTextMode || isVideoMode || isImageMode)
  const sendDisabled = $derived(false)

  $effect(() => {
    if ($activeChatId) {
      loadMessages($activeChatId)
    } else {
      messages = []
    }
  })

  $effect(() => {
    if (!showModelCard) return
    const onDocClick = (e: MouseEvent) => handleClickOutside(e)
    document.addEventListener('click', onDocClick)
    return () => document.removeEventListener('click', onDocClick)
  })

  $effect(() => {
    const _ = messages
    tick().then(() => {
      const container = document.querySelector('.messages-container')
      if (container) {
        const nodes = Array.from(container.querySelectorAll('.mermaid')) as HTMLElement[]
        if (nodes.length > 0) mermaid.run({ nodes }).catch(() => {})
      }
    })
  })

  $effect(() => {
    const el = messagesContainerEl
    if (!el) return
    const onCopyClick = (e: MouseEvent) => {
      const btn = (e.target as HTMLElement).closest('.code-copy-btn')
      if (btn) handleCodeCopy(btn as HTMLElement)
    }
    el.addEventListener('click', onCopyClick)
    return () => el.removeEventListener('click', onCopyClick)
  })

  onMount(async () => {
    mermaid.initialize({
      startOnLoad: false,
      theme: 'neutral',
      securityLevel: 'loose'
    })
    try {
      const cfg = await configApi.getConfig()
      const categories = buildModelCategoriesFromConfig(cfg.model)
      modelCategories = categories
      selectedModel = getDefaultSelectedModel(categories, cfg.model)
    } catch (err) {
      logError('加载配置失败，使用默认模型列表', err)
    }
  })

  async function loadMessages(chatId: string) {
    log('加载消息', { chatId })
    loading = true
    try {
      messages = await chatApi.getMessages(chatId)
      log('加载消息成功', { chatId, count: messages.length })
    } catch (err) {
      logError('加载消息失败', err)
      messages = []
    } finally {
      loading = false
    }
  }

  function getTaskIdFromResponse(res: VideoTaskResponse): string | null {
    if (typeof res.task_id === 'string') return res.task_id
    if (typeof res.id === 'string') return res.id
    return null
  }

  /** 按文档：完成时响应含 video_url；兼容 data / raw_response 等嵌套 */
  function getVideoUrlFromResult(res: VideoTaskResponse): string | null {
    if (typeof res.video_url === 'string' && res.video_url) return res.video_url
    const withData = res as { data?: { video_url?: string } }
    if (withData.data?.video_url && typeof withData.data.video_url === 'string') return withData.data.video_url
    const raw = res.raw_response as { data?: { video_url?: string } } | undefined
    if (raw?.data?.video_url && typeof raw.data.video_url === 'string') return raw.data.video_url
    if (res.output && typeof (res.output as { url?: string }).url === 'string') {
      return (res.output as { url: string }).url
    }
    if (typeof res.result_url === 'string') return res.result_url
    if (typeof res.url === 'string') return res.url
    if (typeof res.output === 'string' && /^https?:\/\//.test(res.output)) return res.output
    return null
  }

  /** 文档：queued / in_progress / completed / failed */
  function isFailedStatus(status: unknown): boolean {
    if (typeof status !== 'string') return false
    return status.toLowerCase() === 'failed'
  }

  async function pollVideoTask(taskId: string): Promise<string> {
    for (let i = 0; i < POLL_MAX_ATTEMPTS; i++) {
      const result = await videoApi.getVideoTaskResult(taskId)
      lastVideoTaskInfo = result
      let url = getVideoUrlFromResult(result)
      if (!url && result.status === 'completed') {
        const withData = result as { data?: { video_url?: string } }
        url = withData.data?.video_url || (result.raw_response as { data?: { video_url?: string } })?.data?.video_url || null
      }
      if (url) return url
      if (isFailedStatus(result.status)) {
        const msg = typeof result.error === 'string' && result.error
          ? result.error
          : result.status || '任务失败'
        throw new Error(msg)
      }
      const status = result.status || 'queued'
      videoStatus = `生成中… ${status} (${i + 1}/${POLL_MAX_ATTEMPTS})`
      await new Promise((r) => setTimeout(r, POLL_INTERVAL_MS))
    }
    throw new Error('生成超时')
  }

  async function handleSend() {
    if (!$activeChatId || sending || sendDisabled) return
    const content = inputText.trim()
    if (isTextMode && !content && !imageFile) return
    if (isVideoMode && !content && !imageFile) return
    if (isImageMode && !content && !imageFile) return

    sending = true
    videoStatus = ''
    imageStatus = ''
    if (isVideoMode) lastVideoTaskInfo = null

    try {
      if (isTextMode) {
        const userContent = content || (imageFile ? '[图片]' : '')
        inputText = ''
        messages = [...messages, { role: 'user', content: userContent, timestamp: new Date().toISOString() }]
        messages = [...messages, { role: 'assistant', content: '', timestamp: new Date().toISOString(), placeholder: true }]
        scrollToBottom()
        let imageBase64: string | undefined
        if (imageFile) imageBase64 = await fileToBase64(imageFile)
        const response = await chatApi.sendMessage($activeChatId, content || (imageFile ? '请根据图片内容回复' : ''), selectedModel.id, imageBase64)
        messages = [...messages.slice(0, -1), response]
        imageFile = null
        imagePreview = null
        log('发送消息成功', { chatId: $activeChatId })
      } else if (isImageMode) {
        let bodyFromJson: Record<string, unknown> | null = null
        if (extraParamsJson.trim()) {
          try {
            const parsed = JSON.parse(extraParamsJson.trim())
            if (parsed !== null && typeof parsed === 'object' && !Array.isArray(parsed)) {
              bodyFromJson = parsed as Record<string, unknown>
            }
          } catch {
            extraParamsError = '请求体 JSON 格式错误'
            sending = false
            return
          }
        }
        extraParamsError = ''
        const userContent = content || (imageFile ? '图生图' : '文生图')
        messages = [...messages, { role: 'user', content: userContent, timestamp: new Date().toISOString() }]
        imageStatus = '生成中…'
        let imageBase64: string | undefined
        if (imageFile) imageBase64 = await fileToBase64(imageFile)
        const createRes = await imageApi.createImage({
          body: bodyFromJson ?? undefined,
          prompt: content || (bodyFromJson?.prompt as string) || (imageFile ? '根据图片生成' : '生成图片'),
          image: imageBase64
        })
        const imageUrl = imageApi.getImageUrlFromResponse(createRes)
        if (!imageUrl) throw new Error('未返回图片地址')
        imageStatus = '正在写入对话…'
        await chatApi.addImageResult($activeChatId, userContent, imageUrl)
        await loadMessages($activeChatId)
        inputText = ''
        imageFile = null
        imagePreview = null
        imageStatus = ''
      } else if (isVideoMode) {
        let extraParams: Record<string, unknown> = {}
        if (extraParamsJson.trim()) {
          try {
            const parsed = JSON.parse(extraParamsJson.trim())
            if (parsed !== null && typeof parsed === 'object' && !Array.isArray(parsed)) {
              extraParams = parsed as Record<string, unknown>
            }
          } catch {
            extraParamsError = '参数 JSON 格式错误'
            sending = false
            return
          }
        }
        extraParamsError = ''
        const userContent = content || (imageFile ? '图生视频' : '文生视频')
        messages = [...messages, { role: 'user', content: userContent, timestamp: new Date().toISOString() }]
        let imageBase64: string | undefined
        if (imageFile) imageBase64 = await fileToBase64(imageFile)
        const createRes = await videoApi.createVideoTask({
          prompt: content || '根据图片生成视频',
          image: imageBase64,
          extraParams: Object.keys(extraParams).length > 0 ? extraParams : undefined
        })
        lastVideoTaskInfo = createRes
        const taskId = getTaskIdFromResponse(createRes)
        if (!taskId) throw new Error('未返回任务 ID')
        videoStatus = '提交成功，等待生成…'
        const videoUrl = await pollVideoTask(taskId)
        videoStatus = '正在写入对话…'
        const writeTimeoutMs = 15000
        await Promise.race([
          (async () => {
            await chatApi.addVideoResult($activeChatId, userContent, videoUrl)
            await loadMessages($activeChatId)
          })(),
          new Promise((_, reject) => setTimeout(() => reject(new Error('写入对话超时')), writeTimeoutMs))
        ])
        inputText = ''
        imageFile = null
        imagePreview = null
        videoStatus = ''
        lastVideoTaskInfo = null
      }
      scrollToBottom()
    } catch (err) {
      logError(
        isTextMode ? '发送消息失败' : isImageMode ? '图片生成失败' : '视频生成失败',
        err
      )
      alert(err instanceof Error ? err.message : '操作失败，请重试')
      if (isTextMode && content) {
        messages = messages.slice(0, -2)
        inputText = content
      } else if (isVideoMode || isImageMode) {
        messages = messages.slice(0, -1)
      }
      videoStatus = ''
      imageStatus = ''
    } finally {
      sending = false
    }
  }

  function selectModel(item: ModelItem) {
    if (item.disabled) return
    selectedModel = item
    showModelCard = false
  }

  function handleClickOutside(e: MouseEvent) {
    if (
      showModelCard &&
      modelCardEl &&
      modelButtonEl &&
      !modelCardEl.contains(e.target as Node) &&
      !modelButtonEl.contains(e.target as Node)
    ) {
      showModelCard = false
    }
  }

  function fileToBase64(file: File): Promise<string> {
    return new Promise((resolve, reject) => {
      const reader = new FileReader()
      reader.onload = () => {
        const result = reader.result
        if (typeof result === 'string') resolve(result)
        else reject(new Error('读取文件失败'))
      }
      reader.onerror = () => reject(reader.error)
      reader.readAsDataURL(file)
    })
  }

  function onImageSelect(e: Event) {
    const input = e.target as HTMLInputElement
    const file = input.files?.[0]
    if (!file || !file.type.startsWith('image/')) return
    imageFile = file
    const reader = new FileReader()
    reader.onload = () => {
      imagePreview = typeof reader.result === 'string' ? reader.result : null
    }
    reader.readAsDataURL(file)
  }

  function clearImage() {
    imageFile = null
    imagePreview = null
  }

  function onPasteImage(e: ClipboardEvent) {
    if (!canSendImage) return
    const items = e.clipboardData?.items
    if (!items) return
    for (const item of items) {
      if (item.type.startsWith('image/')) {
        const file = item.getAsFile()
        if (!file) return
        e.preventDefault()
        imageFile = file
        const reader = new FileReader()
        reader.onload = () => {
          imagePreview = typeof reader.result === 'string' ? reader.result : null
        }
        reader.readAsDataURL(file)
        return
      }
    }
  }

  function handleKeypress(event: KeyboardEvent) {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault()
      handleSend()
    }
  }

  function scrollToBottom() {
    setTimeout(() => {
      const container = document.querySelector('.messages-container')
      if (container) container.scrollTop = container.scrollHeight
    }, 100)
  }

  function isUrl(content: string): boolean {
    return /^https?:\/\//.test(content.trim())
  }

  function isImageUrl(content: string): boolean {
    const s = content.trim()
    if (/^data:image\//i.test(s)) return true
    if (/^https?:\/\//i.test(s) && /\.(png|jpe?g|gif|webp)(\?|$)/i.test(s)) return true
    return false
  }

  async function queryTaskById() {
    const id = queryTaskId.trim()
    if (!id || queryingTask) return
    queryingTask = true
    queryTaskError = ''
    try {
      const result = await videoApi.getVideoTaskResult(id)
      lastVideoTaskInfo = result
    } catch (err) {
      queryTaskError = err instanceof Error ? err.message : '查询失败'
    } finally {
      queryingTask = false
    }
  }

  async function handleCodeCopy(btn: HTMLElement) {
    const code = btn.getAttribute('data-code')
    if (code == null) return
    try {
      await navigator.clipboard.writeText(code)
      const orig = btn.textContent
      btn.textContent = '已复制'
      btn.classList.add('copied')
      setTimeout(() => {
        btn.textContent = orig
        btn.classList.remove('copied')
      }, 1500)
    } catch {
      btn.textContent = '复制失败'
      setTimeout(() => { btn.textContent = '复制' }, 1500)
    }
  }
</script>

<div class="chat-container">
  {#if !$activeChatId}
    <div class="welcome">
      <div class="welcome-icon">💬</div>
      <h2>欢迎使用 Smlrag</h2>
      <p>在左侧点击「新对话」即可开始文本、图片或视频生成</p>
    </div>
  {:else}
    <div class="messages-container" bind:this={messagesContainerEl}>
      {#if loading}
        <div class="loading-messages">加载消息中...</div>
      {:else if messages.length === 0}
        <div class="empty-messages">
          <span class="empty-icon">✨</span>
          <p>开始新的对话吧</p>
        </div>
      {:else}
        {#each messages as message (message.placeholder ? `placeholder-${message.timestamp}` : message.timestamp)}
          <div class="message" class:user={message.role === 'user'} class:assistant={message.role === 'assistant'}>
            <div class="message-content">
              {#if message.role === 'assistant' && message.placeholder}
                <div class="message-placeholder" aria-label="思考中">
                  <span class="dot"></span><span class="dot"></span><span class="dot"></span>
                </div>
              {:else if message.role === 'assistant' && isImageUrl(message.content)}
                <p class="result-label">图片结果：</p>
                <img src={message.content} alt="生成图片" class="message-result-image" />
                <a href={message.content} target="_blank" rel="noopener noreferrer">打开原图</a>
              {:else if message.role === 'assistant' && isUrl(message.content)}
                <p>视频结果：<a href={message.content} target="_blank" rel="noopener noreferrer">{message.content}</a></p>
              {:else if message.role === 'assistant'}
                <div class="markdown-body">{@html markdownToHtml(message.content)}</div>
              {:else}
                <p>{message.content}</p>
              {/if}
            </div>
            <span class="message-time">{new Date(message.timestamp).toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })}</span>
          </div>
        {/each}
      {/if}
    </div>

    <div class="input-container">
      <div class="input-wrapper">
          {#if showParamsPanel}
            {#if isImageMode}
              <div class="params-row">
                <label class="params-label" for="image-params-json">请求体（JSON，参数平铺，与 video 接口一致）</label>
                <textarea
                  id="image-params-json"
                  class="params-json"
                  bind:value={extraParamsJson}
                  placeholder={'{"model":"Doubao-Seedream-4.5","prompt":"","negative_prompt":"","image":"","extra_body":{"provider":{"only":[],"order":[],"sort":null}}}'}
                  rows="5"
                  disabled={sending}
                ></textarea>
                {#if extraParamsError}
                  <span class="params-error">{extraParamsError}</span>
                {/if}
              </div>
            {/if}
            {#if isVideoMode}
              <div class="query-task-row">
                <label class="params-label" for="query-task-id">根据任务 ID 查询</label>
                <div class="query-task-input-wrap">
                  <input
                    id="query-task-id"
                    type="text"
                    class="query-task-input"
                    bind:value={queryTaskId}
                    placeholder="输入创建任务时返回的 id"
                    disabled={queryingTask || sending}
                  />
                  <button
                    type="button"
                    class="query-task-btn"
                    onclick={queryTaskById}
                    disabled={!queryTaskId.trim() || queryingTask || sending}
                  >
                    {queryingTask ? '查询中...' : '查询'}
                  </button>
                </div>
                {#if queryTaskError}
                  <span class="params-error">{queryTaskError}</span>
                {/if}
              </div>
              <div class="params-row">
                <label class="params-label" for="extra-params-json">参数配置（JSON，与 prompt 同级平铺）</label>
                <textarea
                  id="extra-params-json"
                  class="params-json"
                  bind:value={extraParamsJson}
                  placeholder={'{"aspect_ratio":"16:9","seconds":5}'}
                  rows="3"
                  disabled={sending}
                ></textarea>
                {#if extraParamsError}
                  <span class="params-error">{extraParamsError}</span>
                {/if}
              </div>
            {/if}
          {/if}
        <div class="input-and-actions-row" onpaste={onPasteImage}>
        <div class="input-actions-row">
          <div class="model-row">
            <div class="model-selector-wrap">
            <button
              type="button"
              class="model-select-btn"
              bind:this={modelButtonEl}
              onclick={() => (showModelCard = !showModelCard)}
              aria-expanded={showModelCard}
            >
              <span class="model-select-label">{selectedModel.label}</span>
              <span class="model-select-arrow" class:open={showModelCard}>▾</span>
            </button>
            {#if showModelCard}
              <div
                class="model-card"
                bind:this={modelCardEl}
                role="listbox"
                tabindex="0"
                onclick={(e) => e.stopPropagation()}
                onkeydown={(e) => e.stopPropagation()}
              >
                {#each modelCategories as category}
                  <div class="model-category">
                    <div class="model-category-title">{category.label}</div>
                    <ul class="model-list">
                      {#each category.models as item}
                        <li>
                          <button
                            type="button"
                            class="model-item"
                            class:selected={selectedModel.id === item.id}
                            class:disabled={item.disabled}
                            onclick={() => selectModel(item)}
                            disabled={item.disabled}
                          >
                            {item.label}
                          </button>
                        </li>
                      {/each}
                    </ul>
                  </div>
                {/each}
              </div>
            {/if}
            </div>
          </div>
          {#if canSendImage}
          <div class="image-upload-row">
            <label class="file-input-label">
              <input
                type="file"
                accept="image/*"
                onchange={onImageSelect}
                class="file-input"
              />
              <span class="file-input-btn">选择图片</span>
            </label>
            {#if imagePreview}
              <div class="image-preview-wrap">
                <img src={imagePreview} alt="预览" class="image-preview" />
                <button type="button" class="clear-image-btn" onclick={clearImage}>移除</button>
              </div>
            {:else}
              <span class="image-hint">
                {#if isTextMode}
                  可选：上传图片或从剪贴板粘贴（多模态输入）
                {:else if isImageMode}
                  可选：上传图片或从剪贴板粘贴（图生图）
                {:else}
                  可选：上传图片或从剪贴板粘贴（图生视频）
                {/if}
              </span>
            {/if}
          </div>
          {/if}
          {#if isImageMode || isVideoMode}
          <div class="params-panel-toggle-wrap">
            <button
              type="button"
              class="params-panel-toggle"
              onclick={() => (showParamsPanel = !showParamsPanel)}
              aria-expanded={showParamsPanel}
            >
              <span class="params-panel-toggle-arrow" class:open={showParamsPanel}>▾</span>
              <span>主动输入{isImageMode ? '（请求体 JSON）' : '（根据任务 ID 查询 / 参数 JSON）'}</span>
            </button>
          </div>
          {/if}
        </div>
        <div class="input-row">
          <input
            type="text"
            bind:value={inputText}
            placeholder={isTextMode ? '输入消息...' : isVideoMode ? '输入视频描述/提示词...' : isImageMode ? '输入图片描述/提示词...' : '输入描述...'}
            onkeypress={handleKeypress}
            disabled={sending || sendDisabled}
          />
          {#if !sendDisabled && ((isTextMode && (inputText || imageFile)) || (isVideoMode && (inputText || imageFile)) || (isImageMode && (inputText || imageFile)))}
            <button class="send-btn" onclick={handleSend} disabled={sending}>
              {#if sending && isVideoMode && videoStatus}
                {videoStatus}
              {:else if sending && isImageMode && imageStatus}
                {imageStatus}
              {:else}
                {sending ? '处理中...' : '发送'}
              {/if}
            </button>
          {/if}
        </div>
        </div>
        {#if isVideoMode && lastVideoTaskInfo}
          <div class="video-task-info">
              <div class="video-task-info-title">
                {lastVideoTaskInfo.status === 'completed' ? '任务已完成' : '任务状态'}
              </div>
              <dl class="video-task-info-list">
                {#if lastVideoTaskInfo.id != null}
                  <dt>ID</dt>
                  <dd>{lastVideoTaskInfo.id}</dd>
                {/if}
                {#if lastVideoTaskInfo.status != null}
                  <dt>状态</dt>
                  <dd>{String(lastVideoTaskInfo.status)}</dd>
                {/if}
                {#if lastVideoTaskInfo.created_at != null}
                  <dt>创建时间</dt>
                  <dd>{String(lastVideoTaskInfo.created_at)}</dd>
                {/if}
                {#if lastVideoTaskInfo.completed_at != null}
                  <dt>完成时间</dt>
                  <dd>{String(lastVideoTaskInfo.completed_at)}</dd>
                {/if}
                {#if lastVideoTaskInfo.model != null}
                  <dt>模型</dt>
                  <dd>{String(lastVideoTaskInfo.model)}</dd>
                {/if}
                {#if lastVideoTaskInfo.seconds != null}
                  <dt>时长</dt>
                  <dd>{String(lastVideoTaskInfo.seconds)} 秒</dd>
                {:else if lastVideoTaskInfo.usage?.seconds != null}
                  <dt>时长</dt>
                  <dd>{String(lastVideoTaskInfo.usage.seconds)} 秒</dd>
                {/if}
                {#if lastVideoTaskInfo.size != null}
                  <dt>尺寸</dt>
                  <dd>{String(lastVideoTaskInfo.size)}</dd>
                {:else if lastVideoTaskInfo.usage?.size != null}
                  <dt>尺寸</dt>
                  <dd>{String(lastVideoTaskInfo.usage.size)}</dd>
                {/if}
                {#if lastVideoTaskInfo.status === 'completed'}
                  {@const _url = getVideoUrlFromResult(lastVideoTaskInfo)}
                  {#if _url}
                    <dt>视频</dt>
                    <dd><a href={_url} target="_blank" rel="noopener noreferrer">打开链接</a></dd>
                  {/if}
                {/if}
              </dl>
            </div>
          {/if}
      </div>
    </div>
  {/if}
</div>

<style>
  .chat-container {
    width: 100%;
    height: 100%;
    display: flex;
    flex-direction: column;
  }

  .welcome {
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    color: var(--text-secondary);
    padding: 2rem;
    text-align: center;
  }

  .welcome-icon {
    font-size: 4rem;
    margin-bottom: 1rem;
    opacity: 0.9;
    filter: drop-shadow(0 4px 12px rgba(142, 164, 202, 0.3));
  }

  .welcome h2 {
    font-size: 1.75rem;
    font-weight: 600;
    color: var(--color-brand);
    margin-bottom: 0.5rem;
  }

  .welcome p {
    color: var(--text-muted);
    font-size: 1rem;
    max-width: 320px;
  }

  .messages-container {
    flex: 1;
    overflow-y: auto;
    padding: 2rem;
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }

  .messages-container::-webkit-scrollbar {
    width: 8px;
  }

  .messages-container::-webkit-scrollbar-track {
    background: transparent;
  }

  .messages-container::-webkit-scrollbar-thumb {
    background: var(--color-primary-muted);
    border-radius: 4px;
  }

  .loading-messages, .empty-messages {
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 0.75rem;
    color: var(--text-muted);
  }

  .empty-icon {
    font-size: 2.5rem;
    opacity: 0.8;
  }

  .message {
    display: flex;
    flex-direction: column;
    max-width: 70%;
    animation: slideIn 0.3s ease-out;
  }

  @keyframes slideIn {
    from {
      opacity: 0;
      transform: translateY(10px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }

  .message.user {
    align-self: flex-end;
  }

  .message.assistant {
    align-self: flex-start;
  }

  .message-content {
    padding: 1rem 1.25rem;
    border-radius: 12px;
    word-wrap: break-word;
  }

  .message.user .message-content {
    background: var(--gradient-primary);
    color: #fff;
    border-bottom-right-radius: 4px;
    box-shadow: 0 2px 12px rgba(142, 164, 202, 0.25);
  }

  .message.assistant .message-content {
    background: var(--bg-elevated);
    border: 1px solid var(--border-subtle);
    color: var(--text-primary);
    border-bottom-left-radius: 4px;
  }

  .message-placeholder {
    display: flex;
    align-items: center;
    gap: 4px;
    padding: 2px 0;
    min-height: 1.5em;
  }

  .message-placeholder .dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: var(--text-muted);
    animation: placeholder-bounce 1.4s ease-in-out infinite both;
  }

  .message-placeholder .dot:nth-child(1) { animation-delay: 0s; }
  .message-placeholder .dot:nth-child(2) { animation-delay: 0.2s; }
  .message-placeholder .dot:nth-child(3) { animation-delay: 0.4s; }

  @keyframes placeholder-bounce {
    0%, 80%, 100% { transform: scale(0.6); opacity: 0.6; }
    40% { transform: scale(1); opacity: 1; }
  }

  .message-content p {
    margin: 0;
    line-height: 1.5;
  }

  .message-content a {
    color: var(--color-accent);
    text-decoration: none;
    word-break: break-all;
    border-bottom: 1px solid transparent;
    transition: border-color 0.2s, color 0.2s;
  }

  .message-content a:hover {
    color: var(--color-primary-hover);
    border-bottom-color: currentColor;
  }

  .message-content .result-label {
    margin-bottom: 0.5rem;
  }

  .message-content .markdown-body {
    width: 100%;
    min-width: 0;
  }

  .message-content .markdown-body :global(p) {
    margin: 0 0 0.75em;
    line-height: 1.6;
  }

  .message-content .markdown-body :global(p:last-child) {
    margin-bottom: 0;
  }

  .message-content .markdown-body :global(h1),
  .message-content .markdown-body :global(h2),
  .message-content .markdown-body :global(h3) {
    margin: 1em 0 0.5em;
    font-weight: 600;
    line-height: 1.3;
  }

  .message-content .markdown-body :global(h1) { font-size: 1.25em; }
  .message-content .markdown-body :global(h2) { font-size: 1.1em; }
  .message-content .markdown-body :global(h3) { font-size: 1em; }

  .message-content .markdown-body :global(ul),
  .message-content .markdown-body :global(ol) {
    margin: 0.5em 0;
    padding-left: 1.5em;
  }

  .message-content .markdown-body :global(li) {
    margin: 0.25em 0;
  }

  .message-content .markdown-body :global(.code-block-wrap) {
    position: relative;
    margin: 0.75em 0;
  }

  .message-content .markdown-body :global(.code-copy-btn) {
    position: absolute;
    top: 0.5rem;
    right: 0.5rem;
    z-index: 2;
    padding: 0.25rem 0.6rem;
    font-size: 0.75rem;
    font-weight: 500;
    color: var(--text-muted);
    background: var(--bg-elevated);
    border: 1px solid var(--border-default);
    border-radius: var(--radius-sm);
    cursor: pointer;
    transition: color 0.2s, background 0.2s, border-color 0.2s;
  }

  .message-content .markdown-body :global(.code-copy-btn:hover) {
    color: var(--color-brand);
    background: var(--color-primary-muted);
    border-color: var(--color-primary);
  }

  .message-content .markdown-body :global(.code-copy-btn.copied) {
    color: var(--color-accent);
    border-color: var(--color-accent);
  }

  .message-content .markdown-body :global(pre) {
    margin: 0;
    padding: 2.25rem 1rem 1rem 1rem;
    border-radius: var(--radius-md);
    background: var(--bg-base);
    border: 1px solid var(--border-subtle);
    overflow-x: auto;
    font-size: 0.875rem;
    line-height: 1.5;
  }

  .message-content .markdown-body :global(pre code) {
    padding: 0;
    background: none;
    border: none;
    font-size: inherit;
  }

  .message-content .markdown-body :global(code) {
    padding: 0.2em 0.4em;
    border-radius: 4px;
    background: var(--bg-base);
    border: 1px solid var(--border-subtle);
    font-size: 0.9em;
    font-family: ui-monospace, monospace;
  }

  .message-content .markdown-body :global(.mermaid) {
    margin: 1em 0;
    text-align: center;
    overflow-x: auto;
  }

  .message-content .markdown-body :global(.mermaid svg) {
    max-width: 100%;
    height: auto;
  }

  .message-content .markdown-body :global(blockquote) {
    margin: 0.75em 0;
    padding-left: 1em;
    border-left: 3px solid var(--color-primary);
    color: var(--text-muted);
  }

  .message-content .markdown-body :global(hr) {
    margin: 1em 0;
    border: none;
    border-top: 1px solid var(--border-default);
  }

  .message-content .markdown-body :global(table) {
    border-collapse: collapse;
    font-size: 0.9em;
    margin: 0.75em 0;
  }

  .message-content .markdown-body :global(th),
  .message-content .markdown-body :global(td) {
    border: 1px solid var(--border-default);
    padding: 0.4em 0.75em;
    text-align: left;
  }

  .message-content .markdown-body :global(th) {
    background: var(--bg-base);
    font-weight: 600;
  }

  .message-content .message-result-image {
    display: block;
    max-width: 100%;
    max-height: 320px;
    border-radius: 8px;
    margin-bottom: 0.5rem;
  }

  .message-time {
    font-size: 0.75rem;
    color: var(--text-muted);
    margin-top: 0.25rem;
    padding: 0 0.5rem;
  }

  .message.user .message-time {
    text-align: right;
  }

  .input-container {
    padding: 2rem;
    display: flex;
    justify-content: center;
    align-items: center;
  }

  .input-wrapper {
    width: 100%;
    max-width: 1100px;
    padding: 1.25rem 1.5rem;
    background: var(--bg-elevated);
    border-radius: var(--radius-lg);
    border: 1px solid var(--border-default);
    box-shadow: var(--shadow-sm);
  }

  .input-and-actions-row {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 0.75rem;
    margin-bottom: 0.75rem;
    width: 100%;
  }

  .input-actions-row {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 0.5rem;
    margin-bottom: 0;
    flex-shrink: 0;
  }

  .model-row {
    margin-bottom: 0;
  }

  .model-selector-wrap {
    position: relative;
    display: inline-block;
  }

  .model-select-btn {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    padding: 0.45rem 0.85rem;
    font-size: 0.9rem;
    border-radius: var(--radius-md);
    border: 1px solid var(--border-default);
    background: var(--bg-base);
    color: var(--color-brand);
    cursor: pointer;
    transition: border-color 0.2s, background 0.2s;
  }

  .model-select-btn:hover {
    background: var(--color-primary-muted);
    border-color: var(--color-primary);
  }

  .model-select-label {
    font-weight: 500;
  }

  .model-select-arrow {
    font-size: 0.7rem;
    opacity: 0.8;
    transition: transform 0.2s;
  }

  .model-select-arrow.open {
    transform: rotate(180deg);
  }

  .model-card {
    position: absolute;
    left: 0;
    bottom: 100%;
    margin-bottom: 0.5rem;
    min-width: 220px;
    max-height: 320px;
    overflow-y: auto;
    padding: 0.5rem 0;
    background: #fff;
    border: 1px solid var(--border-default);
    border-radius: 12px;
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
    z-index: 100;
  }

  .model-category {
    padding: 0 0.5rem 0.5rem;
  }

  .model-category:not(:last-child) {
    border-bottom: 1px solid var(--border-subtle);
    margin-bottom: 0.5rem;
  }

  .model-category-title {
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: #64748b;
    padding: 0.25rem 0.5rem;
    margin-bottom: 0.25rem;
  }

  .model-list {
    list-style: none;
    margin: 0;
    padding: 0;
  }

  .model-list li {
    margin: 0;
  }

  .model-item {
    display: block;
    width: 100%;
    text-align: left;
    padding: 0.5rem 0.75rem;
    font-size: 0.9rem;
    border: none;
    background: transparent;
    color: #1e293b;
    cursor: pointer;
    border-radius: 6px;
  }

  .model-item:hover:not(.disabled) {
    background: var(--color-primary-muted);
    color: var(--color-primary);
  }

  .model-item.selected {
    background: var(--color-primary-muted);
    color: var(--color-primary);
  }

  .model-item.disabled {
    color: #94a3b8;
    cursor: not-allowed;
  }


  .query-task-row {
    margin-bottom: 0.75rem;
  }

  .query-task-input-wrap {
    display: flex;
    gap: 0.5rem;
    align-items: center;
  }

  .query-task-input {
    flex: 1;
    min-width: 0;
    padding: 0.5rem 0.75rem;
    font-size: 0.9rem;
    border-radius: 8px;
    border: 1px solid var(--border-default);
    background: #fff;
    color: var(--text-primary);
  }

  .query-task-input:focus {
    outline: none;
    border-color: var(--color-primary);
  }

  .query-task-input::placeholder {
    color: var(--text-muted);
  }

  .query-task-btn {
    flex-shrink: 0;
    padding: 0.5rem 1rem;
    font-size: 0.9rem;
    border-radius: var(--radius-md);
    border: none;
    background: var(--gradient-primary);
    color: var(--color-brand);
    cursor: pointer;
    font-weight: 500;
  }

  .query-task-btn:hover:not(:disabled) {
    filter: brightness(1.08);
  }

  .query-task-btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  .params-panel-toggle-wrap {
    margin-bottom: 0;
  }

  .params-panel-toggle {
    display: inline-flex;
    align-items: center;
    gap: 0.35rem;
    padding: 0.4rem 0.5rem;
    font-size: 0.88rem;
    font-family: inherit;
    color: var(--text-secondary);
    background: transparent;
    border: none;
    border-radius: var(--radius-sm);
    cursor: pointer;
    transition: color 0.2s, background 0.2s;
  }

  .params-panel-toggle:hover {
    color: var(--color-primary);
    background: var(--color-primary-muted);
  }

  .params-panel-toggle-arrow {
    display: inline-block;
    transition: transform 0.2s;
  }

  .params-panel-toggle-arrow.open {
    transform: rotate(180deg);
  }

  .params-row {
    margin-bottom: 0.75rem;
  }

  .params-label {
    display: block;
    font-size: 0.85rem;
    color: var(--text-secondary);
    margin-bottom: 0.35rem;
  }

  .params-json {
    width: 100%;
    padding: 0.5rem 0.75rem;
    font-size: 0.85rem;
    font-family: ui-monospace, monospace;
    border-radius: 8px;
    border: 1px solid var(--border-default);
    background: #fff;
    color: var(--text-primary);
    resize: vertical;
    min-height: 4rem;
  }

  .params-json:focus {
    outline: none;
    border-color: var(--color-primary);
  }

  .params-json::placeholder {
    color: var(--text-muted);
  }

  .params-error {
    display: block;
    font-size: 0.8rem;
    color: #ff6b6b;
    margin-top: 0.25rem;
  }

  .video-task-info {
    margin-bottom: 0.75rem;
    padding: 0.75rem 1rem;
    background: rgba(0, 0, 0, 0.35);
    border: 1px solid var(--border-subtle);
    border-radius: 8px;
  }

  .video-task-info-title {
    font-size: 0.85rem;
    font-weight: 600;
    color: var(--text-primary);
    margin-bottom: 0.5rem;
  }

  .video-task-info-list {
    display: grid;
    grid-template-columns: auto 1fr;
    gap: 0.25rem 1rem;
    margin: 0;
    font-size: 0.8rem;
  }

  .video-task-info-list dt {
    color: var(--text-muted);
    margin: 0;
  }

  .video-task-info-list dd {
    margin: 0;
    color: var(--text-primary);
    word-break: break-all;
  }

  .image-upload-row {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    margin-bottom: 0;
  }

  .file-input-label {
    display: inline-flex;
    cursor: pointer;
    position: relative;
  }

  .file-input {
    position: absolute;
    inset: 0;
    width: 100%;
    height: 100%;
    opacity: 0;
    cursor: pointer;
    font-size: 0;
  }

  .file-input-btn {
    display: inline-flex;
    align-items: center;
    gap: 0.35rem;
    padding: 0.5rem 1rem;
    font-size: 0.9rem;
    font-weight: 500;
    font-family: inherit;
    color: var(--text-primary);
    background: var(--bg-elevated);
    border: 1px solid var(--border-default);
    border-radius: var(--radius-md);
    box-shadow: var(--shadow-sm);
    transition: border-color 0.2s, background 0.2s, box-shadow 0.2s;
  }

  .file-input-label:hover .file-input-btn {
    border-color: var(--color-primary);
    background: var(--color-primary-muted);
    box-shadow: 0 0 0 1px var(--color-primary-muted);
  }

  .file-input-label:focus-within .file-input-btn {
    outline: none;
    border-color: var(--color-primary);
    box-shadow: 0 0 0 3px var(--color-primary-muted);
  }

  .image-hint {
    font-size: 0.9rem;
    color: var(--text-muted);
  }

  .image-preview-wrap {
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }

  .image-preview {
    max-width: 80px;
    max-height: 60px;
    object-fit: contain;
    border-radius: 6px;
    border: 1px solid var(--border-default);
  }

  .clear-image-btn {
    padding: 0.25rem 0.5rem;
    font-size: 0.8rem;
    border-radius: 4px;
    border: 1px solid var(--border-default);
    background: var(--color-primary-muted);
    color: inherit;
    cursor: pointer;
  }

  .clear-image-btn:hover {
    background: var(--color-primary-muted);
  }

  .input-row {
    position: relative;
    flex: 1 1 100%;
    min-width: 0;
  }

  input {
    width: 100%;
    padding: 0.8rem 6rem 0.8rem 1rem;
    font-size: 1rem;
    border-radius: var(--radius-md);
    border: 1px solid var(--border-default);
    background: var(--bg-base);
    color: var(--text-primary);
    transition: border-color 0.2s, box-shadow 0.2s;
  }

  input:focus {
    outline: none;
    border-color: var(--color-primary);
    box-shadow: 0 0 0 3px var(--color-primary-muted);
  }

  input::placeholder {
    color: var(--text-muted);
  }

  input:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  .send-btn {
    position: absolute;
    right: 0.4rem;
    top: 50%;
    transform: translateY(-50%);
    padding: 0.55rem 1.25rem;
    font-size: 0.9rem;
    border-radius: var(--radius-sm);
    border: none;
    background: var(--gradient-primary);
    color: var(--color-brand);
    cursor: pointer;
    font-weight: 600;
    transition: all 0.2s;
    white-space: nowrap;
    box-shadow: 0 2px 8px rgba(142, 164, 202, 0.3);
  }

  .send-btn:hover:not(:disabled) {
    filter: brightness(1.08);
    box-shadow: 0 2px 12px rgba(142, 164, 202, 0.4);
  }

  .send-btn:active:not(:disabled) {
    transform: translateY(-50%) scale(0.95);
  }

  .send-btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
</style>

