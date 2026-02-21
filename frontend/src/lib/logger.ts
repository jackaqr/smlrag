/**
 * 前端操作日志：统一前缀与格式，便于在浏览器控制台筛选 [SMLRAG]
 */

const PREFIX = '[SMLRAG]'

function timestamp(): string {
  return new Date().toLocaleTimeString('zh-CN', {
    hour12: false,
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    fractionalSecondDigits: 3
  })
}

/** 记录一次用户操作或状态变化 */
export function log(action: string, detail?: Record<string, unknown>): void {
  const msg = `${PREFIX} [${timestamp()}] ${action}`
  if (detail != null && Object.keys(detail).length > 0) {
    console.log(msg, detail)
  } else {
    console.log(msg)
  }
}

/** 记录错误（保留原始 console.error 堆栈） */
export function logError(action: string, err: unknown): void {
  console.error(`${PREFIX} [${timestamp()}] ${action}`, err)
}
