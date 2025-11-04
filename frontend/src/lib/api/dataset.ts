/**
 * 文件扫描 API 客户端
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api'

// ========== 类型定义 ==========

export interface FileInfo {
  name: string
  size: number
}

export interface ScanResult {
  status: string
  message: string
  total_files: number
  total_size: number
  files: FileInfo[]
  scan_path: string
}

// ========== API 函数 ==========

/**
 * 扫描 data 目录中的文件
 */
export async function scanFiles(): Promise<ScanResult> {
  const response = await fetch(`${API_BASE_URL}/scan`, {
    method: 'POST'
  })
  if (!response.ok) throw new Error('扫描文件失败')
  return response.json()
}
