/**
 * 格式化日期
 * @param date 日期字符串或Date对象
 * @returns 格式化后的日期字符串 YYYY-MM-DD
 */
export function formatDate(date: string | Date | undefined): string {
  if (!date) return "-";

  const d = typeof date === "string" ? new Date(date) : date;

  if (isNaN(d.getTime())) return "-";

  const year = d.getFullYear();
  const month = String(d.getMonth() + 1).padStart(2, "0");
  const day = String(d.getDate()).padStart(2, "0");

  return `${year}-${month}-${day}`;
}

/**
 * 格式化日期时间
 * @param date 日期字符串或Date对象
 * @returns 格式化后的日期时间字符串 YYYY-MM-DD HH:mm:ss
 */
export function formatDateTime(date: string | Date | undefined): string {
  if (!date) return "-";

  const d = typeof date === "string" ? new Date(date) : date;

  if (isNaN(d.getTime())) return "-";

  const year = d.getFullYear();
  const month = String(d.getMonth() + 1).padStart(2, "0");
  const day = String(d.getDate()).padStart(2, "0");
  const hours = String(d.getHours()).padStart(2, "0");
  const minutes = String(d.getMinutes()).padStart(2, "0");
  const seconds = String(d.getSeconds()).padStart(2, "0");

  return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`;
}

/**
 * 格式化时间
 * @param date 日期字符串或Date对象
 * @returns 格式化后的时间字符串 HH:mm:ss
 */
export function formatTime(date: string | Date | undefined): string {
  if (!date) return "-";

  const d = typeof date === "string" ? new Date(date) : date;

  if (isNaN(d.getTime())) return "-";

  const hours = String(d.getHours()).padStart(2, "0");
  const minutes = String(d.getMinutes()).padStart(2, "0");
  const seconds = String(d.getSeconds()).padStart(2, "0");

  return `${hours}:${minutes}:${seconds}`;
}

/**
 * 格式化金额
 * @param amount 金额
 * @param decimals 小数位数，默认2位
 * @returns 格式化后的金额字符串
 */
export function formatMoney(
  amount: number | string | undefined,
  decimals = 2,
): string {
  if (amount === undefined || amount === null || amount === "") return "0.00";

  const num = typeof amount === "string" ? parseFloat(amount) : amount;

  if (isNaN(num)) return "0.00";

  return num.toFixed(decimals).replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

/**
 * 格式化相对时间
 * @param date 日期字符串或Date对象
 * @returns 相对时间字符串，如"刚刚"、"5分钟前"、"2小时前"等
 */
export function formatRelativeTime(date: string | Date | undefined): string {
  if (!date) return "-";

  const d = typeof date === "string" ? new Date(date) : date;

  if (isNaN(d.getTime())) return "-";

  const now = new Date();
  const diff = now.getTime() - d.getTime();

  const seconds = Math.floor(diff / 1000);
  const minutes = Math.floor(seconds / 60);
  const hours = Math.floor(minutes / 60);
  const days = Math.floor(hours / 24);

  if (seconds < 60) {
    return "刚刚";
  } else if (minutes < 60) {
    return `${minutes}分钟前`;
  } else if (hours < 24) {
    return `${hours}小时前`;
  } else if (days < 7) {
    return `${days}天前`;
  } else {
    return formatDate(d);
  }
}
