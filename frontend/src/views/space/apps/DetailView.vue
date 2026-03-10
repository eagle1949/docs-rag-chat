<script setup lang="ts">
import { ref, nextTick, onMounted, watch } from 'vue'
import {
  IconHome,
  IconUser,
  IconSearch,
  IconApps,
  IconPlus,
  IconArrowRight
} from '@arco-design/web-vue/es/icon'
import MarkdownIt from 'markdown-it'

// 初始化 markdown-it
const md = new MarkdownIt({
  html: true, // 允许 HTML 标签
  linkify: true, // 自动转换 URL 为链接
  typographer: true // 使用智能标点符号
})

const messageList = ref([
  {
    id: 1,
    type: 'system',
    content: '你好，欢迎来到慕课LLMOps😄\n\n慕课LLMOps是新一代大模型AI应用开发平台。无论你是否有编程基础，都可以快速搭建出各种AI应用，并一键发布到各大社交平台，或者轻松部署到自己的网站。\n\n• 随时来「应用广场」逛逛，这里内置了许多有趣的应用。\n• 你也可以直接发送「我想做一个应用」，我可以帮我快速创建应用。\n• 你也可以向我提问有关课程的问题，我可以快速替你解答。\n\n如果你还有其他慕课LLMOps使用问题，也欢迎随时问我！'
  }
])

// 渲染 Markdown 内容
const renderMarkdown = (content: string) => {
  return md.render(content)
}

const inputValue = ref('')
const quickQuestions = ref([
  // '什么是慕课LLMOps?',
  // '我想创建一个应用',
  // '能介绍下什么是RAG吗?'
])

// 聊天消息容器的引用
const chatMessagesRef = ref<HTMLElement | null>(null)

// 滚动到底部
const scrollToBottom = () => {
  nextTick(() => {
    if (chatMessagesRef.value) {
      // 使用 scrollHeight 确保滚动到最底部
      chatMessagesRef.value.scrollTo({
        top: chatMessagesRef.value.scrollHeight,
        behavior: 'smooth'
      })
    }
  })
}

// 监听消息变化,自动滚动到底部
watch(messageList, () => {
  scrollToBottom()
}, { deep: true })

// 组件挂载后滚动到底部
onMounted(() => {
  scrollToBottom()
})

async function sendMessage() {
  if (!inputValue.value.trim()) return

  const userMessage = inputValue.value.trim()

  // 添加用户消息
  messageList.value.push({
    id: messageList.value.length + 1,
    type: 'user',
    content: userMessage
  })

  inputValue.value = ''

  try {
    // 创建一个空的AI回复消息，用于流式更新
    const aiMessageId = messageList.value.length + 1
    messageList.value.push({
      id: aiMessageId,
      type: 'system',
      content: ''
    })

    // 调用后端API，使用流式响应
    const response = await fetch('/api/apps/123e4567-e89b-12d3-a456-426614174000/debug', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        query: userMessage
      })
    })

    if (!response.ok) {
      throw new Error('网络响应失败')
    }

    // 处理流式响应（极简版）
    const reader = response.body?.getReader()
    const decoder = new TextDecoder('utf-8')
    let buffer = ''
    let aiMessageContent = ''
    const msgIndex = messageList.value.findIndex(m => m.id === aiMessageId)

    try {
      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        // 累积数据并按行处理
        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split('\n')
        buffer = lines.pop() || '' // 保留不完整的行

        for (const line of lines) {
          if (!line.startsWith('data: ')) continue

          const jsonStr = line.slice(6).trim()
          if (jsonStr === '[DONE]' || !jsonStr) continue

          try {
            const parsed = JSON.parse(jsonStr)
            if (parsed.content) {
              aiMessageContent += parsed.content
              messageList.value[msgIndex].content = aiMessageContent
            }
          } catch (e) {
            console.error('解析失败:', e)
          }
        }
      }
    } finally {
      reader.releaseLock()
    }

    // 如果没有接收到任何内容
    if (!aiMessageContent) {
      const msgIndex = messageList.value.findIndex(m => m.id === aiMessageId)
      if (msgIndex !== -1) {
        messageList.value[msgIndex].content = '抱歉，没有收到响应内容。'
      }
    }
  } catch (error) {
    console.error('API调用失败:', error)
    messageList.value.push({
      id: messageList.value.length + 1,
      type: 'system',
      content: '网络错误，请检查后端服务是否正常运行。'
    })
  }
}

