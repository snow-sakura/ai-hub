import MarkdownIt from 'markdown-it'
import hljs from 'highlight.js'
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
  const titleAttr = title ? ` title="${title}"` : ''
  const placeholder = 'data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7'
  return `<img data-src="${src}" src="${placeholder}" alt="${alt}"${titleAttr} loading="lazy" />`
}

/** Markdown 渲染 Hook */
export function useMarkdownRenderer() {
  /** 渲染 Markdown 为安全 HTML */
  function render(content: string): string {
    const rawHtml = md.render(content)
    return DOMPurify.sanitize(rawHtml, {
      ADD_TAGS: ['pre', 'code'],
      ADD_ATTR: ['class'],
    })
  }

  return { render }
}
