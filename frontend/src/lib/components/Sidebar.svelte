<script lang="ts">
  import { onMount } from 'svelte'
  import * as chatApi from '$lib/api/chat'
  import type { ChatMetadata } from '$lib/api/chat'
  import { activeChatId } from '$lib/stores/chatStore'
  import { log, logError } from '$lib/logger'

  // 使用 Svelte 5 的 runes API
  let chats = $state<ChatMetadata[]>([])
  let loading = $state(false)
  let error = $state<string | null>(null)
  
  // 批量选择相关状态
  let isEditMode = $state(false)
  let selectedChatIds = $state<Set<string>>(new Set())
  
  // 侧边栏宽度调整
  let sidebarWidth = $state(260)
  let isResizing = $state(false)
  const MIN_WIDTH = 200
  const MAX_WIDTH = 500

  // 加载对话列表
  async function loadChats() {
    log('对话列表加载', {})
    loading = true
    error = null
    try {
      chats = await chatApi.getAllChats()
      chats.sort((a, b) =>
        new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime()
      )
      log('对话列表加载成功', { count: chats.length })
    } catch (err) {
      error = err instanceof Error ? err.message : '加载失败'
      logError('对话列表加载失败', err)
    } finally {
      loading = false
    }
  }

  // 创建新对话
  async function createNewChat() {
    const chatId = `chat-${Date.now()}`
    log('创建新对话', { chatId })
    try {
      const newChat = await chatApi.createChat(chatId, '新对话')
      chats = [newChat, ...chats]
      activeChatId.set(chatId)
      log('创建新对话成功', { chatId, title: newChat.title })
    } catch (err) {
      logError('创建对话失败', err)
      alert('创建对话失败，请重试')
    }
  }

  // 选择对话
  function selectChat(id: string) {
    log('选择对话', { chatId: id })
    activeChatId.set(id)
  }

  // 删除对话
  async function deleteChat(id: string, event: Event) {
    event.stopPropagation()

    log('删除对话', { chatId: id })
    try {
      await chatApi.deleteChat(id)
      chats = chats.filter(chat => chat.id !== id)
      if ($activeChatId === id) {
        activeChatId.set(chats.length > 0 ? chats[0].id : null)
      }
      log('删除对话成功', { chatId: id })
    } catch (err) {
      logError('删除对话失败', err)
      alert('删除失败，请重试')
    }
  }

  // 格式化时间
  function formatDate(dateStr: string): string {
    const date = new Date(dateStr)
    const now = new Date()
    const diff = now.getTime() - date.getTime()
    const days = Math.floor(diff / (1000 * 60 * 60 * 24))
    
    if (days === 0) return '今天'
    if (days === 1) return '昨天'
    if (days < 7) return `${days} 天前`
    return date.toLocaleDateString('zh-CN')
  }

  // 切换编辑模式
  function toggleEditMode() {
    isEditMode = !isEditMode
    if (!isEditMode) selectedChatIds = new Set()
    log('切换编辑模式', { isEditMode })
  }

  // 切换选中状态
  function toggleChatSelection(chatId: string) {
    const newSet = new Set(selectedChatIds)
    if (newSet.has(chatId)) {
      newSet.delete(chatId)
    } else {
      newSet.add(chatId)
    }
    selectedChatIds = newSet
  }

  // 全选/取消全选
  function toggleSelectAll() {
    const willSelectAll = selectedChatIds.size !== chats.length
    if (willSelectAll) {
      selectedChatIds = new Set(chats.map(chat => chat.id))
    } else {
      selectedChatIds = new Set()
    }
    log(willSelectAll ? '全选对话' : '取消全选', { count: selectedChatIds.size })
  }

  // 批量删除
  async function batchDeleteChats() {
    if (selectedChatIds.size === 0) {
      alert('请先选择要删除的对话')
      return
    }

    const ids = Array.from(selectedChatIds)
    log('批量删除对话', { count: ids.length, chatIds: ids })
    try {
      await Promise.all(ids.map(id => chatApi.deleteChat(id)))
      chats = chats.filter(chat => !selectedChatIds.has(chat.id))
      if ($activeChatId && selectedChatIds.has($activeChatId)) {
        activeChatId.set(chats.length > 0 ? chats[0].id : null)
      }
      selectedChatIds = new Set()
      isEditMode = false
      log('批量删除成功', { deleted: ids.length })
    } catch (err) {
      logError('批量删除失败', err)
      alert('批量删除失败，请重试')
    }
  }

  // 开始调整宽度
  function startResize(e: MouseEvent) {
    isResizing = true
    document.body.classList.add('resizing')
    e.preventDefault()
  }

  // 调整宽度
  function resize(e: MouseEvent) {
    if (!isResizing) return
    
    const newWidth = e.clientX
    if (newWidth >= MIN_WIDTH && newWidth <= MAX_WIDTH) {
      sidebarWidth = newWidth
    }
  }

  // 停止调整
  function stopResize() {
    if (isResizing) {
      isResizing = false
      document.body.classList.remove('resizing')
    }
  }

  // 组件挂载时加载数据
  onMount(() => {
    loadChats()
    
    // 添加全局事件监听
    window.addEventListener('mousemove', resize)
    window.addEventListener('mouseup', stopResize)
    
    // 清理函数
    return () => {
      window.removeEventListener('mousemove', resize)
      window.removeEventListener('mouseup', stopResize)
    }
  })