function sendQuickQuestion(question: string) {
  inputValue.value = question
  sendMessage()
}
</script>

<template>
  <div class="app-container">
    <!-- 左侧导航 -->
    <aside class="sidebar">
      <div class="sidebar-header">
        <h1 class="logo">慕课LLMOps</h1>
      </div>
      <nav class="nav-menu">
        <a-menu mode="vertical" :default-selected-keys="['3']">
          <a-menu-item key="1">
            <template #icon>
              <icon-home />
            </template>
            主页
          </a-menu-item>
          <a-menu-item key="2">
            <template #icon>
              <icon-user />
            </template>
            个人空间
          </a-menu-item>
          <a-menu-item key="3">
            <template #icon>
              <icon-search />
            </template>
            探索
          </a-menu-item>
          <a-menu-item key="4">
            <template #icon>
              <icon-apps />
            </template>
            应用广场
          </a-menu-item>
          <a-menu-item key="5">
            <template #icon>
              <icon-plugin />
            </template>
            插件广场
          </a-menu-item>
          <a-menu-item key="6">
            <template #icon>
              <icon-api />
            </template>
            开放API
          </a-menu-item>
        </a-menu>
      </nav>
      <div class="sidebar-footer">
        <a-button type="primary" long>
          <template #icon>
            <icon-plus />
          </template>
          创建AI应用
        </a-button>
      </div>
    </aside>

    <!-- 右侧主内容 -->
    <main class="main-content">
      <!-- <div class="welcome-section">
        <h2>Hi, 我是慕课 AI 应用构建器</h2>
        <h3>你的专属 AI 原生应用开发平台</h3>
        <p>说出你的创意，我可以快速帮你创建专属应用，一键轻松分享给朋友，也可以一键发布到慕课LLMOps平台、微信等多个渠道。</p>
      </div> -->

      <!-- 聊天界面 -->
      <div ref="chatMessagesRef" class="chat-container">
        <div class="chat-avatar">
          <a-avatar shape="circle" style="background-color: #36cfc9; color: white; width: 36px; height: 36px; font-size: 14px; line-height: 36px;">
            小课
          </a-avatar>
          <span class="avatar-name">慕小课</span>
        </div>

        <div class="chat-messages">
          <div v-for="msg in messageList" :key="msg.id" class="message-item" :class="msg.type">
            <!-- 系统消息使用 Markdown 渲染 -->
            <div v-if="msg.type === 'system'" class="message-content markdown-body" v-html="renderMarkdown(msg.content)"></div>
            <!-- 用户消息保持纯文本 -->
            <div v-else class="message-content">
              {{ msg.content }}
            </div>
          </div>
        </div>

        <!-- 快速问答 -->
        <div class="quick-questions">
          <span
            v-for="(question, index) in quickQuestions"
            :key="index"
            @click="sendQuickQuestion(question)"
            class="quick-question-link"
            :style="{ marginRight: index < quickQuestions.length - 1 ? '20px' : '0' }"
          >
            {{ question }}
          </span>
        </div>
      </div>

      <!-- 聊天输入 -->
      <div class="chat-input-wrapper">
        <div class="input-container">
          <div class="input-actions">
            <a-button type="text" size="small" class="action-btn">
              <template #icon>
                <icon-plus />
              </template>
            </a-button>
          </div>
          <a-input
            v-model="inputValue"
            placeholder="发送消息或创建AI应用..."
            @pressEnter="sendMessage"
            :bordered="false"
            class="chat-input"
          />
          <div class="input-send">
            <a-button @click="sendMessage" type="primary" size="small" :disabled="!inputValue.trim()" class="send-btn">
              <template #icon>
                <icon-arrow-right />
              </template>
            </a-button>
          </div>
        </div>
        <p class="disclaimer">内容由AI生成，无法确保真实准确，仅供参考。</p>
      </div>
    </main>
  </div>
</template>

<style scoped>
.app-container {
  display: flex;
  height: 100vh;
  background-color: #f8fafc;
}

/* 左侧导航 */
.sidebar {
  width: 200px;
  background-color: white;
  border-right: 1px solid #e2e8f0;
  display: flex;
  flex-direction: column;
  padding: 0;
}

.sidebar-header {
  padding: 20px 24px;
  border-bottom: 1px solid #e2e8f0;
}

.logo {
  font-size: 18px;
  font-weight: bold;
  color: #1e293b;
  margin: 0;
}

