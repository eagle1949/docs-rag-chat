<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { Message } from '@arco-design/web-vue'
import { useRAG } from '@/composables/useRAG'

const {
  appId,
  sessionId,
  uploadedDocuments,
  qaHistory,
  isUploading,
  isAsking,
  isLoadingDocuments,
  loadDocuments,
  switchApp,
  handleFileUpload,
  handleDeleteDocument,
  handleAskQuestion,
  clearConversation,
} = useRAG()

const questionInput = ref('')
const selectedFile = ref<File | null>(null)
const fileInput = ref<HTMLInputElement | null>(null)
const appInput = ref(appId.value)

const formatFileSize = (bytes: number) => `${(bytes / 1024).toFixed(1)} KB`

const handleFileSelect = (event: Event) => {
  const target = event.target as HTMLInputElement
  const files = target.files
  if (!files || files.length === 0) return

  const file = files[0]
  if (!file.name.endsWith('.md') && !file.name.endsWith('.txt')) {
    Message.error('仅支持 .md 和 .txt 文件')
    return
  }
  selectedFile.value = file
}

const triggerFileSelect = () => {
  fileInput.value?.click()
}

const handleUploadClick = async () => {
  if (!selectedFile.value) {
    Message.warning('请先选择文件')
    return
  }

  const success = await handleFileUpload(selectedFile.value)
  if (success) {
    selectedFile.value = null
    if (fileInput.value) {
      fileInput.value.value = ''
    }
  }
}

const handleSendQuestion = async () => {
  if (!questionInput.value.trim()) {
    Message.warning('请输入问题')
    return
  }

  await handleAskQuestion(questionInput.value)
  questionInput.value = ''
}

const applyAppId = async () => {
  await switchApp(appInput.value)
}

const documentCountText = computed(() => {
  if (isLoadingDocuments.value) return 'Loading...'
  return `${uploadedDocuments.value.length}`
})

onMounted(async () => {
  await loadDocuments()
})
</script>