</script>

<aside class="sidebar" style="width: {sidebarWidth}px">
  <div class="sidebar-header">
    <h2>Smlrag</h2>
    
    {#if !isEditMode}
      <div class="header-actions">
        <button class="new-chat-btn" onclick={createNewChat}>
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M12 5v14M5 12h14"/>
          </svg>
          新对话
        </button>
        <button class="edit-btn" onclick={toggleEditMode} title="批量管理">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M11 4H4a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2v-7"/>
            <path d="M18.5 2.5a2.121 2.121 0 013 3L12 15l-4 1 1-4 9.5-9.5z"/>
          </svg>
        </button>
      </div>
    {:else}
      <div class="edit-mode-actions">
        <button class="select-all-btn" onclick={toggleSelectAll}>
          {selectedChatIds.size === chats.length ? '取消全选' : '全选'}
        </button>
        <button class="delete-selected-btn" onclick={batchDeleteChats} disabled={selectedChatIds.size === 0}>
          删除 ({selectedChatIds.size})
        </button>
        <button class="cancel-btn" onclick={toggleEditMode}>
          取消
        </button>
      </div>
    {/if}
  </div>

  <div class="chat-list">
    {#if loading}
      <div class="loading">加载中...</div>
    {:else if error}
      <div class="error">
        <p>{error}</p>
        <button onclick={loadChats}>重试</button>
      </div>
    {:else if chats.length === 0}
      <div class="empty">
        <p>还没有对话</p>
        <p class="hint">点击上方"新对话"开始</p>
      </div>
    {:else}
      {#each chats as chat (chat.id)}
        <div 
          class="chat-item"
          class:active={chat.id === $activeChatId && !isEditMode}
          class:edit-mode={isEditMode}
          role="button"
          tabindex="0"
          onclick={() => isEditMode ? toggleChatSelection(chat.id) : selectChat(chat.id)}
          onkeydown={(e) => e.key === 'Enter' && (isEditMode ? toggleChatSelection(chat.id) : selectChat(chat.id))}
        >
          {#if isEditMode}
            <input 
              type="checkbox" 
              class="chat-checkbox"
              checked={selectedChatIds.has(chat.id)}
              onchange={() => toggleChatSelection(chat.id)}
              onclick={(e) => e.stopPropagation()}
            />
          {/if}
          
          <div class="chat-info">
            <h3 class="chat-title">{chat.title}</h3>
            <span class="chat-date">{formatDate(chat.updated_at)}</span>
          </div>
          
          {#if !isEditMode}
            <button 
              class="delete-btn"
              onclick={(e) => deleteChat(chat.id, e)}
              title="删除对话"
            >
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M3 6h18M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6m3 0V4a2 2 0 012-2h4a2 2 0 012 2v2"/>
              </svg>
            </button>
          {/if}
        </div>
      {/each}
    {/if}
  </div>

  <div class="sidebar-footer">
    <div class="user-info">
      <div class="avatar">U</div>
      <span class="username">用户</span>
    </div>
  </div>
  
  <!-- svelte-ignore a11y_no_noninteractive_element_interactions -->
  <!-- svelte-ignore a11y_no_noninteractive_tabindex -->
  <div 
    class="resize-handle" 
    class:resizing={isResizing}
    onmousedown={startResize}
    role="separator"
    tabindex="0"
    aria-label="调整侧边栏宽度"
    aria-orientation="vertical"
  ></div>
</aside>

<style>
  .sidebar {
    height: 100%;
    background: var(--bg-base);
    border-right: 1px solid var(--border-subtle);
    display: flex;
    flex-direction: column;
    overflow: hidden;
    position: relative;
    flex-shrink: 0;
  }

  .sidebar-header {
    padding: 1.25rem 1rem;
    border-bottom: 1px solid var(--border-subtle);
  }

  .sidebar-header h2 {
    margin: 0 0 1rem 0;
    font-size: 1.25rem;
    font-weight: 600;
    text-align: center;
    color: var(--color-brand);
  }

  .header-actions {
    display: flex;
    gap: 0.5rem;
  }

  .new-chat-btn {
    flex: 1;
    padding: 0.65rem 1rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
    justify-content: center;
    background: var(--color-primary-muted);
    border: 1px solid var(--color-primary);
    border-radius: var(--radius-md);
    color: var(--color-primary);
    font-size: 0.9rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s;
  }

  .new-chat-btn:hover {
    background: rgba(249, 115, 22, 0.25);
    border-color: var(--color-primary);
    box-shadow: 0 2px 8px rgba(249, 115, 22, 0.2);
  }

  .new-chat-btn svg {
    flex-shrink: 0;
  }

  .edit-btn {
    padding: 0.65rem;
    background: var(--bg-elevated);
    border: 1px solid var(--border-default);
    border-radius: var(--radius-md);
    color: var(--text-secondary);
    cursor: pointer;
    transition: all 0.2s;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .edit-btn:hover {
    background: var(--color-primary-muted);
    color: var(--color-primary);
    border-color: var(--color-primary);
  }

  .edit-mode-actions {
    display: flex;
    gap: 0.5rem;
    flex-wrap: wrap;
  }

  .select-all-btn,
  .delete-selected-btn,
  .cancel-btn {
    padding: 0.6rem 1rem;
    border-radius: 6px;
    font-size: 0.9rem;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s;
    border: 1px solid;
  }

  .select-all-btn {
    flex: 1;
    background: var(--color-primary-muted);
    border-color: var(--border-default);
    color: var(--text-primary);
  }

  .select-all-btn:hover {
    background: var(--color-primary-muted);
  }

  .delete-selected-btn {
    background: var(--color-primary-muted);
    border-color: var(--color-primary);
    color: var(--color-primary);
  }

  .delete-selected-btn:hover:not(:disabled) {
    background: rgba(249, 115, 22, 0.25);
    border-color: var(--color-primary);
  }

  .delete-selected-btn:disabled {
    opacity: 0.4;
    cursor: not-allowed;
  }

  .cancel-btn {
    background: var(--color-primary-muted);
    border-color: var(--border-default);
    color: var(--text-secondary);
  }

  .cancel-btn:hover {
    background: var(--color-primary-muted);
  }

  .chat-list {
    flex: 1;
    overflow-y: auto;
    padding: 0.5rem;
  }

  .chat-list::-webkit-scrollbar {
    width: 6px;
  }

  .chat-list::-webkit-scrollbar-track {
    background: transparent;
  }

  .chat-list::-webkit-scrollbar-thumb {
    background: var(--color-primary-muted);
    border-radius: 3px;
  }

  .chat-list::-webkit-scrollbar-thumb:hover {
    background: var(--color-primary-muted);
  }

  .chat-item {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.75rem;
    margin-bottom: 0.25rem;
    border-radius: 8px;
    cursor: pointer;
    transition: all 0.2s;
    position: relative;
    outline: none;
  }

  .chat-item:hover {
    background: var(--bg-elevated);
  }

  .chat-item.active {
    background: var(--color-primary-muted);
    border-left: 3px solid var(--color-primary);
  }

  .chat-item.edit-mode {
    padding-left: 0.5rem;
  }

  .chat-checkbox {
    width: 18px;
    height: 18px;
    cursor: pointer;
    accent-color: var(--color-primary);
    flex-shrink: 0;
  }

  .chat-info {
    flex: 1;
    min-width: 0;
  }

  .chat-title {
    margin: 0;
    font-size: 0.9rem;
    font-weight: 500;
    color: var(--text-primary);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .chat-date {
    font-size: 0.75rem;
    color: var(--text-muted);
  }

  .delete-btn {
    flex-shrink: 0;
    padding: 0.25rem;
    background: transparent;
    border: none;
    color: var(--text-muted);
    cursor: pointer;
    border-radius: 4px;
    opacity: 0;
    transition: all 0.2s;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .chat-item:hover .delete-btn {
    opacity: 1;
  }

  .delete-btn:hover {
    background: var(--color-primary-muted);
    color: var(--color-primary);
  }

  .sidebar-footer {
    padding: 1rem;
    border-top: 1px solid var(--border-subtle);
  }

  .user-info {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 0.5rem;
    border-radius: var(--radius-md);
    transition: background 0.2s;
  }

  .user-info:hover {
    background: var(--bg-elevated);
  }

  .avatar {
    width: 32px;
    height: 32px;
    border-radius: 50%;
    background: var(--gradient-primary);
    display: flex;
    align-items: center;
    justify-content: center;
    color: #fff;
    font-weight: 600;
    font-size: 0.9rem;
  }

  .username {
    font-size: 0.9rem;
    color: var(--text-primary);
  }

  .loading, .error, .empty {
    padding: 2rem 1rem;
    text-align: center;
    color: var(--text-muted);
  }

  .error p {
    color: var(--color-primary);
    margin-bottom: 1rem;
  }

  .error button {
    padding: 0.5rem 1rem;
    background: var(--color-primary-muted);
    border: 1px solid var(--color-primary);
    border-radius: var(--radius-sm);
    color: var(--color-primary);
    cursor: pointer;
  }

  .empty .hint {
    font-size: 0.85rem;
    margin-top: 0.5rem;
    opacity: 0.7;
  }

  .resize-handle {
    position: absolute;
    right: 0;
    top: 0;
    bottom: 0;
    width: 4px;
    cursor: col-resize;
    background: transparent;
    transition: background 0.2s;
    z-index: 10;
  }

  .resize-handle:hover,
  .resize-handle.resizing {
    background: var(--color-primary);
    opacity: 0.6;
  }

  .resize-handle::before {
    content: '';
    position: absolute;
    left: -2px;
    right: -2px;
    top: 0;
    bottom: 0;
  }

  :global(body.resizing) {
    cursor: col-resize;
    user-select: none;
  }
</style>

