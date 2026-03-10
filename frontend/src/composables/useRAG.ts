import { ref } from 'vue'
import { uploadDocument, askQuestion, type DocumentItem, type SourceItem } from '@/api/rag'
import { Message } from '@arco-design/web-vue'

export function useRAG() {
  // 状态管理
  const uploadedDocuments = ref<DocumentItem[]>([])
  const currentQuestion = ref('')
  const currentAnswer = ref('')
  const currentSources = ref<SourceItem[]>([])
  const isUploading = ref(false)
  const isAsking = ref(false)

  // 上传文档
  const handleFileUpload = async (file: File) => {
    try {
      isUploading.value = true

      const response = await uploadDocument(file)

      if (response.code === 'success') {
        uploadedDocuments.value.push({
          filename: response.data.filename,
          size: response.data.size,
          chunks: response.data.chunks,
        })

        Message.success(`成功上传 ${file.name}`)
        return true
      } else {
        Message.error(response.data?.message || '上传失败')
        return false
      }
    } catch (error: any) {
      Message.error(`上传失败: ${error.message || '未知错误'}`)
      return false
    } finally {
      isUploading.value = false
    }
  }

  // 提问
  const handleAskQuestion = async (question: string) => {
    if (!question.trim()) {
      Message.warning('请输入问题')
      return
    }

    if (uploadedDocuments.value.length === 0) {
      Message.warning('请先上传文档')
      return
    }

    try {
      isAsking.value = true
      currentQuestion.value = question
      currentAnswer.value = ''
      currentSources.value = []

      const response = await askQuestion({ question })

      if (response.code === 'success') {
        currentAnswer.value = response.data.answer
        currentSources.value = response.data.sources
        Message.success('回答生成成功')
      } else {
        Message.error(response.data?.message || '提问失败')
      }
    } catch (error: any) {
      Message.error(`提问失败: ${error.message || '未知错误'}`)
    } finally {
      isAsking.value = false
    }
  }

  // 清空所有文档
  const clearDocuments = () => {
    uploadedDocuments.value = []
    currentQuestion.value = ''
    currentAnswer.value = ''
    currentSources.value = []
    Message.info('已清空所有文档')
  }

  return {
    // 状态
    uploadedDocuments,
    currentQuestion,
    currentAnswer,
    currentSources,
    isUploading,
    isAsking,

    // 方法
    handleFileUpload,
    handleAskQuestion,
    clearDocuments,
  }
}
