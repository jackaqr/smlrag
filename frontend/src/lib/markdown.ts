/**
 * Markdown 渲染：支持代码块语法高亮、复制按钮与 Mermaid 图表
 */
import { Marked } from 'marked'
import { markedHighlight } from 'marked-highlight'
import hljs from 'highlight.js'

function escapeHtml(text: string): string {
  const map: Record<string, string> = {
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#39;'
  }
  return text.replace(/[&<>"']/g, (ch) => map[ch] ?? ch)
}

/** 用于 HTML 属性值，避免断行和引号破坏属性 */
function escapeAttr(text: string): string {
  return escapeHtml(text).replace(/\r?\n/g, '&#10;')
}

/** 判断是否为后端/模型返回的已高亮 HTML（highlight.js 的 span） */
function isPreRenderedHljs(html: string): boolean {
  return /<span class="hljs-/.test(html)
}

/** 从已高亮的 HTML 中提取纯文本（用于复制按钮） */
function stripHljsToPlainText(html: string): string {
  const withoutTags = html.replace(/<[^>]+>/g, '')
  return withoutTags
    .replace(/&quot;/g, '"')
    .replace(/&#39;/g, "'")
    .replace(/&apos;/g, "'")
    .replace(/&lt;/g, '<')
    .replace(/&gt;/g, '>')
    .replace(/&amp;/g, '&')
    .replace(/&#(\d+);/g, (_, n) => String.fromCharCode(Number(n)))
    .replace(/&#x([0-9a-fA-F]+);/g, (_, n) => String.fromCharCode(parseInt(n, 16)))
}

const marked = new Marked(
  markedHighlight({
    langPrefix: 'hljs language-',
    highlight(code: string, lang: string) {
      if (lang === 'mermaid') return code
      const language = hljs.getLanguage(lang) ? lang : 'plaintext'
      return hljs.highlight(code, { language }).value
    }
  })
)

marked.use({
  renderer: {
    code({ text, lang }: { text: string; lang?: string }) {
      if (lang === 'mermaid') {
        return `<div class="mermaid">${escapeHtml(text.trim())}</div>`
      }
      // 后端/模型有时会返回已高亮的 HTML，直接输出为 HTML 避免被二次转义
      if (isPreRenderedHljs(text)) {
        const plainText = stripHljsToPlainText(text)
        return `<div class="code-block-wrap"><button type="button" class="code-copy-btn" data-code="${escapeAttr(plainText)}" title="复制代码">复制</button><pre><code class="hljs">${text}</code></pre></div>`
      }
      const language = hljs.getLanguage(lang ?? '') ? (lang ?? 'plaintext') : 'plaintext'
      const highlighted = hljs.highlight(text, { language }).value
      const langClass = `hljs language-${language}`
      return `<div class="code-block-wrap"><button type="button" class="code-copy-btn" data-code="${escapeAttr(text)}" title="复制代码">复制</button><pre><code class="${langClass}">${highlighted}</code></pre></div>`
    }
  }
})

/**
 * 将 Markdown 字符串转为 HTML（含代码高亮与 mermaid 占位）
 */
export function markdownToHtml(md: string): string {
  const trimmed = md?.trim() ?? ''
  if (!trimmed) return ''
  // 整条消息就是已高亮的 HTML 时，直接按代码块输出，避免被 markdown 转义
  if (isPreRenderedHljs(trimmed)) {
    const plainText = stripHljsToPlainText(trimmed)
    return `<div class="code-block-wrap"><button type="button" class="code-copy-btn" data-code="${escapeAttr(plainText)}" title="复制代码">复制</button><pre><code class="hljs">${trimmed}</code></pre></div>`
  }
  try {
    return marked.parse(trimmed) as string
  } catch {
    return escapeHtml(trimmed)
  }
}
