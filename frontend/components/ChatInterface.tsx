'use client'

import { useState, useRef, useEffect } from 'react'
import axios from 'axios'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

interface ChatInterfaceProps {
  paperId: string
  paper2Id?: string
}

interface Message {
  role: 'user' | 'assistant'
  content: string
  isRelevant?: boolean
  relevanceScore?: number
}

export default function ChatInterface({ paperId, paper2Id }: ChatInterfaceProps) {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [explanationLevel, setExplanationLevel] = useState<'simple' | 'technical'>('technical')
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!input.trim() || loading) return

    const userMessage: Message = {
      role: 'user',
      content: input,
    }
    setMessages((prev) => [...prev, userMessage])
    setInput('')
    setLoading(true)

    try {
      const response = await axios.post(
        `${API_URL}/api/ask`,
        {
          paper_id: paperId,
          question: input,
          explanation_level: explanationLevel,
          paper2_id: paper2Id,
        },
        { timeout: 120000 }
      )

      const assistantMessage: Message = {
        role: 'assistant',
        content: response.data.answer,
        isRelevant: response.data.is_relevant,
        relevanceScore: response.data.relevance_score,
      }

      setMessages((prev) => [...prev, assistantMessage])
    } catch (error: any) {
      const errorMessage: Message = {
        role: 'assistant',
        content: error.response?.data?.detail || error.message || 'Failed to get response',
        isRelevant: false,
      }
      setMessages((prev) => [...prev, errorMessage])
    } finally {
      setLoading(false)
    }
  }

  const getRelevanceTier = (score?: number): 'high' | 'medium' | 'low' => {
    if (score === undefined) return 'low'
    if (score >= 0.5) return 'high'
    if (score >= 0.3) return 'medium'
    return 'low'
  }

  return (
    <div>
      <div style={{ marginBottom: '1.5rem', display: 'flex', gap: '1rem', alignItems: 'center', flexWrap: 'wrap' }}>
        <label style={{ fontWeight: '600', color: '#2F3E34', fontSize: '0.95rem' }}>Explanation Level:</label>
        <select
          value={explanationLevel}
          onChange={(e) => setExplanationLevel(e.target.value as 'simple' | 'technical')}
          className="input"
          style={{ width: 'auto', padding: '0.625rem 1rem', minWidth: '150px' }}
        >
          <option value="simple">Simple</option>
          <option value="technical">Technical</option>
        </select>
      </div>

      <div
        style={{
          height: '450px',
          overflowY: 'auto',
          border: '1px solid #E5E7E6',
          borderRadius: '10px',
          padding: '1.5rem',
          marginBottom: '1.5rem',
          background: '#FFFFFF',
        }}
      >
        {messages.length === 0 && (
          <div style={{ textAlign: 'center', color: '#999999', padding: '3rem 1rem' }}>
            <p style={{ fontSize: '1.1rem', marginBottom: '0.5rem', color: '#666666' }}>Ask questions about the uploaded paper(s)</p>
            <p style={{ fontSize: '0.9rem', lineHeight: '1.6' }}>
              The AI will answer based strictly on the paper content
            </p>
          </div>
        )}

        {messages.map((message, idx) => {
          const relevanceTier = message.relevanceScore !== undefined ? getRelevanceTier(message.relevanceScore) : 'low'
          return (
            <div
              key={idx}
              className={`chat-message ${message.role}`}
              style={{ marginBottom: '1.25rem' }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem' }}>
                <div style={{ fontWeight: '600', color: '#2F3E34', fontSize: '0.95rem' }}>
                  {message.role === 'user' ? 'You' : 'Assistant'}
                </div>
                {message.relevanceScore !== undefined && (
                  <div className={`relevance-badge ${relevanceTier}`} style={{ flexDirection: 'column', alignItems: 'flex-end', gap: '0.25rem' }}>
                    <span style={{ fontSize: '0.8rem' }}>Relevance: {(message.relevanceScore * 100).toFixed(0)}%</span>
                    <div className="relevance-bar" style={{ width: '80px', height: '4px' }}>
                      <div 
                        className={`relevance-bar-fill ${relevanceTier}`}
                        style={{ width: `${message.relevanceScore * 100}%` }}
                      />
                    </div>
                  </div>
                )}
              </div>
              <div style={{ whiteSpace: 'pre-wrap', lineHeight: '1.7', color: '#333333', fontSize: '0.95rem' }}>
                {message.content}
              </div>
              {message.isRelevant === false && (
                <div style={{ marginTop: '0.75rem', padding: '0.75rem', background: '#F4F6F5', borderRadius: '6px', fontSize: '0.9rem', color: '#666666', borderLeft: '3px solid #B0B0B0' }}>
                  This answer is based on limited context from the paper
                </div>
              )}
            </div>
          )
        })}

        {loading && (
          <div className="chat-message assistant">
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', color: '#666666' }}>
              <span className="loading"></span>
              <span>Thinking...</span>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      <form onSubmit={handleSubmit}>
        <div style={{ display: 'flex', gap: '0.75rem' }}>
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="What is the main objective of this paper?"
            className="input"
            disabled={loading}
            style={{ flex: 1, fontSize: '1rem', padding: '1rem' }}
          />
          <button type="submit" disabled={loading || !input.trim()} className="button" style={{ padding: '1rem 2rem' }}>
            {loading ? (
              <span className="loading" style={{ width: '16px', height: '16px' }} />
            ) : (
              'Ask'
            )}
          </button>
        </div>
      </form>

      <p style={{ marginTop: '1rem', fontSize: '0.85rem', color: '#999999', textAlign: 'center', lineHeight: '1.5' }}>
        💡 Tip: Ask specific questions about methodology, results, datasets, or limitations
      </p>
    </div>
  )
}




