'use client'

import { useState } from 'react'
import axios from 'axios'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

interface PDFUploadProps {
  onUploadSuccess: (data: { paper1_id: string; paper2_id?: string; mode: 'single' | 'comparison' }) => void
}

export default function PDFUpload({ onUploadSuccess }: PDFUploadProps) {
  const [paper1, setPaper1] = useState<File | null>(null)
  const [paper2, setPaper2] = useState<File | null>(null)
  const [mode, setMode] = useState<'single' | 'comparison'>('single')
  const [uploading, setUploading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)

  const handlePaper1Change = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setPaper1(e.target.files[0])
      setError(null)
    }
  }

  const handlePaper2Change = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setPaper2(e.target.files[0])
      setError(null)
    }
  }

  const handleUpload = async () => {
    if (!paper1) {
      setError('Please select at least one PDF file')
      return
    }

    if (mode === 'comparison' && !paper2) {
      setError('Please select a second PDF for comparison mode')
      return
    }

    setUploading(true)
    setError(null)
    setSuccess(null)

    // #region agent log
    fetch('http://127.0.0.1:7242/ingest/aef6e04e-f389-4efd-ae55-bef45c14ffca',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'PDFUpload.tsx:45',message:'Upload started',data:{paper1_name:paper1.name,paper1_size:paper1.size,mode:mode,paper2_name:paper2?.name,paper2_size:paper2?.size},timestamp:Date.now(),sessionId:'debug-session',runId:'upload',hypothesisId:'F'})}).catch(()=>{});
    // #endregion

    try {
      const formData = new FormData()
      formData.append('paper1', paper1)
      if (paper2 && mode === 'comparison') {
        formData.append('paper2', paper2)
      }

      // #region agent log
      fetch('http://127.0.0.1:7242/ingest/aef6e04e-f389-4efd-ae55-bef45c14ffca',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'PDFUpload.tsx:56',message:'Sending axios request',data:{url:`${API_URL}/api/upload`,timeout:300000},timestamp:Date.now(),sessionId:'debug-session',runId:'upload',hypothesisId:'F'})}).catch(()=>{});
      // #endregion

      const response = await axios.post(`${API_URL}/api/upload`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        timeout: 300000, // 5 minutes timeout for large PDFs
      })

      // #region agent log
      fetch('http://127.0.0.1:7242/ingest/aef6e04e-f389-4efd-ae55-bef45c14ffca',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'PDFUpload.tsx:65',message:'Upload successful',data:{status:response.status,paper1_id:response.data.paper1_id,paper2_id:response.data.paper2_id},timestamp:Date.now(),sessionId:'debug-session',runId:'upload',hypothesisId:'F'})}).catch(()=>{});
      // #endregion

      setSuccess('PDF(s) uploaded and processed successfully!')
      onUploadSuccess(response.data)
    } catch (err: any) {
      console.error('Upload error:', err)
      // #region agent log
      fetch('http://127.0.0.1:7242/ingest/aef6e04e-f389-4efd-ae55-bef45c14ffca',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'PDFUpload.tsx:72',message:'Upload error caught',data:{has_response:!!err.response,has_request:!!err.request,error_message:err.message,response_status:err.response?.status,response_data:err.response?.data},timestamp:Date.now(),sessionId:'debug-session',runId:'upload',hypothesisId:'F'})}).catch(()=>{});
      // #endregion
      let errorMessage = 'Failed to upload PDF'
      
      if (err.response) {
        // Server responded with error
        errorMessage = err.response.data?.detail || err.response.data?.error || err.response.statusText || 'Server error'
      } else if (err.request) {
        // Request made but no response
        errorMessage = 'Network error: Could not connect to backend. Please ensure the backend is running on ' + API_URL
      } else {
        // Something else happened
        errorMessage = err.message || 'Unknown error occurred'
      }
      
      setError(errorMessage)
    } finally {
      setUploading(false)
    }
  }

  return (
    <div>
      <h2 style={{ fontSize: '1.75rem', marginBottom: '2rem', color: '#2F3E34', fontWeight: '600' }}>
        Upload Research Paper(s)
      </h2>

      <div style={{ marginBottom: '2rem' }}>
        <label style={{ display: 'block', marginBottom: '0.75rem', fontWeight: '600', color: '#2F3E34', fontSize: '1rem' }}>
          Mode:
        </label>
        <div style={{ display: 'flex', gap: '1.5rem', flexWrap: 'wrap' }}>
          <label style={{ display: 'flex', alignItems: 'center', cursor: 'pointer', padding: '0.75rem 1rem', borderRadius: '8px', transition: 'all 0.2s ease', border: mode === 'single' ? '2px solid #A8D5BA' : '2px solid #E5E7E6', background: mode === 'single' ? '#F0F9F3' : '#FFFFFF' }}>
            <input
              type="radio"
              name="mode"
              value="single"
              checked={mode === 'single'}
              onChange={(e) => setMode(e.target.value as 'single' | 'comparison')}
              style={{ marginRight: '0.75rem', accentColor: '#A8D5BA' }}
            />
            <span style={{ color: '#2F3E34', fontWeight: '500' }}>Single Paper</span>
          </label>
          <label style={{ display: 'flex', alignItems: 'center', cursor: 'pointer', padding: '0.75rem 1rem', borderRadius: '8px', transition: 'all 0.2s ease', border: mode === 'comparison' ? '2px solid #A8D5BA' : '2px solid #E5E7E6', background: mode === 'comparison' ? '#F0F9F3' : '#FFFFFF' }}>
            <input
              type="radio"
              name="mode"
              value="comparison"
              checked={mode === 'comparison'}
              onChange={(e) => setMode(e.target.value as 'single' | 'comparison')}
              style={{ marginRight: '0.75rem', accentColor: '#A8D5BA' }}
            />
            <span style={{ color: '#2F3E34', fontWeight: '500' }}>Comparison (Two Papers)</span>
          </label>
        </div>
      </div>

      <div style={{ marginBottom: '2rem' }}>
        <label style={{ display: 'block', marginBottom: '0.75rem', fontWeight: '600', color: '#2F3E34', fontSize: '1rem' }}>
          Paper 1 (Required):
        </label>
        <label className={`file-label ${paper1 ? 'has-file' : ''}`} style={{ display: 'block', width: '100%' }}>
          <input
            type="file"
            accept=".pdf"
            onChange={handlePaper1Change}
            className="file-input"
          />
          {paper1 ? (
            <span style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.5rem' }}>
              <span>📄</span>
              <span>{paper1.name}</span>
              <span style={{ fontSize: '0.85rem', color: '#666', marginLeft: '0.5rem' }}>
                ({(paper1.size / 1024 / 1024).toFixed(2)} MB)
              </span>
            </span>
          ) : (
            <span style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '0.5rem' }}>
              <span style={{ fontSize: '1.5rem' }}>📎</span>
              <span>Click to choose PDF file or drag and drop</span>
            </span>
          )}
        </label>
      </div>

      {mode === 'comparison' && (
        <div style={{ marginBottom: '2rem' }}>
          <label style={{ display: 'block', marginBottom: '0.75rem', fontWeight: '600', color: '#2F3E34', fontSize: '1rem' }}>
            Paper 2 (Required for comparison):
          </label>
          <label className={`file-label ${paper2 ? 'has-file' : ''}`} style={{ display: 'block', width: '100%' }}>
            <input
              type="file"
              accept=".pdf"
              onChange={handlePaper2Change}
              className="file-input"
            />
            {paper2 ? (
              <span style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.5rem' }}>
                <span>📄</span>
                <span>{paper2.name}</span>
                <span style={{ fontSize: '0.85rem', color: '#666', marginLeft: '0.5rem' }}>
                  ({(paper2.size / 1024 / 1024).toFixed(2)} MB)
                </span>
              </span>
            ) : (
              <span style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '0.5rem' }}>
                <span style={{ fontSize: '1.5rem' }}>📎</span>
                <span>Click to choose PDF file or drag and drop</span>
              </span>
            )}
          </label>
        </div>
      )}

      {error && <div className="error">{error}</div>}
      {success && <div className="success">{success}</div>}

      <button
        onClick={handleUpload}
        disabled={uploading || !paper1 || (mode === 'comparison' && !paper2)}
        className="button"
        style={{ width: '100%', marginTop: '1.5rem', padding: '1rem' }}
      >
        {uploading ? (
          <span style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.75rem' }}>
            <span className="loading"></span>
            <span>Processing PDF(s)...</span>
          </span>
        ) : (
          'Upload and Process'
        )}
      </button>

      <p style={{ marginTop: '1.25rem', fontSize: '0.9rem', color: '#666666', textAlign: 'center', lineHeight: '1.5' }}>
        Note: Large PDFs may take a few minutes to process. Please wait...
      </p>
    </div>
  )
}

