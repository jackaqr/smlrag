/**
 * 聊天状态管理 - 使用传统 Svelte store
 */
import { writable } from 'svelte/store'

export const activeChatId = writable<string | null>(null)

