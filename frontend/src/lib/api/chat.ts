/**
 * 聊天 API 客户端
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api'

// ========== 类型定义 ==========

export interface Message {
  role: 'user' | 'assistant'
  content: string
  timestamp: string
}

export interface ChatMetadata {
  id: string
  title: string
  created_at: string
  updated_at: string
  message_count: number
}

// ========== API 函数 ==========

/**
 * 获取所有对话列表
 */
export async function getAllChats(): Promise<ChatMetadata[]> {
  const response = await fetch(`${API_BASE_URL}/chats`)
  if (!response.ok) throw new Error('获取对话列表失败')
  return response.json()
}

/**
 * 创建新对话
 */
export async function createChat(chatId: string, title: string = '新对话'): Promise<ChatMetadata> {
  const response = await fetch(`${API_BASE_URL}/chats?chat_id=${chatId}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ title })
  })
  if (!response.ok) throw new Error('创建对话失败')
  return response.json()
}

/**
 * 获取对话元数据
 */
export async function getChatMetadata(chatId: string): Promise<ChatMetadata> {
  const response = await fetch(`${API_BASE_URL}/chats/${chatId}`)
  if (!response.ok) throw new Error('获取对话信息失败')
  return response.json()
}

/**
 * 获取对话消息列表
 */
export async function getMessages(chatId: string, limit?: number): Promise<Message[]> {
  const url = limit 
    ? `${API_BASE_URL}/chats/${chatId}/messages?limit=${limit}`
    : `${API_BASE_URL}/chats/${chatId}/messages`
  
  const response = await fetch(url)
  if (!response.ok) throw new Error('获取消息失败')
  return response.json()
}

/**
 * 发送消息
 */
export async function sendMessage(chatId: string, content: string): Promise<Message> {
  const response = await fetch(`${API_BASE_URL}/chats/${chatId}/messages`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ content })
  })
  if (!response.ok) throw new Error('发送消息失败')
  return response.json()
}

/**
 * 更新对话标题
 */
export async function updateChatTitle(chatId: string, title: string): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/chats/${chatId}/title`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ title })
  })
  if (!response.ok) throw new Error('更新标题失败')
}

/**
 * 删除对话
 */
export async function deleteChat(chatId: string): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/chats/${chatId}`, {
    method: 'DELETE'
  })
  if (!response.ok) throw new Error('删除对话失败')
}

/**
 * 获取统计信息
 */
export async function getStats(): Promise<{ total_chats: number; total_messages: number }> {
  const response = await fetch(`${API_BASE_URL}/stats`)
  if (!response.ok) throw new Error('获取统计信息失败')
  return response.json()
}