.nav-menu {
  flex: 1;
  padding: 20px 0;
}

.nav-menu :deep(.arco-menu-item) {
  padding: 12px 24px;
  font-size: 14px;
}

.nav-menu :deep(.arco-menu-item-selected) {
  background-color: #e0f2fe;
  color: #0ea5e9;
}

.sidebar-footer {
  padding: 20px;
}

.sidebar-footer :deep(.arco-btn-long) {
  width: 100%;
}

/* 右侧主内容 */
.main-content {
  flex: 1;
  padding: 24px 48px 48px 48px;
  overflow-y: auto;
  background: #ffffff;
  position: relative;
  display: flex;
  flex-direction: column;
}

/* 欢迎区域 */
.welcome-section {
  margin-bottom: 48px;
  color: #1e293b;
}

.welcome-section h2 {
  font-size: 28px;
  font-weight: bold;
  margin: 0 0 8px;
}

.welcome-section h3 {
  font-size: 16px;
  font-weight: 400;
  color: #64748b;
  margin: 0 0 16px;
}

.welcome-section p {
  font-size: 14px;
  color: #64748b;
  margin: 0;
  line-height: 1.6;
  max-width: 600px;
}

/* 聊天容器 */
.chat-container {
  flex: 1;
  max-width: 900px;
  width: 100%;
  margin: 0 auto;
  background-color: transparent;
  border-radius: 0;
  padding: 0;
  box-shadow: none;
  overflow-y: auto;
  overflow-x: hidden;
}

/* 自定义滚动条样式 */
.chat-container::-webkit-scrollbar {
  width: 6px;
}

.chat-container::-webkit-scrollbar-track {
  background: transparent;
}

.chat-container::-webkit-scrollbar-thumb {
  background-color: #e5e7eb;
  border-radius: 3px;
}

.chat-container::-webkit-scrollbar-thumb:hover {
  background-color: #d1d5db;
}

.chat-avatar {
  display: flex;
  align-items: center;
  margin-bottom: 16px;
}

.avatar-name {
  margin-left: 8px;
  font-size: 14px;
  font-weight: 500;
  color: #1e293b;
}

/* 聊天消息 */
.chat-messages {
  margin-bottom: 24px;
}

.message-item {
  margin-bottom: 16px;
  display: flex;
  align-items: flex-start;
}

.message-item.system {
  flex-direction: column;
  align-items: flex-start;
}

.message-item.user {
  justify-content: flex-end;
}

.message-content {
  max-width: 80%;
  padding: 12px 16px;
  line-height: 1.6;
  font-size: 15px;
  word-wrap: break-word;
  border-radius: 12px;
}

.message-item.system .message-content {
  color: #1e293b;
  background-color: #f7f7f8;
}

.message-item.user .message-content {
  color: #1e293b;
  background-color: #0ea5e9;
  color: white;
}

/* 快速问答 */
.quick-questions {
  margin-bottom: 24px;
}

.quick-question-link {
  color: #0284c7;
  font-size: 14px;
  cursor: pointer;
  text-decoration: underline;
  transition: color 0.2s;
}

.quick-question-link:hover {
  color: #0369a1;
}

/* 聊天输入 */
.chat-input-wrapper {
  margin-top: 24px;
  padding-bottom: 24px;
  max-width: 900px;
  margin-left: auto;
  margin-right: auto;
}

.input-container {
  
  display: flex;
  align-items: flex-end;
  background-color: #ffffff;
  border: 1px solid #e5e7eb;
  border-radius: 24px;
  padding: 16px 20px;
  transition: all 0.2s ease;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.04);

  width: 900px;
}

.input-container:hover {
  border-color: #d1d5db;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.input-container:focus-within {
  border-color: #0ea5e9;
  box-shadow: 0 4px 16px rgba(14, 165, 233, 0.15);
}

.input-actions {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-right: 12px;
  padding-bottom: 2px;
}

.action-btn {
  width: 32px;
  height: 32px;
  color: #666666;
  cursor: pointer;
  transition: all 0.2s;
  border-radius: 6px;
  background: transparent;
  border: none;
}

.action-btn:hover {
  color: #0ea5e9;
  background-color: rgba(14, 165, 233, 0.1);
}

.chat-input {
  flex: 1;
}

.chat-input :deep(.arco-input-wrapper) {
  border: none;
  box-shadow: none;
  background: transparent;
}

