'use client'

import { useState } from 'react'
import PDFUpload from '@/components/PDFUpload'
import ChatInterface from '@/components/ChatInterface'
import ComparisonView from '@/components/ComparisonView'

type PaperData = {
  paper1_id: string
  paper2_id?: string
  mode: 'single' | 'comparison'
  paper1_name?: string
  paper2_name?: string
}

export default function Home() {
  const [papers, setPapers] = useState<PaperData | null>(null)
  const [mode, setMode] = useState<'upload' | 'chat' | 'compare'>('upload')

  const handleUploadSuccess = (data: PaperData) => {
    setPapers(data)
    setMode(data.mode === 'comparison' ? 'compare' : 'chat')
  }

  const handleReset = () => {
    setPapers(null)
    setMode('upload')
  }

  return (
    <div className="container">
      <header style={{ textAlign: 'center', marginBottom: '3rem' }}>
        <h1 style={{ fontSize: '2.5rem', marginBottom: '0.75rem', fontWeight: '700', color: '#2F3E34' }}>
          Research Paper RAG System
        </h1>
        <p style={{ fontSize: '1.1rem', color: '#666666', fontWeight: '400' }}>
          Upload papers, ask questions, and compare research using AI
        </p>
      </header>

      {mode === 'upload' && (
        <div className="card">
          <PDFUpload onUploadSuccess={handleUploadSuccess} />
        </div>
      )}

      {mode === 'chat' && papers && (
        <div className="card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
            <h2 style={{ fontSize: '1.75rem', color: '#2F3E34', fontWeight: '600' }}>Chat with Paper</h2>
            <button onClick={handleReset} className="button button-secondary">
              Upload New Paper
            </button>
          </div>
          <ChatInterface paperId={papers.paper1_id} paper2Id={papers.paper2_id} />
        </div>
      )}

      {mode === 'compare' && papers && papers.paper2_id && (
        <div className="card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
            <h2 style={{ fontSize: '1.75rem', color: '#2F3E34', fontWeight: '600' }}>Compare Papers</h2>
            <button onClick={handleReset} className="button button-secondary">
              Upload New Papers
            </button>
          </div>
          <ComparisonView paper1Id={papers.paper1_id} paper2Id={papers.paper2_id} />
        </div>
      )}
    </div>
  )
}




