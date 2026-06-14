import MarkdownIt from 'markdown-it'

// ── Tree-shakable highlight.js（仅注册实际使用的语言） ────────
import hljs from 'highlight.js/lib/core'
import json from 'highlight.js/lib/languages/json'
import python from 'highlight.js/lib/languages/python'
import javascript from 'highlight.js/lib/languages/javascript'
import bash from 'highlight.js/lib/languages/bash'
import typescript from 'highlight.js/lib/languages/typescript'
import sql from 'highlight.js/lib/languages/sql'
import xml from 'highlight.js/lib/languages/xml'
import yaml from 'highlight.js/lib/languages/yaml'
import markdown from 'highlight.js/lib/languages/markdown'
import plaintext from 'highlight.js/lib/languages/plaintext'

hljs.registerLanguage('json', json)
hljs.registerLanguage('python', python)
hljs.registerLanguage('javascript', javascript)
hljs.registerLanguage('js', javascript)
hljs.registerLanguage('bash', bash)
hljs.registerLanguage('sh', bash)
hljs.registerLanguage('typescript', typescript)
hljs.registerLanguage('ts', typescript)
hljs.registerLanguage('sql', sql)
hljs.registerLanguage('xml', xml)
hljs.registerLanguage('yaml', yaml)
hljs.registerLanguage('yml', yaml)
hljs.registerLanguage('markdown', markdown)
hljs.registerLanguage('md', markdown)
hljs.registerLanguage('plaintext', plaintext)
hljs.registerLanguage('text', plaintext)

import DOMPurify from 'dompurify'
import 'highlight.js/styles/github-dark.min.css'

const md: MarkdownIt = new MarkdownIt({
  html: false,
  linkify: true,
  typographer: true,
  highlight(str: string, lang: string): string {
    if (lang && hljs.getLanguage(lang)) {
      try {
        return `<pre class="code-block"><code class="hljs language-${lang}">${
          hljs.highlight(str, { language: lang }).value
        }</code></pre>`
      } catch {
        // fall through
      }
    }
    return `<pre class="code-block"><code class="hljs">${md.utils.escapeHtml(str)}</code></pre>`
  },
})

/** HTML 属性值转义（防止 XSS） */
function escapeAttr(s: string): string {
  return s
    .replace(/&/g, '&amp;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
}

// 自定义链接渲染：添加 target="_blank" + rel="noopener noreferrer"
const defaultLinkRender = md.renderer.rules.link_open ||
  function (tokens: any, idx: any, options: any, _env: any, self: any) { return self.renderToken(tokens, idx, options) }

md.renderer.rules.link_open = function (tokens, idx, options, env, self) {
  tokens[idx].attrPush(['target', '_blank'])
  tokens[idx].attrPush(['rel', 'noopener noreferrer'])
  return defaultLinkRender(tokens, idx, options, env, self)
}

// 自定义图片渲染规则：添加 data-src 用于懒加载
md.renderer.rules.image = function (tokens, idx) {
  const token = tokens[idx]
  const srcIndex = token.attrIndex('src')
  const alt = token.content || ''
  const titleIndex = token.attrIndex('title')

  let src = ''
  let title = ''

  if (srcIndex >= 0) {
    src = token.attrs![srcIndex][1]
  }
  if (titleIndex >= 0) {
    title = token.attrs![titleIndex][1]
  }

  // 使用 data-src 而非 src，实现懒加载；src 使用透明占位图避免空 src 触发请求
  const titleAttr = title ? ` title="${escapeAttr(title)}"` : ''
  const placeholder = 'data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7'
  return `<img data-src="${escapeAttr(src)}" src="${placeholder}" alt="${escapeAttr(alt)}"${titleAttr} loading="lazy" />`
}

/** Markdown 渲染 Hook */
export function useMarkdownRenderer() {
  /** 渲染 Markdown 为安全 HTML */
  function render(content: string): string {
    const rawHtml = md.render(content)
    return DOMPurify.sanitize(rawHtml, {
      ADD_TAGS: ['pre', 'code'],
      ADD_ATTR: ['class', 'data-src', 'loading', 'target', 'rel'],
    })
  }

  return { render }
}
