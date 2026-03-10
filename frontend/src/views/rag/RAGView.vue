<script setup lang="ts">
import { ref, computed } from 'vue'
import { Message } from '@arco-design/web-vue'
import { useRAG } from '@/composables/useRAG'

// 使用RAG composable
const {
  uploadedDocuments,
  currentQuestion,
  currentAnswer,
  currentSources,
  isUploading,
  isAsking,
  handleFileUpload,
  handleAskQuestion,
  clearDocuments,
} = useRAG()

// 本地表单状态
const questionInput = ref('')
const selectedFile = ref<File | null>(null)
const fileInput = ref<HTMLInputElement | null>(null)

// 格式化文件大小
const formatFileSize = (bytes: number) => {
  return `${(bytes / 1024).toFixed(1)} KB`
}

// 处理文件选择
const handleFileSelect = (event: Event) => {
  const target = event.target as HTMLInputElement
  const files = target.files

  if (files && files.length > 0) {
    const file = files[0]
    if (!file.name.endsWith('.md') && !file.name.endsWith('.txt')) {
      Message.error('仅支持 .md 和 .txt 文件')
      return
    }
    selectedFile.value = file
  }
}

// 触发文件选择
const triggerFileSelect = () => {
  fileInput.value?.click()
}

// 处理文件上传
const handleUploadClick = async () => {
  if (!selectedFile.value) {
    Message.warning('请先选择文件')
    return
  }

  const success = await handleFileUpload(selectedFile.value)
  if (success) {
    selectedFile.value = null
  }
}

// 处理提问
const handleSendQuestion = async () => {
  if (!questionInput.value.trim()) {
    Message.warning('请输入问题')
    return
  }

  await handleAskQuestion(questionInput.value)
  questionInput.value = ''
}

// 文档列表空状态提示
const emptyDocumentsText = computed(() => {
  return uploadedDocuments.value.length === 0 ? '暂无文档' : ''
})

// 来源列表空状态提示
const emptySourcesText = computed(() => {
  return currentSources.value.length === 0 ? '暂无参考来源' : ''
})
</script>

<template>
  <div class="rag-container">
    <!-- 左侧：文档管理区 -->
    <div class="left-panel">
      <div class="panel-header">
        <h2 class="panel-title">Document Q&A</h2>
      </div>

      <div class="upload-section">
        <input
          ref="fileInput"
          type="file"
          accept=".md,.txt"
          style="display: none"
          @change="handleFileSelect"
        />
        <div class="upload-btn" @click="triggerFileSelect">
          <icon-upload />
          <span>Upload Files</span>
        </div>

        <div v-if="selectedFile" class="selected-file">
          <span class="file-name">{{ selectedFile.name }}</span>
          <button class="upload-action-btn" :disabled="isUploading" @click="handleUploadClick">
            {{ isUploading ? 'Uploading...' : 'Upload' }}
          </button>
        </div>

        <p class="upload-hint">Select or upload your documents below</p>
      </div>

      <div class="documents-section">
        <h3 class="section-title">Documents ({{ uploadedDocuments.length }})</h3>

        <div v-if="uploadedDocuments.length === 0" class="empty-state">
          <icon-file />
          <p>No documents uploaded</p>
        </div>

        <div v-else class="documents-list">
          <div
            v-for="(doc, index) in uploadedDocuments"
            :key="index"
            class="document-item"
          >
            <div class="document-info">
              <icon-file />
              <div class="document-details">
                <div class="document-name">{{ doc.filename }}</div>
                <div class="document-meta">
                  {{ formatFileSize(doc.size) }} · {{ doc.chunks }} chunks
                </div>
              </div>
            </div>
          </div>
        </div>

        <button v-if="uploadedDocuments.length > 0" class="clear-btn" @click="clearDocuments">
          Clear All
        </button>
      </div>
    </div>

    <!-- 中间：问答交互区 -->
    <div class="middle-panel">
      <div class="panel-header">
        <h2 class="panel-title">Ask a Question</h2>
      </div>

      <div class="qa-display">
        <div v-if="currentQuestion" class="question-box">
          <label>You:</label>
          <div class="question-content">{{ currentQuestion }}</div>
        </div>

        <div v-if="currentAnswer || isAsking" class="answer-box">
          <label>AI:</label>
          <div v-if="isAsking" class="loading-state">
            <icon-loading />
            <span>Thinking...</span>
          </div>
          <div v-else class="answer-content">{{ currentAnswer }}</div>
        </div>

        <div v-if="!currentQuestion && !currentAnswer" class="placeholder-state">
          <icon-question-circle />
          <p>Ask a question about your documents...</p>
        </div>
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
            class="send-btn"
            :disabled="isAsking || !questionInput.trim() || uploadedDocuments.length === 0"
            @click="handleSendQuestion"
          >
            <icon-send v-if="!isAsking" />
            <icon-loading v-else />
            <span>{{ isAsking ? 'Sending...' : 'Send' }}</span>
          </button>
        </div>
        <p v-if="uploadedDocuments.length === 0" class="input-hint">
          Please upload documents first
        </p>
      </div>
    </div>

    <!-- 右侧：参考来源区 -->
    <div class="right-panel">
      <div class="panel-header">
        <h2 class="panel-title">References ({{ currentSources.length }})</h2>
      </div>

      <div v-if="currentSources.length === 0" class="empty-state">
        <icon-bookmark />
        <p>No references available</p>
      </div>

      <div v-else class="references-list">
        <div v-for="(source, index) in currentSources" :key="index" class="reference-item">
          <div class="reference-header">
            <div class="reference-title">Source {{ index + 1 }}: {{ source.filename }}</div>
            <div class="reference-meta">
              Score: {{ (source.score * 100).toFixed(1) }}% | Chunk: {{ source.chunk_id }}
            </div>
          </div>
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

