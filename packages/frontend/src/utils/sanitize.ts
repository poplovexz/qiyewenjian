/**
 * HTML 清理工具
 * 使用 DOMPurify 防止 XSS 攻击
 */
import DOMPurify from 'dompurify'

/**
 * 合同内容安全的 HTML 标签和属性配置
 * 允许常见的格式化标签，禁止脚本和事件处理器
 */
const CONTRACT_CONFIG: DOMPurify.Config = {
  // 允许的 HTML 标签
  ALLOWED_TAGS: [
    // 结构标签
    'div', 'span', 'p', 'br', 'hr',
    // 标题
    'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
    // 文本格式
    'b', 'strong', 'i', 'em', 'u', 'strike', 's', 'del', 'ins', 'sub', 'sup',
    // 列表
    'ul', 'ol', 'li',
    // 表格
    'table', 'thead', 'tbody', 'tfoot', 'tr', 'th', 'td', 'caption', 'colgroup', 'col',
    // 其他
    'a', 'img', 'blockquote', 'pre', 'code', 'address',
  ],
  // 允许的属性
  ALLOWED_ATTR: [
    'class', 'id', 'style',
    'href', 'target', 'rel',
    'src', 'alt', 'width', 'height',
    'colspan', 'rowspan', 'align', 'valign',
    'border', 'cellpadding', 'cellspacing',
  ],
  // 允许的 URL 协议
  ALLOWED_URI_REGEXP: /^(?:(?:https?|mailto|tel):|[^a-z]|[a-z+.-]+(?:[^a-z+.\-:]|$))/i,
  // 移除所有脚本
  FORBID_TAGS: ['script', 'style', 'iframe', 'object', 'embed', 'form', 'input', 'button'],
  // 禁止事件处理器
  FORBID_ATTR: ['onerror', 'onload', 'onclick', 'onmouseover', 'onfocus', 'onblur'],
}

/**
 * 清理合同 HTML 内容，防止 XSS 攻击
 * @param html - 需要清理的 HTML 字符串
 * @returns 清理后的安全 HTML 字符串
 */
export function sanitizeContractHtml(html: string | null | undefined): string {
  if (!html) return ''
  return DOMPurify.sanitize(html, CONTRACT_CONFIG)
}

/**
 * 通用 HTML 清理（更严格）
 * @param html - 需要清理的 HTML 字符串
 * @returns 清理后的安全 HTML 字符串
 */
export function sanitizeHtml(html: string | null | undefined): string {
  if (!html) return ''
  return DOMPurify.sanitize(html)
}

/**
 * 清理并只保留纯文本
 * @param html - 需要清理的 HTML 字符串
 * @returns 纯文本字符串
 */
export function stripHtml(html: string | null | undefined): string {
  if (!html) return ''
  return DOMPurify.sanitize(html, { ALLOWED_TAGS: [] })
}

export default {
  sanitizeContractHtml,
  sanitizeHtml,
  stripHtml,
}

