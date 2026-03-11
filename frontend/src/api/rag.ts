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

  const processEventBlock = (block: string) => {
    const lines = block.split('\n')
    let event = 'message'
    const dataLines: string[] = []
    for (const line of lines) {
      if (line.startsWith('event:')) {
        event = line.slice(6).trim()
      } else if (line.startsWith('data:')) {
        // Keep token leading spaces from SSE payload (only strip the protocol delimiter space).
        const raw = line.slice(5)
        dataLines.push(raw.startsWith(' ') ? raw.slice(1) : raw)
      }
    }
    const dataText = dataLines.join('\n')
    if (event === 'token') {
      handlers.onToken(dataText)
      return
    }
    if (event === 'done') {
      try {
        handlers.onDone(JSON.parse(dataText) as AskStreamDonePayload)
      } catch {
        handlers.onDone({ session_id: data.session_id, sources: [] })
      }
      return
    }
    if (event === 'error') {
      try {
        const payload = JSON.parse(dataText) as { message?: string }
        handlers.onError(payload.message || '流式响应出错')
      } catch {
        handlers.onError(dataText || '流式响应出错')
      }
    }
  }

  while (true) {
    const { done, value } = await reader.read()
    if (done) break

    buffer += decoder.decode(value, { stream: true })
    const blocks = buffer.split('\n\n')
    buffer = blocks.pop() || ''
    for (const block of blocks) {
      if (block.trim()) processEventBlock(block)
    }
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