/* 左侧面板 */
.left-panel {
  flex: 1;
  background-color: white;
  border-radius: 8px;
  padding: 20px;
  border: 1px solid #ddd;
}

/* 中间面板 */
.middle-panel {
  flex: 2;
  background-color: white;
  border-radius: 8px;
  padding: 20px;
  border: 1px solid #ddd;
}

/* 右侧面板 */
.right-panel {
  flex: 1;
  background-color: white;
  border-radius: 8px;
  padding: 20px;
  border: 1px solid #ddd;
}

/* 通用样式 */
.panel-header {
  margin-bottom: 20px;
  padding-bottom: 10px;
  border-bottom: 2px solid #333;
}

.panel-title {
  font-size: 18px;
  font-weight: bold;
  margin: 0;
  color: #333;
}

/* 上传区域 */
.upload-section {
  margin-bottom: 30px;
}

.upload-btn {
  width: 100%;
  padding: 12px;
  background-color: #e0e0e0;
  border: 1px solid #ccc;
  border-radius: 4px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  font-size: 14px;
  transition: background-color 0.3s;
}

.upload-btn:hover {
  background-color: #d0d0d0;
}

.selected-file {
  margin-top: 10px;
  padding: 10px;
  background-color: #f0f0f0;
  border-radius: 4px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.file-name {
  font-size: 14px;
  color: #333;
}

.upload-action-btn {
  padding: 6px 16px;
  background-color: #165dff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 13px;
  transition: background-color 0.3s;
}

.upload-action-btn:hover:not(:disabled) {
  background-color: #0e42d2;
}

.upload-action-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.upload-hint {
  margin-top: 8px;
  font-size: 12px;
  color: #666;
  text-align: center;
}

/* 文档列表 */
.documents-section {
  margin-top: 20px;
}

.section-title {
  font-size: 16px;
  margin-bottom: 15px;
  font-weight: 600;
  color: #333;
}

.empty-state {
  text-align: center;
  padding: 40px 20px;
  color: #999;
}

.empty-state svg {
  font-size: 48px;
  margin-bottom: 10px;
  opacity: 0.3;
}

.documents-list {
  margin-top: 10px;
}

.document-item {
  padding: 10px;
  border-bottom: 1px solid #eee;
}

.document-info {
  display: flex;
  align-items: flex-start;
  gap: 8px;
}

.document-details {
  flex: 1;
}

.document-name {
  font-size: 14px;
  font-weight: 500;
  color: #333;
  margin-bottom: 4px;
  word-break: break-all;
}

.document-meta {
  font-size: 12px;
  color: #666;
}

.clear-btn {
  margin-top: 15px;
  width: 100%;
  padding: 8px;
  background-color: #f53f3f;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 13px;
  transition: background-color 0.3s;
}

.clear-btn:hover {
  background-color: #d91a1a;
}

/* 问答区域 */
.qa-display {
  margin-bottom: 20px;
  min-height: 300px;
}

.question-box,
.answer-box {
  margin-bottom: 20px;
}

.question-box label,
.answer-box label {
  font-weight: bold;
  display: block;
  margin-bottom: 8px;
  color: #333;
  font-size: 14px;
}

.question-content,
.answer-content {
  padding: 12px;
  background-color: #f9f9f9;
  border: 1px solid #eee;
  border-radius: 4px;
  line-height: 1.6;
  white-space: pre-wrap;
  word-break: break-word;
}

.question-content {
  background-color: #e8f4ff;
  border-color: #bae7ff;
}

.loading-state {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px;
  color: #666;
}

.placeholder-state {
  text-align: center;
  padding: 60px 20px;
  color: #999;
}

.placeholder-state svg {
  font-size: 64px;
  margin-bottom: 15px;
  opacity: 0.3;
}

.placeholder-state p {
  margin: 0;
  font-size: 14px;
}

/* 输入区域 */
.input-section {
  margin-top: 20px;
}

.input-bar {
  display: flex;
  gap: 10px;
}

.question-input {
  flex: 1;
  padding: 12px;
  border: 1px solid #ccc;
  border-radius: 4px;
  font-size: 14px;
  outline: none;
  transition: border-color 0.3s;
}

.question-input:focus {
  border-color: #165dff;
}

.question-input:disabled {
  background-color: #f5f5f5;
  cursor: not-allowed;
}

.send-btn {
  padding: 12px 24px;
  background-color: #165dff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 6px;
  transition: background-color 0.3s;
  white-space: nowrap;
}

.send-btn:hover:not(:disabled) {
  background-color: #0e42d2;
}

.send-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.input-hint {
  margin-top: 8px;
  font-size: 12px;
  color: #999;
}

/* 参考来源 */
.references-list {
  margin-top: 10px;
}

.reference-item {
  margin-bottom: 20px;
  padding: 12px;
  background-color: #f9f9f9;
  border-radius: 4px;
  border: 1px solid #eee;
}

.reference-header {
  margin-bottom: 8px;
}

.reference-title {
  font-size: 13px;
  font-weight: 600;
  color: #333;
  margin-bottom: 4px;
}

.reference-meta {
  font-size: 11px;
  color: #999;
}

.reference-content {
  font-size: 12px;
  color: #666;
  line-height: 1.6;
  white-space: pre-wrap;
  word-break: break-word;
}
</style>
