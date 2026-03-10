import { get, post } from '@/utils/request'

// RAG API接口类型定义
export interface UploadDocumentResponse {
  code: string
  data: {
    filename: string
    size: number
    chunks: number
    message: string
  }
  message: string
}

export interface AskQuestionRequest {
  question: string
}

export interface AskQuestionResponse {
  code: string
  data: {
    answer: string
    sources: SourceItem[]
  }
  message: string
}

export interface SourceItem {
  filename: string
  chunk_id: number
  content: string
  score: number
}

export interface DocumentItem {
  filename: string
  size: number
  chunks: number
}

// 上传文档
export const uploadDocument = (file: File) => {
  const formData = new FormData()
  formData.append('file', file)

  return fetch('/api/rag/documents/upload', {
    method: 'POST',
    body: formData,
  }).then((res) => res.json())
}

// 提问
export const askQuestion = (data: AskQuestionRequest) => {
  return post<AskQuestionResponse>('/rag/ask', { body: data })
}
