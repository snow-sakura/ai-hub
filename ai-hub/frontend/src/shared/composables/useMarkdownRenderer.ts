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
