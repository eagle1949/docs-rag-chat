import { computed, ref } from 'vue'
import {
  askQuestionStream,
  clearSessionMemory,
  deleteDocument,
  listDocuments,
  uploadDocument,
  uploadUrlDocument,
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

  const handleUrlUpload = async (url: string) => {
    const normalized = url.trim()
    if (!normalized) {
      Message.warning('请输入链接')
      return false
    }

    try {
      isUploading.value = true
      const response = await uploadUrlDocument(appId.value, { url: normalized })
      if (response.code === 'success') {
        await loadDocuments()
        Message.success('链接解析并入库成功')
        return true
      }
      Message.error(response.data?.message || response.message || '链接解析失败')
      return false
    } catch (error: any) {
      Message.error(`链接解析失败: ${error.message || '未知错误'}`)
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
      const qaItem: QAItem = {
        question,
        answer: '',
        sources: [],
        createdAt: new Date().toISOString(),
      }
      qaHistory.value.push(qaItem)
      const qaIndex = qaHistory.value.length - 1

      await askQuestionStream(
        appId.value,
        {
          question,
          session_id: sessionId.value,
        },
        {
          onToken: (token: string) => {
            const current = qaHistory.value[qaIndex]
            if (!current) return
            current.answer += token
          },
          onDone: (payload) => {
            const current = qaHistory.value[qaIndex]
            if (!current) return
            current.sources = payload.sources || []
          },
          onError: (message: string) => {
            const current = qaHistory.value[qaIndex]
            if (!current) return
            current.answer = current.answer || message
          },
        },
      )

      const current = qaHistory.value[qaIndex]
      if (current && !current.answer.trim()) {
        current.answer = '根据当前会话记忆和文档内容，我无法回答这个问题。'
      }
      Message.success('回答生成成功')
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
    handleUrlUpload,
    handleDeleteDocument,
    handleAskQuestion,
    clearConversation,
  }
}
