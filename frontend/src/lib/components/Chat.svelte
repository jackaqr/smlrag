<script lang="ts">
  import * as chatApi from '$lib/api/chat'
  import * as videoApi from '$lib/api/video'
  import type { Message } from '$lib/api/chat'
  import type { VideoTaskResponse } from '$lib/api/video'
  import { activeChatId } from '$lib/stores/chatStore'
  import { log, logError } from '$lib/logger'

  type ModelType = 'text' | 'image' | 'video'

  interface ModelItem {
    id: string
    label: string
    type: ModelType
    disabled?: boolean
  }

  const modelCategories: { id: string; label: string; models: ModelItem[] }[] = [
    {
      id: 'text',
      label: '文本生成',
      models: [{ id: 'GLM-5', label: 'GLM-5', type: 'text' }]
    },
    {
      id: 'image',
      label: '图片生成',
      models: [{ id: 'image-placeholder', label: '敬请期待', type: 'image', disabled: true }]
    },
    {
      id: 'video',
      label: '视频生成',
      models: [{ id: 'jimeng', label: '即梦视频生成 3.0 Pro', type: 'video' }]
    }
  ]

  const POLL_INTERVAL_MS = 2500
  const POLL_MAX_ATTEMPTS = 120

  let inputText = $state('')
  let messages = $state<Message[]>([])
  let loading = $state(false)
  let sending = $state(false)
  let selectedModel = $state<ModelItem>(modelCategories[0].models[0])
  let showModelCard = $state(false)
  let modelCardEl = $state<HTMLDivElement | null>(null)
  let modelButtonEl = $state<HTMLButtonElement | null>(null)
  let imageFile = $state<File | null>(null)
  let imagePreview = $state<string | null>(null)
  let videoStatus = $state('')
  let extraParamsJson = $state('')
  let extraParamsError = $state('')
  /** 创建视频任务后 API 立即返回的任务信息 */
  let lastVideoTaskInfo = $state<VideoTaskResponse | null>(null)
  /** 根据 task_id 查询：输入框与状态 */
  let queryTaskId = $state('')
  let queryingTask = $state(false)
  let queryTaskError = $state('')

  const isTextMode = $derived(selectedModel.type === 'text')
  const isImageMode = $derived(selectedModel.type === 'image')
  const isVideoMode = $derived(selectedModel.type === 'video')
  const canSendImage = $derived(isVideoMode)
  const sendDisabled = $derived(isImageMode)

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

  /** 按文档：完成时响应含 video_url；兼容 raw_response.data.video_url（火山引擎等） */
  function getVideoUrlFromResult(res: VideoTaskResponse): string | null {
    if (typeof res.video_url === 'string' && res.video_url) return res.video_url
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
      const url = getVideoUrlFromResult(result)
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
    if (isTextMode && !content) return
    if (isVideoMode && !content && !imageFile) return

    sending = true
    videoStatus = ''
    if (isVideoMode) lastVideoTaskInfo = null

    try {
      if (isTextMode) {
        inputText = ''
        messages = [...messages, { role: 'user', content, timestamp: new Date().toISOString() }]
        const response = await chatApi.sendMessage($activeChatId, content, selectedModel.id)
        messages = [...messages, response]
        log('发送消息成功', { chatId: $activeChatId })
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
        await chatApi.addVideoResult($activeChatId, userContent, videoUrl)
        await loadMessages($activeChatId)
        inputText = ''
        imageFile = null
        imagePreview = null
        videoStatus = ''
        lastVideoTaskInfo = null
      }
      scrollToBottom()
    } catch (err) {
      logError(isTextMode ? '发送消息失败' : '视频生成失败', err)
      alert(err instanceof Error ? err.message : '操作失败，请重试')
      if (isTextMode && content) {
        messages = messages.slice(0, -1)
        inputText = content
      } else if (isVideoMode) {
        messages = messages.slice(0, -1)
      }
      videoStatus = ''
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
</script>

<div class="chat-container">
  {#if !$activeChatId}
    <div class="welcome">
      <h2>欢迎使用 Smlrag</h2>
      <p>点击左侧 "新对话" 开始对话</p>
    </div>
  {:else}
    <div class="messages-container">
      {#if loading}
        <div class="loading-messages">加载消息中...</div>
      {:else if messages.length === 0}
        <div class="empty-messages">
          <p>开始新的对话吧！</p>
        </div>
      {:else}
        {#each messages as message (message.timestamp)}
          <div class="message" class:user={message.role === 'user'} class:assistant={message.role === 'assistant'}>
            <div class="message-content">
              {#if message.role === 'assistant' && isUrl(message.content)}
                <p>视频结果：<a href={message.content} target="_blank" rel="noopener noreferrer">{message.content}</a></p>
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
              <div class="model-card" bind:this={modelCardEl} role="listbox" onclick={(e) => e.stopPropagation()}>
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
            <input
              type="file"
              accept="image/*"
              onchange={onImageSelect}
              class="file-input"
            />
            {#if imagePreview}
              <div class="image-preview-wrap">
                <img src={imagePreview} alt="预览" class="image-preview" />
                <button type="button" class="clear-image-btn" onclick={clearImage}>移除</button>
              </div>
            {:else}
              <span class="image-hint">可选：上传图片（图生视频）</span>
            {/if}
          </div>
        {/if}
        {#if isImageMode}
          <p class="image-mode-hint">图片生成能力敬请期待</p>
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
          {#if lastVideoTaskInfo}
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
        {/if}
        <div class="input-row">
          <input
            type="text"
            bind:value={inputText}
            placeholder={isTextMode ? '输入消息...' : isVideoMode ? '输入视频描述/提示词...' : '输入描述...'}
            onkeypress={handleKeypress}
            disabled={sending || sendDisabled}
          />
          {#if !sendDisabled && ((isTextMode && inputText) || (isVideoMode && (inputText || imageFile)))}
            <button class="send-btn" onclick={handleSend} disabled={sending}>
              {#if sending && isVideoMode && videoStatus}
                {videoStatus}
              {:else}
                {sending ? '处理中...' : '发送'}
              {/if}
            </button>
          {/if}
        </div>
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
    color: rgba(255, 255, 255, 0.7);
  }

  .welcome h2 {
    color: #ff3e00;
    margin-bottom: 1rem;
  }

  .welcome p {
    color: rgb(189, 46, 46);
    font-size: 1rem;
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
    background: rgba(255, 255, 255, 0.2);
    border-radius: 4px;
  }

  .loading-messages, .empty-messages {
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: center;
    color: rgba(255, 255, 255, 0.5);
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
    background: #ff3e00;
    color: white;
    border-bottom-right-radius: 4px;
  }

  .message.assistant .message-content {
    background: rgba(255, 255, 255, 0.08);
    color: rgba(255, 255, 255, 0.9);
    border-bottom-left-radius: 4px;
  }

  .message-content p {
    margin: 0;
    line-height: 1.5;
  }

  .message-content a {
    color: #ff8c5a;
    text-decoration: underline;
    word-break: break-all;
  }

  .message-content a:hover {
    color: #ffb380;
  }

  .message-time {
    font-size: 0.75rem;
    color: rgba(255, 255, 255, 0.4);
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
    max-width: 800px;
    padding: 1.5rem;
    background: rgba(255, 255, 255, 0.0);
    border-radius: 12px;
    border: 1px solid rgba(255, 255, 255, 0);
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0);
  }

  .model-row {
    margin-bottom: 0.75rem;
  }

  .model-selector-wrap {
    position: relative;
    display: inline-block;
  }

  .model-select-btn {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    padding: 0.4rem 0.75rem;
    font-size: 0.9rem;
    border-radius: 8px;
    border: 1px solid rgba(255, 255, 255, 0.25);
    background: rgba(0, 0, 0, 0.35);
    color: inherit;
    cursor: pointer;
  }

  .model-select-btn:hover {
    background: rgba(0, 0, 0, 0.5);
    border-color: rgba(255, 255, 255, 0.35);
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
    background: rgba(20, 20, 22, 0.98);
    border: 1px solid rgba(255, 255, 255, 0.15);
    border-radius: 12px;
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);
    z-index: 100;
  }

  .model-category {
    padding: 0 0.5rem 0.5rem;
  }

  .model-category:not(:last-child) {
    border-bottom: 1px solid rgba(255, 255, 255, 0.08);
    margin-bottom: 0.5rem;
  }

  .model-category-title {
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: rgba(255, 255, 255, 0.5);
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
    color: rgba(255, 255, 255, 0.9);
    cursor: pointer;
    border-radius: 6px;
  }

  .model-item:hover:not(.disabled) {
    background: rgba(255, 255, 255, 0.08);
  }

  .model-item.selected {
    background: rgba(255, 62, 0, 0.25);
    color: #ff8c5a;
  }

  .model-item.disabled {
    color: rgba(255, 255, 255, 0.4);
    cursor: not-allowed;
  }

  .image-mode-hint {
    font-size: 0.85rem;
    color: rgba(255, 255, 255, 0.5);
    margin: 0 0 0.5rem 0;
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
    border: 1px solid rgba(255, 255, 255, 0.2);
    background: rgba(0, 0, 0, 0.3);
    color: inherit;
  }

  .query-task-input:focus {
    outline: none;
    border-color: #ff3e00;
  }

  .query-task-input::placeholder {
    color: rgba(255, 255, 255, 0.35);
  }

  .query-task-btn {
    flex-shrink: 0;
    padding: 0.5rem 1rem;
    font-size: 0.9rem;
    border-radius: 8px;
    border: none;
    background: #ff3e00;
    color: white;
    cursor: pointer;
    font-weight: 500;
  }

  .query-task-btn:hover:not(:disabled) {
    background: #e63900;
  }

  .query-task-btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  .params-row {
    margin-bottom: 0.75rem;
  }

  .params-label {
    display: block;
    font-size: 0.85rem;
    color: rgba(255, 255, 255, 0.6);
    margin-bottom: 0.35rem;
  }

  .params-json {
    width: 100%;
    padding: 0.5rem 0.75rem;
    font-size: 0.85rem;
    font-family: ui-monospace, monospace;
    border-radius: 8px;
    border: 1px solid rgba(255, 255, 255, 0.2);
    background: rgba(0, 0, 0, 0.3);
    color: inherit;
    resize: vertical;
    min-height: 4rem;
  }

  .params-json:focus {
    outline: none;
    border-color: #ff3e00;
  }

  .params-json::placeholder {
    color: rgba(255, 255, 255, 0.35);
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
    border: 1px solid rgba(255, 255, 255, 0.12);
    border-radius: 8px;
  }

  .video-task-info-title {
    font-size: 0.85rem;
    font-weight: 600;
    color: rgba(255, 255, 255, 0.9);
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
    color: rgba(255, 255, 255, 0.5);
    margin: 0;
  }

  .video-task-info-list dd {
    margin: 0;
    color: rgba(255, 255, 255, 0.85);
    word-break: break-all;
  }

  .image-upload-row {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    margin-bottom: 0.75rem;
  }

  .file-input {
    width: auto;
    padding: 0.25rem;
    font-size: 0.85rem;
  }

  .image-hint {
    font-size: 0.9rem;
    color: rgba(255, 255, 255, 0.5);
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
    border: 1px solid rgba(255, 255, 255, 0.2);
  }

  .clear-image-btn {
    padding: 0.25rem 0.5rem;
    font-size: 0.8rem;
    border-radius: 4px;
    border: 1px solid rgba(255, 255, 255, 0.3);
    background: rgba(255, 255, 255, 0.1);
    color: inherit;
    cursor: pointer;
  }

  .clear-image-btn:hover {
    background: rgba(255, 255, 255, 0.2);
  }

  .input-row {
    position: relative;
    width: 100%;
  }

  input {
    width: 100%;
    padding: 0.8rem 6rem 0.8rem 1rem;
    font-size: 1rem;
    border-radius: 8px;
    border: 1px solid rgba(255, 255, 255, 0.15);
    background: rgba(0, 0, 0, 0.3);
    color: inherit;
    transition: border-color 0.3s, box-shadow 0.3s, background 0.3s;
  }

  input:focus {
    outline: none;
    border-color: #ff3e00;
    background: rgba(0, 0, 0, 0.4);
    box-shadow: 0 0 0 3px rgba(255, 62, 0, 0.1);
  }

  input::placeholder {
    color: rgba(255, 255, 255, 0.4);
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
    padding: 0.6rem 1.5rem;
    font-size: 0.95rem;
    border-radius: 6px;
    border: none;
    background: #ff3e00;
    color: white;
    cursor: pointer;
    font-weight: 600;
    transition: all 0.2s;
    white-space: nowrap;
  }

  .send-btn:hover:not(:disabled) {
    background: #e63900;
    box-shadow: 0 2px 6px rgba(255, 62, 0, 0.4);
  }

  .send-btn:active:not(:disabled) {
    transform: translateY(-50%) scale(0.95);
  }

  .send-btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
</style>

