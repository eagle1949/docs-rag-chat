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

export interface UploadUrlRequest {
  url: string
}

export interface AskQuestionRequest {
  question: string
  session_id: string
}

export interface AskStreamDonePayload {
  session_id: string
  sources: SourceItem[]
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

export const uploadUrlDocument = (appId: string, data: UploadUrlRequest) => {
  return post<UploadDocumentResponse>(`/apps/${encodePart(appId)}/rag/url/upload`, {
    body: data,
  })
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

export const askQuestionStream = async (
  appId: string,
  data: AskQuestionRequest,
  handlers: {
    onToken: (token: string) => void
    onDone: (payload: AskStreamDonePayload) => void
    onError: (message: string) => void
  },
) => {
  const response = await fetch(`${apiPrefix}/apps/${encodePart(appId)}/rag/ask/stream`, {
    method: 'POST',
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  })

  if (!response.ok || !response.body) {
    throw new Error(`流式请求失败: HTTP ${response.status}`)
  }
  const contentType = response.headers.get('content-type') || ''
  if (!contentType.includes('text/event-stream')) {
    const payload = await response.json().catch(() => null)
    const msg = payload?.data?.message || payload?.message || '接口未返回 SSE 流'
    throw new Error(msg)
  }

  const reader = response.body.getReader()
  const decoder = new TextDecoder('utf-8')
  let buffer = ''
  let donePayload: AskStreamDonePayload | null = null

  const processDataLine = (dataText: string) => {
    const text = dataText.trim()
    if (!text) return

    if (text === '[DONE]') {
      handlers.onDone(donePayload || { session_id: data.session_id, sources: [] })
      donePayload = null
      return
    }

    try {
      const payload = JSON.parse(text) as {
        content?: string
        error?: string
        done?: boolean
        session_id?: string
        sources?: SourceItem[]
        message?: string
      }

      if (payload.error) {
        handlers.onError(payload.error)
        return
      }
      if (typeof payload.content === 'string') {
        handlers.onToken(payload.content)
      }
      if (payload.done) {
        donePayload = {
          session_id: payload.session_id || data.session_id,
          sources: payload.sources || [],
        }
      }
    } catch {
      // Backward compatibility: plain token string
      handlers.onToken(dataText)
    }
  }

  while (true) {
    const { done, value } = await reader.read()
    if (done) break

    buffer += decoder.decode(value, { stream: true })
    const lines = buffer.split(/\r?\n/)
    buffer = lines.pop() || ''
    for (const line of lines) {
      if (!line.startsWith('data:')) continue
      const raw = line.slice(5)
      processDataLine(raw.startsWith(' ') ? raw.slice(1) : raw)
    }
  }

  if (buffer.trim().startsWith('data:')) {
    const raw = buffer.trim().slice(5)
    processDataLine(raw.startsWith(' ') ? raw.slice(1) : raw)
  }
  if (donePayload) {
    handlers.onDone(donePayload)
  }
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
