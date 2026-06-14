/**
 * 配置工具函数
 */
import type { ConfigItem } from '@/modules/ai_testing/types/generation'

/** 从配置项数组中查找并解析值 */
export function findConfigValue(items: ConfigItem[], key: string, fallback: string): string {
  return items.find(i => i.key === key)?.value ?? fallback
}
