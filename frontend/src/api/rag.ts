import { apiPrefix } from '@/config'
import { get, post } from '@/utils/request'

export interface UploadDocumentResponse {
  code: string
  data: {
    document_id: string
    filename: string
    size: number
    chunks: number
    message: string
  }
  message: string
}

export interface AskQuestionRequest {
  question: string
  session_id: string
}

export interface AskQuestionResponse {
  code: string
  data: {
    answer: string
    session_id: string
    sources: SourceItem[]
  }
  message: string
}

export interface SourceItem {
  document_id: string
  filename: string
  chunk_id: number
  content: string
  score: number
}

export interface DocumentItem {
  document_id: string
  filename: string
  size: number
  chunks: number
  created_at: string
}

export interface ListDocumentsResponse {
  code: string
  data: {
    documents: DocumentItem[]
  }
  message: string
}

const encodePart = (value: string) => encodeURIComponent(value)

export const uploadDocument = (appId: string, file: File) => {
  const formData = new FormData()
  formData.append('file', file)

  return fetch(`${apiPrefix}/apps/${encodePart(appId)}/rag/documents/upload`, {
    method: 'POST',
    body: formData,
    credentials: 'include',
  }).then((res) => res.json() as Promise<UploadDocumentResponse>)
}

export const listDocuments = (appId: string) => {
  return get<ListDocumentsResponse>(`/apps/${encodePart(appId)}/rag/documents`)
}

export const deleteDocument = (appId: string, documentId: string) => {
  return fetch(`${apiPrefix}/apps/${encodePart(appId)}/rag/documents/${encodePart(documentId)}`, {
    method: 'DELETE',
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
    },
  }).then((res) => res.json())
}

export const askQuestion = (appId: string, data: AskQuestionRequest) => {
  return post<AskQuestionResponse>(`/apps/${encodePart(appId)}/rag/ask`, { body: data })
}

export const clearSessionMemory = (appId: string, sessionId: string) => {
  return fetch(`${apiPrefix}/apps/${encodePart(appId)}/rag/sessions/${encodePart(sessionId)}/memory`, {
    method: 'DELETE',
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
    },
  }).then((res) => res.json())
}
