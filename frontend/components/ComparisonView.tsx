'use client'

import { useState } from 'react'
import axios from 'axios'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

interface ComparisonViewProps {
  paper1Id: string
  paper2Id: string
}

interface ComparisonData {
  comparison: {
    [key: string]: {
      paper1: string
      paper2: string
      differences: string
      raw_text: string
    }
  }
  paper1_name: string
  paper2_name: string
}

export default function ComparisonView({ paper1Id, paper2Id }: ComparisonViewProps) {
  const [comparison, setComparison] = useState<ComparisonData | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const aspects = ['methodology', 'dataset', 'results', 'limitations']

  const handleCompare = async () => {
    setLoading(true)
    setError(null)

    try {
      const response = await axios.post(
        `${API_URL}/api/compare`,
        {
          paper1_id: paper1Id,
          paper2_id: paper2Id,
          aspects,
        },
        { timeout: 180000 }
      )
      setComparison(response.data)
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    /* HARD CONTAINER */
    <div
      style={{
        maxWidth: '1000px',
        margin: '0 auto',
        padding: '0 1rem',
        overflowX: 'hidden',
      }}
    >
      <button
        onClick={handleCompare}
        disabled={loading}
        style={{
          width: '100%',
          padding: '1rem',
          marginBottom: '2rem',
          background: '#B7E4C7',
          color: '#1B4332',
          fontWeight: 600,
          borderRadius: '8px',
        }}
      >
        {loading ? 'Generating Comparison…' : 'Generate Comparison'}
      </button>

      {error && <div className="error">{error}</div>}

      {comparison && (
        <>
          <h3
            style={{
              textAlign: 'center',
              marginBottom: '2rem',
              color: '#1B4332',
              fontSize: '1.5rem',
              fontWeight: 600,
            }}
          >
            {comparison.paper1_name} vs {comparison.paper2_name}
          </h3>

          {aspects.map((aspect) => {
            const data = comparison.comparison[aspect]
            if (!data) return null

            return (
              <div
                key={aspect}
                style={{
                  background: '#ffffff',
                  borderRadius: '12px',
                  padding: '1.5rem',
                  marginBottom: '2rem',
                  overflow: 'hidden', // 🔑 critical
                }}
              >
                <h4
                  style={{
                    marginBottom: '1rem',
                    color: '#1B4332',
                    borderBottom: '2px solid #B7E4C7',
                    paddingBottom: '0.5rem',
                    textTransform: 'capitalize',
                  }}
                >
                  {aspect}
                </h4>

                {/* GRID — CONSTRAINED */}
                <div
                  style={{
                    display: 'grid',
                    gridTemplateColumns: '1fr 1fr',
                    gap: '1rem',
                    width: '100%',
                  }}
                >
                  {/* Paper 1 */}
                  <div style={{ minWidth: 0 }}>
                    <strong>{comparison.paper1_name}</strong>
                    <div
                      style={{
                        marginTop: '0.5rem',
                        padding: '1rem',
                        background: '#F4F6F5',
                        borderRadius: '8px',
                        maxHeight: '240px',
                        overflowY: 'auto',
                        whiteSpace: 'pre-wrap',
                        wordBreak: 'break-word',
                        borderLeft: '4px solid #95D5B2',
                      }}
                    >
                      {data.paper1 || 'Not mentioned in this paper.'}
                    </div>
                  </div>

                  {/* Paper 2 */}
                  <div style={{ minWidth: 0 }}>
                    <strong>{comparison.paper2_name}</strong>
                    <div
                      style={{
                        marginTop: '0.5rem',
                        padding: '1rem',
                        background: '#F4F6F5',
                        borderRadius: '8px',
                        maxHeight: '240px',
                        overflowY: 'auto',
                        whiteSpace: 'pre-wrap',
                        wordBreak: 'break-word',
                        borderLeft: '4px solid #95D5B2',
                      }}
                    >
                      {data.paper2 || 'Not mentioned in this paper.'}
                    </div>
                  </div>
                </div>

                {/* Differences */}
                {data.differences && (
                  <div style={{ marginTop: '1.5rem' }}>
                    <strong>Key Differences</strong>
                    <div
                      style={{
                        marginTop: '0.5rem',
                        padding: '1rem',
                        background: '#ECFDF3',
                        borderRadius: '8px',
                        borderLeft: '4px solid #74C69D',
                        whiteSpace: 'pre-wrap',
                        wordBreak: 'break-word',
                      }}
                    >
                      {data.differences}
                    </div>
                  </div>
                )}
              </div>
            )
          })}
        </>
      )}
    </div>
  )
}
