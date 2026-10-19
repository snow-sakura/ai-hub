#!/usr/bin/env node
/**
 * Demo 一键构建脚本（零依赖，Node 18+）
 * 把仓库内的验证截图与运行数据快照复制进 demo/ 站点目录，
 * 保证 GitHub Pages 部署后所有资源同源（assets/、data/），
 * 避免依赖 raw.githubusercontent.com（部分网络不可达）。
 *
 * 数据来源（单一事实源，均在仓库中维护）：
 *   ai-hub/docs/screenshots/*.png  →  demo/assets/*.png
 *   ai-hub/demo/data/run.json      →  源文件本身即站点路径，无需复制
 *
 * 用法：node ai-hub/demo/build.mjs   （CI 与本地通用）
 */
import { cpSync, mkdirSync, writeFileSync, existsSync, readdirSync } from 'node:fs'
import { join, dirname } from 'node:path'
import { fileURLToPath } from 'node:url'

const here = dirname(fileURLToPath(import.meta.url)) // ai-hub/demo
const repoRoot = join(here, '..', '..')

// 1) 截图资源 → demo/assets/
const shotsSrc = join(repoRoot, 'ai-hub', 'docs', 'screenshots')
const shotsDest = join(here, 'assets')
mkdirSync(shotsDest, { recursive: true })
if (existsSync(shotsSrc)) {
  cpSync(shotsSrc, shotsDest, { recursive: true })
}
const pngs = readdirSync(shotsDest).filter(f => f.endsWith('.png'))

// 2) 数据快照占位保护（run.json 已在仓库 demo/data/ 内，缺失时生成空态避免 404）
const dataDir = join(here, 'data')
mkdirSync(dataDir, { recursive: true })
const runJson = join(dataDir, 'run.json')
if (!existsSync(runJson)) {
  writeFileSync(runJson, JSON.stringify({
    generated_at: new Date().toISOString(),
    note: '未提供数据快照源（ai-hub/demo/data/run.json），页面显示空态。',
    generate_stats: { total_tasks: 0, completed_tasks: 0, total_cases: 0 },
    sequences: [], generation_tasks: [], scheduled_runs: [],
  }))
}
console.log(`[demo-build] 截图 ${pngs.length} 张 → assets/ ；数据 data/run.json 就绪`)
