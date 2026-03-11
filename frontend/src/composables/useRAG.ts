import { computed, ref } from 'vue'
import {
  askQuestion,
  clearSessionMemory,
  deleteDocument,
  listDocuments,
  uploadDocument,
  type DocumentItem,
  type SourceItem,
} from '@/api/rag'
import { Message } from '@arco-design/web-vue'

export interface QAItem {
  question: string
  answer: string
  sources: SourceItem[]
  createdAt: string
}

export function useRAG() {
  const appId = ref('default')
  const sessionId = ref(`session_${Date.now()}`)

  const uploadedDocuments = ref<DocumentItem[]>([])
  const qaHistory = ref<QAItem[]>([])

  const isUploading = ref(false)
  const isAsking = ref(false)
  const isLoadingDocuments = ref(false)

  const currentQuestion = computed(() => {
    const last = qaHistory.value[qaHistory.value.length - 1]
    return last?.question || ''
  })

  const currentAnswer = computed(() => {
    const last = qaHistory.value[qaHistory.value.length - 1]
    return last?.answer || ''
  })

  const currentSources = computed(() => {
    const last = qaHistory.value[qaHistory.value.length - 1]
    return last?.sources || []
  })

  const loadDocuments = async () => {
    try {
      isLoadingDocuments.value = true
      const response = await listDocuments(appId.value)
      if (response.code === 'success') {
        uploadedDocuments.value = response.data.documents || []
      } else {
        Message.error(response.message || '获取文档列表失败')
      }
    } catch (error: any) {
      Message.error(`获取文档列表失败: ${error.message || '未知错误'}`)
    } finally {
      isLoadingDocuments.value = false
    }
  }

  const handleFileUpload = async (file: File) => {
    try {
      isUploading.value = true
      const response = await uploadDocument(appId.value, file)

      if (response.code === 'success') {
        await loadDocuments()
        Message.success(`成功上传 ${file.name}`)
        return true
      }

      Message.error(response.data?.message || response.message || '上传失败')
      return false
    } catch (error: any) {
      Message.error(`上传失败: ${error.message || '未知错误'}`)
      return false
    } finally {
      isUploading.value = false
    }
  }

  const handleDeleteDocument = async (documentId: string) => {
    try {
      const response = await deleteDocument(appId.value, documentId)
      if (response.code === 'success') {
        uploadedDocuments.value = uploadedDocuments.value.filter((item) => item.document_id !== documentId)
        Message.success('文档删除成功')
      } else {
        Message.error(response.data?.message || response.message || '文档删除失败')
      }
    } catch (error: any) {
      Message.error(`文档删除失败: ${error.message || '未知错误'}`)
    }
  }

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
      const response = await askQuestion(appId.value, {
        question,
        session_id: sessionId.value,
      })

      if (response.code === 'success') {
        qaHistory.value.push({
          question,
          answer: response.data.answer,
          sources: response.data.sources || [],
          createdAt: new Date().toISOString(),
        })
        Message.success('回答生成成功')
      } else {
        Message.error(response.message || '提问失败')
      }
    } catch (error: any) {
      Message.error(`提问失败: ${error.message || '未知错误'}`)
    } finally {
      isAsking.value = false
    }
  }

  const clearConversation = async () => {
    try {
      await clearSessionMemory(appId.value, sessionId.value)
    } catch {
      // 后端清理失败不影响前端本地清空
    }

    qaHistory.value = []
    Message.info('会话已清空')
  }

  const switchApp = async (nextAppId: string) => {
    const normalized = nextAppId.trim() || 'default'
    appId.value = normalized
    qaHistory.value = []
    await loadDocuments()
  }

  return {
    appId,
    sessionId,
    uploadedDocuments,
    qaHistory,
    currentQuestion,
    currentAnswer,
    currentSources,
    isUploading,
    isAsking,
    isLoadingDocuments,
    loadDocuments,
    switchApp,
    handleFileUpload,
    handleDeleteDocument,
    handleAskQuestion,
    clearConversation,
  }
}
