import { BaseProvider } from './BaseProvider'
import type { APICallParams, AIResponse, ChatMessage, MessageContent, StreamChunk } from '../types'
import { ResponseCleaner } from '../utils/ResponseCleaner'

/**
 * OpenAI Responses API 提供商实现
 * 适用于需要使用 /v1/responses 协议的兼容服务
 */
export class OpenAIResponsesProvider extends BaseProvider {
  async callAPI(messages: ChatMessage[], stream: boolean, params?: APICallParams): Promise<AIResponse | ReadableStream<Uint8Array>> {
    if (!this.config.baseUrl) {
      throw new Error('API URL 未配置')
    }

    const apiUrl = this.buildApiUrl(this.config.baseUrl)
    const timeoutMs = this.getTimeout()

    const systemPrompt = this.extractSystemPrompt(messages)
    const userMessages = messages.filter(message => message.role !== 'system')

    const payload: Record<string, unknown> = {
      model: this.modelId,
      input: this.convertMessages(userMessages),
      temperature: params?.temperature ?? 1.0,
      max_output_tokens: params?.maxTokens ?? 8192,
      top_p: params?.topP ?? 0.95,
      ...(stream && { stream: true })
    }

    if (systemPrompt) {
      payload.system = systemPrompt
    }

    const response = await this.fetchWithTimeout(apiUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${this.config.apiKey}`
      },
      body: JSON.stringify(payload)
    }, timeoutMs)

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      const error = new Error(`OpenAI Responses API error: ${response.status} ${response.statusText}`)
      ;(error as any).error = errorData
      ;(error as any).status = response.status
      throw error
    }

    if (stream) {
      return response.body as ReadableStream<Uint8Array>
    }

    const data = await response.json()
    const result = this.extractOutputText(data)

    if (!result || result.trim() === '') {
      throw new Error('API返回空内容或无法解析响应格式')
    }

    return {
      content: ResponseCleaner.cleanThinkTags(ResponseCleaner.cleanResponse(result)),
      finishReason: data.done_reason
    }
  }

  parseStreamChunk(data: string): StreamChunk | null {
    const trimmed = data.trim()
    if (!trimmed) {
      return null
    }

    if (trimmed === '[DONE]') {
      return { content: '', done: true }
    }

    try {
      const parsed = JSON.parse(trimmed)
      const type = parsed.type || parsed.event

      let content: string | undefined

      if (typeof parsed.delta === 'string') {
        content = parsed.delta
      } else if (typeof parsed.output_text_delta === 'string') {
        content = parsed.output_text_delta
      } else if (typeof parsed.response?.output_text_delta === 'string') {
        content = parsed.response.output_text_delta
      } else if (typeof parsed.data?.delta === 'string') {
        content = parsed.data.delta
      } else if (typeof parsed.response?.delta === 'string') {
        content = parsed.response.delta
      }

      // 某些实现会把增量文本放在 output/output_text 层级
      if (!content && Array.isArray(parsed.output)) {
        for (const outputItem of parsed.output) {
          if (Array.isArray(outputItem.content)) {
            for (const part of outputItem.content) {
              if (typeof part.delta === 'string') {
                content = part.delta
                break
              }
              if (part.type === 'output_text' && typeof part.text === 'string') {
                content = part.text
                break
              }
            }
          }
          if (content) break
        }
      }

      const done =
        parsed.done === true ||
        parsed.done_reason !== undefined ||
        type === 'response.completed' ||
        type === 'response.output_text.done' ||
        (typeof type === 'string' && type.endsWith('.done'))

      return {
        content: content || '',
        done
      }
    } catch (error) {
      // JSON解析错误时忽略此chunk
      return null
    }
  }

  private buildApiUrl(baseUrl: string): string {
    let apiUrl = baseUrl.trim()

    if (apiUrl.includes('/responses')) {
      return apiUrl
    }

    if (apiUrl.includes('/v1')) {
      apiUrl = apiUrl.replace(/\/+$/, '') + '/responses'
    } else {
      apiUrl = apiUrl.replace(/\/+$/, '') + '/v1/responses'
    }

    return apiUrl
  }

  private getTimeout(): number {
    const isThinkingModel = this.modelId.includes('gpt-5') || this.modelId.includes('o1') || this.modelId.includes('thinking')
    return isThinkingModel ? 600000 : 300000
  }

  private convertMessages(messages: ChatMessage[]): Array<{ role: string; content: MessageContent[] }> {
    const converted = messages
      .map(message => ({
        role: message.role,
        content: this.convertContent(message)
      }))
      .filter(message => message.content.length > 0)

    if (converted.length === 0) {
      return [
        {
          role: 'user',
          content: [{ type: 'input_text', text: '' }]
        }
      ]
    }

    return converted
  }

  private extractSystemPrompt(messages: ChatMessage[]): string {
    const parts: string[] = []

    for (const message of messages) {
      if (message.role !== 'system') continue

      if (typeof message.content === 'string') {
        const trimmed = message.content.trim()
        if (trimmed) {
          parts.push(trimmed)
        }
      } else if (Array.isArray(message.content)) {
        for (const item of message.content) {
          if ('text' in item && typeof item.text === 'string') {
            const trimmed = item.text.trim()
            if (trimmed) {
              parts.push(trimmed)
            }
          }
        }
      }
    }

    return parts.join('\n\n')
  }

  private convertContent(message: ChatMessage): MessageContent[] {
    const content: MessageContent[] = []

    const getContentType = (existingType?: string): MessageContent['type'] => {
      if (existingType && !['text', 'input_text', 'output_text'].includes(existingType)) {
        return existingType as MessageContent['type']
      }

      if (message.role === 'system') {
        return 'text'
      }

      if (message.role === 'assistant') {
        return 'output_text'
      }

      return 'input_text'
    }

    if (typeof message.content === 'string' && message.content.trim()) {
      content.push({ type: getContentType(), text: message.content })
    } else if (Array.isArray(message.content)) {
      for (const item of message.content) {
        if (item.type === 'text' && typeof item.text === 'string' && item.text.trim()) {
          content.push({ type: getContentType(item.type), text: item.text })
        } else if (item.type && 'text' in item && typeof item.text === 'string' && item.text.trim()) {
          content.push({ ...item, type: getContentType(item.type), text: item.text })
        }
      }
    }

    return content
  }

  private extractOutputText(data: any): string | undefined {
    if (Array.isArray(data.output)) {
      for (const outputItem of data.output) {
        if (Array.isArray(outputItem.content)) {
          for (const part of outputItem.content) {
            if (part.type === 'output_text' && typeof part.text === 'string') {
              return part.text
            }
            if (typeof part.text === 'string') {
              return part.text
            }
          }
        }
      }
    }

    if (typeof data.output_text === 'string') {
      return data.output_text
    }

    if (typeof data.text === 'string') {
      return data.text
    }

    return undefined
  }
}
