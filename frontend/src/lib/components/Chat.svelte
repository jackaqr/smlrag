<script lang="ts">
  import { onMount } from 'svelte'
  import * as chatApi from '$lib/api/chat'
  import type { Message } from '$lib/api/chat'
  import { activeChatId } from '$lib/stores/chatStore'

  // 使用 Svelte 5 的 runes API
  let inputText = $state('')
  let messages = $state<Message[]>([])
  let loading = $state(false)
  let sending = $state(false)

  // 监听激活的对话ID变化
  $effect(() => {
    if ($activeChatId) {
      loadMessages($activeChatId)
    } else {
      messages = []
    }
  })
  
  // 加载消息历史
  async function loadMessages(chatId: string) {
    loading = true
    try {
      messages = await chatApi.getMessages(chatId)
    } catch (err) {
      console.error('加载消息失败:', err)
      messages = []
    } finally {
      loading = false
    }
  }

  // 发送消息
  async function handleSend() {
    if (!inputText.trim() || !$activeChatId || sending) return
    
    const content = inputText.trim()
    inputText = ''
    sending = true
    
    try {
      // 添加用户消息到界面
      messages = [...messages, {
        role: 'user',
        content,
        timestamp: new Date().toISOString()
      }]
      
      // 发送到后端并获取AI回复
      const response = await chatApi.sendMessage($activeChatId, content)
      
      // 添加AI回复
      messages = [...messages, response]
      
      // 滚动到底部
      scrollToBottom()
    } catch (err) {
      console.error('发送消息失败:', err)
      alert('发送失败，请重试')
      // 移除失败的用户消息
      messages = messages.slice(0, -1)
      inputText = content // 恢复输入
    } finally {
      sending = false
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
      if (container) {
        container.scrollTop = container.scrollHeight
      }
    }, 100)
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
              <p>{message.content}</p>
            </div>
            <span class="message-time">{new Date(message.timestamp).toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })}</span>
          </div>
        {/each}
      {/if}
    </div>

    <div class="input-container">
      <div class="input-wrapper">
        <div class="input-row">
          <input 
            type="text" 
            bind:value={inputText}
            placeholder="输入消息..."
            onkeypress={handleKeypress}
            disabled={sending}
          />
          {#if inputText}
            <button class="send-btn" onclick={handleSend} disabled={sending}>
              {sending ? '发送中...' : '发送'}
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
    background: rgba(255, 255, 255, 0.05);
    border-radius: 12px;
    border: 1px solid rgba(255, 255, 255, 0.1);
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
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

