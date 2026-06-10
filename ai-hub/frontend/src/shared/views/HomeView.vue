<template>
  <div class="home-view">
    <div class="home-content">
      <!-- 标题区 -->
      <header class="home-header">
        <div class="logo-area">
          <div class="logo-icon">✦</div>
          <div class="logo-text-wrap">
            <h1 class="logo-text">AI-HUB工作台</h1>
            <p class="subtitle">智能对话 · 知识管理 · 创意无限</p>
          </div>
        </div>
      </header>

      <!-- 卡片网格 -->
      <div class="card-grid">
        <div
          v-for="card in cards"
          :key="card.id"
          class="app-card"
          :class="{ disabled: card.disabled }"
          @click="card.disabled ? null : router.push(card.route)"
        >
          <div class="card-inner">
            <div class="card-icon-area">
              <span class="card-icon">{{ card.icon }}</span>
              <div v-if="card.badge" class="card-badge">{{ card.badge }}</div>
            </div>
            <h3 class="card-title">{{ card.title }}</h3>
            <p class="card-desc">{{ card.description }}</p>
            <div class="card-tags">
              <span v-for="tag in card.tags" :key="tag" class="tag">{{ tag }}</span>
            </div>
            <div class="card-footer">
              <span v-if="card.disabled" class="coming-soon">即将上线</span>
              <span v-else class="enter-btn">
                打开
                <span class="arrow">→</span>
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'

const router = useRouter()

interface AppCard {
  id: string
  icon: string
  title: string
  description: string
  tags: string[]
  route: string
  badge?: string
  disabled?: boolean
}

const cards: AppCard[] = [
  {
    id: 'chat',
    icon: '⚡',
    title: 'AI 聊天室',
    description: '与超级智能体对话，支持多模型切换、RAG 知识库、7 大内置工具，自动规划复杂任务',
    tags: ['多模型', 'RAG', '工具调用'],
    route: '/chat',
    badge: 'HOT',
  },
  {
    id: 'knowledge',
    icon: '🎯',
    title: '知识库管理',
    description: '上传 PDF/Word/TXT 文档，AI 自动理解并引用，打造专属知识助手',
    tags: ['PDF', 'Word', '向量检索'],
    route: '/knowledge',
  },
  {
    id: 'comfort',
    icon: '💖',
    title: '哄哄模拟器',
    description: 'AI 模拟各种场景下的情绪反应，学习安慰话术，实时分析安慰效果',
    tags: ['角色扮演', '情绪分析', '原谅值'],
    route: '/comfort',
    badge: 'NEW',
  },
]
</script>

<style scoped>
.home-view {
  min-height: 100vh;
  background: var(--bg-primary);
  overflow-y: auto;
}

.home-content {
  max-width: 1100px;
  margin: 0 auto;
  padding: 48px 24px 80px;
}

.home-header {
  margin-bottom: 48px;
  display: flex;
  justify-content: center;
}

.logo-area {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
}

.logo-icon {
  font-size: 40px;
  width: 56px;
  height: 56px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--accent-bg);
  border-radius: 14px;
}

.logo-text {
  font-size: 28px;
  font-weight: 700;
  color: var(--text-primary);
  letter-spacing: -0.02em;
  line-height: 1.2;
}

.subtitle {
  font-size: 14px;
  color: var(--text-muted);
  margin-top: 4px;
  letter-spacing: 2px;
}

.card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 20px;
}

.app-card {
  border-radius: 14px;
  cursor: pointer;
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
  animation: cardIn 0.5s ease both;
  border: 1px solid rgba(0, 0, 0, 0.06);
}

.app-card:nth-child(1) { animation-delay: 0.05s }
.app-card:nth-child(2) { animation-delay: 0.1s }
.app-card:nth-child(3) { animation-delay: 0.15s }

@keyframes cardIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.app-card:hover {
  transform: translateY(-4px);
  border-color: rgba(99, 102, 241, 0.2);
  box-shadow: 0 8px 24px rgba(99, 102, 241, 0.08);
}

.app-card:hover .arrow {
  transform: translateX(3px);
}

.app-card:hover .card-icon {
  transform: scale(1.1);
}

.app-card.disabled {
  cursor: default;
  opacity: 0.5;
}

.app-card.disabled:hover {
  transform: none;
  border-color: rgba(0, 0, 0, 0.06);
  box-shadow: none;
}

.card-inner {
  padding: 24px;
  background: var(--bg-card);
  border-radius: 14px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.card-icon-area {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.card-icon {
  font-size: 36px;
  display: block;
  transition: transform 0.25s ease;
}

.card-badge {
  font-size: 10px;
  font-weight: 600;
  padding: 3px 8px;
  border-radius: 999px;
  background: var(--accent);
  color: #fff;
  letter-spacing: 0.5px;
}

.card-title {
  font-size: 17px;
  font-weight: 600;
  color: var(--text-primary);
  letter-spacing: -0.01em;
}

.card-desc {
  font-size: 13px;
  color: var(--text-secondary);
  line-height: 1.6;
  flex: 1;
}

.card-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.tag {
  font-size: 11px;
  padding: 2px 8px;
  border-radius: 999px;
  background: var(--accent-bg);
  color: var(--accent);
  font-weight: 500;
}

.card-footer {
  display: flex;
  justify-content: flex-end;
  margin-top: 4px;
}

.enter-btn {
  font-size: 13px;
  color: var(--accent);
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 4px;
}

.arrow {
  transition: transform 0.25s ease;
  display: inline-block;
}

.coming-soon {
  font-size: 12px;
  color: var(--text-muted);
  font-style: italic;
}

@media (max-width: 768px) {
  .card-grid {
    grid-template-columns: 1fr;
  }

  .home-content {
    padding: 32px 16px 60px;
  }

  .logo-text {
    font-size: 24px;
  }
}
</style>
