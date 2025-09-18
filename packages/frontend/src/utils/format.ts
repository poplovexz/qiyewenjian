/**
 * 格式化工具函数
 */

/**
 * 格式化日期时间
 * @param date 日期字符串或Date对象
 * @param format 格式化模式，默认为 'YYYY-MM-DD HH:mm:ss'
 * @returns 格式化后的日期字符串
 */
export function formatDateTime(date: string | Date | null | undefined, format: string = 'YYYY-MM-DD HH:mm:ss'): string {
  if (!date) return '-'
  
  const d = typeof date === 'string' ? new Date(date) : date
  
  if (isNaN(d.getTime())) return '-'
  
  const year = d.getFullYear()
  const month = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  const hours = String(d.getHours()).padStart(2, '0')
  const minutes = String(d.getMinutes()).padStart(2, '0')
  const seconds = String(d.getSeconds()).padStart(2, '0')
  
  return format
    .replace('YYYY', String(year))
    .replace('MM', month)
    .replace('DD', day)
    .replace('HH', hours)
    .replace('mm', minutes)
    .replace('ss', seconds)
}

/**
 * 格式化日期
 * @param date 日期字符串或Date对象
 * @returns 格式化后的日期字符串 (YYYY-MM-DD)
 */
export function formatDate(date: string | Date | null | undefined): string {
  return formatDateTime(date, 'YYYY-MM-DD')
}

/**
 * 格式化时间
 * @param date 日期字符串或Date对象
 * @returns 格式化后的时间字符串 (HH:mm:ss)
 */
export function formatTime(date: string | Date | null | undefined): string {
  return formatDateTime(date, 'HH:mm:ss')
}

/**
 * 格式化金额
 * @param amount 金额数字
 * @param currency 货币符号，默认为 '¥'
 * @param decimals 小数位数，默认为 2
 * @returns 格式化后的金额字符串
 */
export function formatCurrency(amount: number | string | null | undefined, currency: string = '¥', decimals: number = 2): string {
  if (amount === null || amount === undefined || amount === '') return '-'
  
  const num = typeof amount === 'string' ? parseFloat(amount) : amount
  
  if (isNaN(num)) return '-'
  
  return `${currency}${num.toLocaleString('zh-CN', {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals
  })}`
}

/**
 * 格式化文件大小
 * @param bytes 字节数
 * @returns 格式化后的文件大小字符串
 */
export function formatFileSize(bytes: number | null | undefined): string {
  if (!bytes || bytes === 0) return '0 B'
  
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  
  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(2))} ${sizes[i]}`
}

/**
 * 格式化手机号
 * @param phone 手机号
 * @returns 格式化后的手机号 (138****8888)
 */
export function formatPhone(phone: string | null | undefined): string {
  if (!phone) return '-'
  
  if (phone.length === 11) {
    return `${phone.slice(0, 3)}****${phone.slice(7)}`
  }
  
  return phone
}

/**
 * 格式化身份证号
 * @param idCard 身份证号
 * @returns 格式化后的身份证号 (前6位****后4位)
 */
export function formatIdCard(idCard: string | null | undefined): string {
  if (!idCard) return '-'
  
  if (idCard.length === 18) {
    return `${idCard.slice(0, 6)}********${idCard.slice(14)}`
  }
  
  return idCard
}

/**
 * 格式化银行卡号
 * @param cardNumber 银行卡号
 * @returns 格式化后的银行卡号 (前4位****后4位)
 */
export function formatBankCard(cardNumber: string | null | undefined): string {
  if (!cardNumber) return '-'
  
  if (cardNumber.length >= 8) {
    const start = cardNumber.slice(0, 4)
    const end = cardNumber.slice(-4)
    const middle = '*'.repeat(Math.max(4, cardNumber.length - 8))
    return `${start}${middle}${end}`
  }
  
  return cardNumber
}

/**
 * 格式化百分比
 * @param value 数值 (0-1 或 0-100)
 * @param isDecimal 是否为小数形式 (0-1)，默认为 true
 * @param decimals 小数位数，默认为 2
 * @returns 格式化后的百分比字符串
 */
export function formatPercentage(value: number | null | undefined, isDecimal: boolean = true, decimals: number = 2): string {
  if (value === null || value === undefined) return '-'
  
  const percentage = isDecimal ? value * 100 : value
  
  return `${percentage.toFixed(decimals)}%`
}

/**
 * 格式化相对时间
 * @param date 日期字符串或Date对象
 * @returns 相对时间字符串 (如：刚刚、5分钟前、1小时前等)
 */
export function formatRelativeTime(date: string | Date | null | undefined): string {
  if (!date) return '-'
  
  const d = typeof date === 'string' ? new Date(date) : date
  const now = new Date()
  const diff = now.getTime() - d.getTime()
  
  if (diff < 0) return '未来时间'
  
  const seconds = Math.floor(diff / 1000)
  const minutes = Math.floor(seconds / 60)
  const hours = Math.floor(minutes / 60)
  const days = Math.floor(hours / 24)
  const months = Math.floor(days / 30)
  const years = Math.floor(days / 365)
  
  if (seconds < 60) return '刚刚'
  if (minutes < 60) return `${minutes}分钟前`
  if (hours < 24) return `${hours}小时前`
  if (days < 30) return `${days}天前`
  if (months < 12) return `${months}个月前`
  return `${years}年前`
}
