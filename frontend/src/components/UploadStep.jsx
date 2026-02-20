import { useState } from 'react'
import { uploadDocument } from '../services/api'

function UploadStep({ onComplete }) {
  const [file, setFile] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [dragging, setDragging] = useState(false)

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0]
    if (selectedFile && selectedFile.name.endsWith('.docx')) {
      setFile(selectedFile)
      setError(null)
    } else {
      setError('Por favor selecciona un archivo DOCX válido')
    }
  }

  const handleDrop = (e) => {
    e.preventDefault()
    setDragging(false)
    
    const droppedFile = e.dataTransfer.files[0]
    if (droppedFile && droppedFile.name.endsWith('.docx')) {
      setFile(droppedFile)
      setError(null)
    } else {
      setError('Por favor selecciona un archivo DOCX válido')
    }
  }

  const handleDragOver = (e) => {
    e.preventDefault()
    setDragging(true)
  }

  const handleDragLeave = () => {
    setDragging(false)
  }

  const handleUpload = async () => {
    if (!file) return

    setLoading(true)
    setError(null)

    try {
      const data = await uploadDocument(file)
      onComplete(data)
    } catch (err) {
      setError(err.response?.data?.detail || 'Error al procesar el documento')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="card">
      <h2>Subir Documento</h2>
      <p style={{ marginBottom: '20px', color: '#666' }}>
        Sube un archivo DOCX para iniciar el análisis
      </p>

      <div
        className={`upload-zone ${dragging ? 'dragging' : ''}`}
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onClick={() => document.getElementById('file-input').click()}
      >
        <input
          id="file-input"
          type="file"
          accept=".docx"
          onChange={handleFileChange}
          style={{ display: 'none' }}
        />
        
        {file ? (
          <div>
            <div style={{ fontSize: '3rem', marginBottom: '10px' }}>📄</div>
            <div style={{ fontSize: '1.2rem', fontWeight: 'bold' }}>{file.name}</div>
            <div style={{ color: '#666', marginTop: '5px' }}>
              {(file.size / 1024 / 1024).toFixed(2)} MB
            </div>
          </div>
        ) : (
          <div>
            <div style={{ fontSize: '3rem', marginBottom: '10px' }}>📁</div>
            <div style={{ fontSize: '1.2rem', marginBottom: '10px' }}>
              Arrastra un archivo DOCX aquí
            </div>
            <div style={{ color: '#666' }}>o haz clic para seleccionar</div>
          </div>
        )}
      </div>

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

      <div style={{ marginTop: '30px', textAlign: 'center' }}>
        <button
          className="btn btn-primary"
          onClick={handleUpload}
          disabled={!file || loading}
          style={{ minWidth: '200px' }}
        >
          {loading ? 'Procesando...' : 'Analizar Documento'}
        </button>
      </div>

      {loading && (
        <div className="loading">
          <div className="spinner"></div>
          <p>Extrayendo estructura y clasificando documento...</p>
        </div>
      )}
    </div>
  )
}

export default UploadStep