.chat-input :deep(.arco-input) {
  border: none;
  box-shadow: none;
  background: transparent;
  font-size: 15px;
  line-height: 1.5;
  color: #1e293b;
}

.chat-input :deep(.arco-input::placeholder) {
  color: #999999;
}

.chat-input :deep(.arco-input-wrapper) {
  padding: 0;
}

.input-send {
  margin-left: 12px;
  padding-bottom: 2px;
}

.send-btn {
  width: 32px;
  height: 32px;
  min-width: 32px;
  padding: 0;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #0ea5e9;
  border: none;
}

.send-btn:hover:not(:disabled) {
  background-color: #0284c7;
}

.send-btn:disabled {
  background-color: #e5e7eb;
  color: #9ca3af;
}

.disclaimer {
  margin-top: 12px;
  font-size: 12px;
  color: #94a3b8;
  text-align: center;
}

/* Markdown 样式 - OpenAI 风格 */
.markdown-body {
  overflow-x: auto;
  color: #1e293b;
}

.markdown-body :deep(h1),
.markdown-body :deep(h2),
.markdown-body :deep(h3),
.markdown-body :deep(h4),
.markdown-body :deep(h5),
.markdown-body :deep(h6) {
  margin-top: 24px;
  margin-bottom: 12px;
  font-weight: 600;
  line-height: 1.4;
  color: #1e293b;
}

.markdown-body :deep(h1) {
  font-size: 1.8em;
  margin-top: 0;
}

.markdown-body :deep(h2) {
  font-size: 1.4em;
  border-bottom: none;
  padding-bottom: 0;
  margin-top: 32px;
}

.markdown-body :deep(h3) {
  font-size: 1.2em;
}

.markdown-body :deep(p) {
  margin-top: 0;
  margin-bottom: 12px;
  line-height: 1.6;
}

.markdown-body :deep(p:first-child) {
  margin-top: 0;
}

.markdown-body :deep(code) {
  padding: 0.2em 0.4em;
  margin: 0;
  font-size: 0.9em;
  background-color: rgba(175, 184, 193, 0.2);
  border-radius: 3px;
  font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace;
}

.markdown-body :deep(pre) {
  padding: 12px;
  overflow: auto;
  font-size: 0.85em;
  line-height: 1.5;
  /* background-color: #f6f8fa; */
  border-radius: 6px;
  margin-bottom: 16px;
  /* border: 1px solid #e2e8f0; */
}

.markdown-body :deep(pre code) {
  padding: 0;
  background-color: transparent;
  border: none;
}

.markdown-body :deep(ul),
.markdown-body :deep(ol) {
  padding-left: 1.5em;
  margin-top: 0;
  margin-bottom: 12px;
  line-height: 1.6;
}

.markdown-body :deep(li) {
  margin-top: 0.25em;
  margin-bottom: 0.25em;
}

.markdown-body :deep(li > p) {
  margin-top: 0;
  margin-bottom: 0;
}

.markdown-body :deep(blockquote) {
  padding: 0 1em;
  color: #64748b;
  border-left: 3px solid #e2e8f0;
  margin: 16px 0;
}

.markdown-body :deep(blockquote p) {
  margin-bottom: 0;
}

.markdown-body :deep(table) {
  border-spacing: 0;
  border-collapse: collapse;
  margin-bottom: 16px;
  width: 100%;
}

.markdown-body :deep(table th),
.markdown-body :deep(table td) {
  padding: 8px 12px;
  border: 1px solid #e2e8f0;
  text-align: left;
}

.markdown-body :deep(table th) {
  font-weight: 600;
  background-color: #f8fafc;
}

.markdown-body :deep(table tr) {
  background-color: white;
  border-top: 1px solid #e2e8f0;
}

.markdown-body :deep(table tr:nth-child(2n)) {
  background-color: #f8fafc;
}

.markdown-body :deep(a) {
  color: #0969da;
  text-decoration: none;
}

.markdown-body :deep(a:hover) {
  text-decoration: underline;
}

.markdown-body :deep(img) {
  max-width: 100%;
  border-radius: 4px;
  margin: 8px 0;
}

.markdown-body :deep(hr) {
  height: 1px;
  padding: 0;
  margin: 24px 0;
  background-color: #e2e8f0;
  border: none;
}

.markdown-body :deep(strong) {
  font-weight: 600;
  color: #1e293b;
}

.markdown-body :deep(em) {
  font-style: italic;
}
</style>
