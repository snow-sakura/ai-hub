import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import AutoImport from 'unplugin-auto-import/vite'
import Components from 'unplugin-vue-components/vite'
import { NaiveUiResolver } from 'unplugin-vue-components/resolvers'
import { fileURLToPath, URL } from 'node:url'
import viteCompression from 'vite-plugin-compression'

export default defineConfig({
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
  plugins: [
    vue(),
    AutoImport({
      imports: [
        'vue',
        'vue-router',
        'pinia',
        { '@vueuse/core': ['useDebounceFn'] },
      ],
      dts: 'src/auto-imports.d.ts',
    }),
    Components({
      resolvers: [NaiveUiResolver()],
      dts: 'src/components.d.ts',
    }),
    // 生产环境启用 brotli 预压缩（现代浏览器均支持，比率优于 gzip）
    viteCompression({
      algorithm: 'brotliCompress',
      ext: '.br',
      threshold: 10240,
      deleteOriginFile: false,
    }),
  ],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
  build: {
    // Naive UI 体积较大，提高阈值避免误报
    chunkSizeWarningLimit: 900,
    rollupOptions: {
      output: {
        // 手动配置代码分割策略（仅针对 node_modules）
        manualChunks(id) {
          if (id.includes('node_modules')) {
            // Naive UI 单独分包（最大依赖）
            if (id.includes('naive-ui')) {
              return 'vendor-ui'
            }

            // Markdown 编辑器（最大，独立分包）
            if (id.includes('md-editor-v3')) {
              return 'vendor-md-editor'
            }

            // 代码高亮（体积大，独立分包）
            if (id.includes('highlight.js')) {
              return 'vendor-highlight'
            }

            // Markdown 渲染 + 净化
            if (id.includes('markdown-it') || id.includes('dompurify')) {
              return 'vendor-md-render'
            }

            // Vue 生态（核心框架）
            if (id.includes('vue') || id.includes('pinia') || id.includes('vue-router')) {
              return 'vendor-vue'
            }

            // Axios 和网络请求
            if (id.includes('axios')) {
              return 'vendor-http'
            }

            // VueUse 工具库
            if (id.includes('@vueuse')) {
              return 'vendor-utils'
            }

            // TanStack Virtual（虚拟滚动）
            if (id.includes('@tanstack')) {
              return 'vendor-virtual'
            }
          }
          // 业务代码使用默认分包策略
        },
        // 优化 chunk 文件名
        chunkFileNames: 'assets/[name]-[hash].js',
        entryFileNames: 'assets/[name]-[hash].js',
        assetFileNames: 'assets/[name]-[hash].[ext]',
      },
    },
  },
})
