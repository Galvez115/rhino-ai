import { useState } from 'react'
import { submitAnswers } from '../services/api'

function QuestionsStep({ runId, questions, onComplete }) {
  const [answers, setAnswers] = useState({})
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const handleAnswerChange = (questionId, value) => {
    setAnswers(prev => ({
      ...prev,
      [questionId]: value
    }))
  }

  const handleSubmit = async () => {
    setLoading(true)
    setError(null)

    try {
      const answersArray = Object.entries(answers).map(([question_id, answer]) => ({
        question_id,
        answer
      }))

      const evaluation = await submitAnswers(runId, answersArray)
      onComplete(evaluation)
    } catch (err) {
      setError(err.response?.data?.detail || 'Error al enviar respuestas')
    } finally {
      setLoading(false)
    }
  }

  const handleSkip = () => {
    // Submit empty answers
    handleSubmit()
  }

  const getPriorityColor = (priority) => {
    const colors = {
      P0: '#f56565',
      P1: '#ed8936',
      P2: '#ecc94b',
      P3: '#4299e1'
    }
    return colors[priority] || '#cbd5e0'
  }

  return (
    <div className="card">
      <h2>Preguntas sobre el Documento</h2>
      <p style={{ marginBottom: '30px', color: '#666' }}>
        Responde estas preguntas para mejorar la evaluación. Solo preguntamos sobre gaps críticos (P0/P1/P2).
      </p>

      {questions.map((q, index) => (
        <div key={q.id} className={`question-card priority-${q.prioridad}`}>
          <div style={{ display: 'flex', alignItems: 'center', marginBottom: '15px' }}>
            <span style={{
              background: getPriorityColor(q.prioridad),
              color: 'white',
              padding: '4px 12px',
              borderRadius: '12px',
              fontSize: '0.85rem',
              fontWeight: 'bold',
              marginRight: '10px'
            }}>
              {q.prioridad}
            </span>
            <span style={{ color: '#666', fontSize: '0.9rem' }}>{q.categoria}</span>
          </div>

          <h3 style={{ marginBottom: '10px', fontSize: '1.1rem' }}>
            {index + 1}. {q.pregunta}
          </h3>

          <div style={{ 
            background: 'white', 
            padding: '12px', 
            borderRadius: '6px',
            marginBottom: '15px',
            fontSize: '0.9rem'
          }}>
            <strong>Por qué importa:</strong> {q.por_que_importa}
          </div>

          <textarea
            placeholder="Tu respuesta aquí..."
            value={answers[q.id] || ''}
            onChange={(e) => handleAnswerChange(q.id, e.target.value)}
            style={{ marginBottom: '10px' }}
          />

          <div style={{ fontSize: '0.85rem', color: '#666', fontStyle: 'italic' }}>
            Si no respondes: {q.si_no_responde}
          </div>
        </div>
      ))}

      {error && (
        <div style={{ 
          marginTop: '20px', 
          padding: '15px', 
          background: '#fff5f5', 
          color: '#c53030',
          borderRadius: '6px'
        }}>
          {error}
        </div>
      )}

      <div style={{ 
        marginTop: '30px', 
        display: 'flex', 
        gap: '15px', 
        justifyContent: 'center' 
      }}>
        <button
          className="btn btn-secondary"
          onClick={handleSkip}
          disabled={loading}
        >
          Saltar Preguntas
        </button>
        <button
          className="btn btn-primary"
          onClick={handleSubmit}
          disabled={loading}
          style={{ minWidth: '200px' }}
        >
          {loading ? 'Evaluando...' : 'Enviar Respuestas'}
        </button>
      </div>

      {loading && (
        <div className="loading">
          <div className="spinner"></div>
          <p>Re-evaluando documento con tus respuestas...</p>
        </div>
      )}
    </div>
  )
}

export default QuestionsStep