<template>
  <div class="rag-container">
    <div class="left-panel">
      <div class="panel-header">
        <h2 class="panel-title">Knowledge Base</h2>
      </div>

      <div class="config-section">
        <label class="field-label">App ID</label>
        <div class="inline-field">
          <input v-model="appInput" class="text-input" placeholder="default" />
          <button class="secondary-btn" @click="applyAppId">Apply</button>
        </div>

        <label class="field-label">Session ID</label>
        <input v-model="sessionId" class="text-input" placeholder="session_xxx" />
      </div>

      <div class="upload-section">
        <input
          ref="fileInput"
          type="file"
          accept=".md,.txt"
          style="display: none"
          @change="handleFileSelect"
        />
        <button class="primary-btn" @click="triggerFileSelect">Choose File</button>

        <div v-if="selectedFile" class="selected-file">
          <span class="file-name">{{ selectedFile.name }}</span>
          <button class="primary-btn" :disabled="isUploading" @click="handleUploadClick">
            {{ isUploading ? 'Uploading...' : 'Upload' }}
          </button>
        </div>
      </div>

      <div class="documents-section">
        <h3 class="section-title">Documents ({{ documentCountText }})</h3>

        <div v-if="uploadedDocuments.length === 0" class="empty-state">No documents</div>

        <div v-else class="documents-list">
          <div v-for="doc in uploadedDocuments" :key="doc.document_id" class="document-item">
            <div class="document-name">{{ doc.filename }}</div>
            <div class="document-meta">{{ formatFileSize(doc.size) }} | {{ doc.chunks }} chunks</div>
            <div class="document-actions">
              <button class="danger-btn" @click="handleDeleteDocument(doc.document_id)">Delete</button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="middle-panel">
      <div class="panel-header">
        <h2 class="panel-title">Multi-turn Chat</h2>
      </div>

      <div class="qa-display">
        <div v-if="qaHistory.length === 0" class="empty-state">Start asking questions...</div>

        <div v-else class="history-list">
          <div v-for="(item, index) in qaHistory" :key="`${item.createdAt}-${index}`" class="history-item">
            <div class="question-box">
              <label>You</label>
              <div class="content">{{ item.question }}</div>
            </div>
            <div class="answer-box">
              <label>AI</label>
              <div class="content">{{ item.answer }}</div>
            </div>
          </div>
        </div>

        <div v-if="isAsking" class="loading-state">Thinking...</div>
      </div>

      <div class="input-section">
        <div class="input-bar">
          <input
            v-model="questionInput"
            type="text"
            class="question-input"
            placeholder="Type your question..."
            :disabled="isAsking || uploadedDocuments.length === 0"
            @keypress.enter="handleSendQuestion"
          />
          <button
            class="primary-btn"
            :disabled="isAsking || !questionInput.trim() || uploadedDocuments.length === 0"
            @click="handleSendQuestion"
          >
            {{ isAsking ? 'Sending...' : 'Send' }}
          </button>
        </div>
        <div class="inline-actions">
          <button class="secondary-btn" @click="clearConversation">Clear Session</button>
        </div>
      </div>
    </div>

    <div class="right-panel">
      <div class="panel-header">
        <h2 class="panel-title">References</h2>
      </div>

      <div v-if="qaHistory.length === 0" class="empty-state">No references</div>
      <div v-else class="references-list">
        <div
          v-for="(source, index) in qaHistory[qaHistory.length - 1].sources"
          :key="`${source.document_id}-${index}`"
          class="reference-item"
        >
          <div class="reference-title">{{ source.filename }} (chunk {{ source.chunk_id }})</div>
          <div class="reference-meta">Score: {{ (source.score * 100).toFixed(1) }}%</div>
          <div class="reference-content">{{ source.content }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.rag-container {
  display: flex;
  min-height: calc(100vh - 120px);
  background-color: #f5f5f5;
  padding: 20px;
  gap: 20px;
}

.left-panel,
.middle-panel,
.right-panel {
  background: #fff;
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 16px;
}

.left-panel {
  flex: 1;
}

.middle-panel {
  flex: 2;
}

.right-panel {
  flex: 1;
}

.panel-header {
  margin-bottom: 12px;
  padding-bottom: 8px;
  border-bottom: 2px solid #333;
}

.panel-title {
  margin: 0;
  font-size: 18px;
  font-weight: 700;
}

.config-section,
.upload-section,
.documents-section,
.input-section {
  margin-bottom: 16px;
}

.field-label {
  display: block;
  margin-bottom: 4px;
  font-size: 12px;
  color: #666;
}

.inline-field {
  display: flex;
  gap: 8px;
  margin-bottom: 10px;
}

.text-input,
.question-input {
  width: 100%;
  border: 1px solid #ccc;
  border-radius: 4px;
  padding: 8px;
  font-size: 14px;
}

.input-bar {
  display: flex;
  gap: 8px;
}

.primary-btn,
.secondary-btn,
.danger-btn {
  border: none;
  border-radius: 4px;
  padding: 8px 12px;
  cursor: pointer;
}

.primary-btn {
  background: #165dff;
  color: #fff;
}

.secondary-btn {
  background: #e5e7eb;
  color: #111827;
}

.danger-btn {
  background: #ef4444;
  color: #fff;
}

.selected-file {
  margin-top: 10px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 8px;
}

.file-name {
  font-size: 13px;
  word-break: break-all;
}

.section-title {
  margin: 0 0 10px;
  font-size: 15px;
}

.documents-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.document-item {
  border: 1px solid #eee;
  border-radius: 6px;
  padding: 10px;
}

.document-name {
  font-size: 14px;
  font-weight: 600;
  margin-bottom: 4px;
}

.document-meta {
  font-size: 12px;
  color: #666;
}

.document-actions {
  margin-top: 8px;
}

.qa-display {
  min-height: 340px;
}

.history-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  max-height: 480px;
  overflow-y: auto;
}

.history-item {
  border: 1px solid #eee;
  border-radius: 6px;
  padding: 10px;
}

.question-box label,
.answer-box label {
  font-size: 12px;
  color: #666;
}

.content {
  margin-top: 4px;
  white-space: pre-wrap;
  word-break: break-word;
  line-height: 1.6;
}

.question-box .content {
  background: #f0f7ff;
  padding: 8px;
  border-radius: 4px;
}

.answer-box .content {
  background: #f9fafb;
  padding: 8px;
  border-radius: 4px;
}

.inline-actions {
  margin-top: 10px;
}

.references-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.reference-item {
  border: 1px solid #eee;
  border-radius: 6px;
  padding: 10px;
  background: #fafafa;
}

.reference-title {
  font-size: 13px;
  font-weight: 600;
}

.reference-meta {
  font-size: 12px;
  color: #666;
  margin: 4px 0;
}

.reference-content {
  font-size: 12px;
  white-space: pre-wrap;
  word-break: break-word;
  line-height: 1.6;
}

.empty-state,
.loading-state {
  color: #999;
  padding: 20px 0;
  text-align: center;
}

@media (max-width: 1024px) {
  .rag-container {
    flex-direction: column;
  }
}
</style>
