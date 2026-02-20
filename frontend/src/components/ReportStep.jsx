import { exportJSON, exportMarkdown } from '../services/api'

function ReportStep({ runId, filename, docType, evaluation, onReset, detectionResult }) {
  const getDecisionColor = (decision) => {
    const colors = {
      APROBADO: '#48bb78',
      REQUIERE_CORRECCION: '#ed8936',
      RECHAZADO: '#f56565'
    }
    return colors[decision] || '#cbd5e0'
  }

  const getSeverityIcon = (severity) => {
    const icons = {
      bloqueante: '🔴',
      mayor: '🟠',
      menor: '🟡',
      sugerencia: '🔵'
    }
    return icons[severity] || '⚪'
  }

  const handleExportJSON = () => {
    window.open(exportJSON(runId), '_blank')
  }

  const handleExportMarkdown = () => {
    window.open(exportMarkdown(runId), '_blank')
  }

  return (
    <div>
      {/* Score Display */}
      <div className="score-display">
        <h2>Resultado de Evaluación</h2>
        <div style={{ fontSize: '1.2rem', opacity: 0.9, marginTop: '10px' }}>
          {filename} • {docType}
          {detectionResult && (
            <span style={{ fontSize: '0.9rem', marginLeft: '10px' }}>
              (Confianza: {(detectionResult.confianza * 100).toFixed(0)}%)
            </span>
          )}
        </div>
        
        <div className="score-number">
          {evaluation.score?.toFixed(1) || 0}
          <span style={{ fontSize: '2rem' }}>/100</span>
        </div>

        <div 
          className="decision"
          style={{ background: getDecisionColor(evaluation.decision) }}
        >
          {evaluation.decision}
        </div>

        {/* Score Potencial */}
        {evaluation.score_potencial && (
          <div className="score-potential">
            <div className="score-potential-item">
              <h4>Actual</h4>
              <div className="value">{evaluation.score_potencial.actual}</div>
            </div>
            <div className="score-potential-item">
              <h4>Si corrige P0</h4>
              <div className="value">{evaluation.score_potencial.si_corrige_p0}</div>
            </div>
            <div className="score-potential-item">
              <h4>Si corrige P0+P1</h4>
              <div className="value">{evaluation.score_potencial.si_corrige_p0_p1}</div>
            </div>
            <div className="score-potential-item">
              <h4>Si corrige todo</h4>
              <div className="value">{evaluation.score_potencial.si_corrige_todo}</div>
            </div>
          </div>
        )}
      </div>

      {/* MVP1.1: Detection Result */}
      {detectionResult && (
        <div className="card">
          <h2>🔍 Detección de Tipo de Documento</h2>
          <div style={{ marginTop: '15px' }}>
            <p><strong>Tipo detectado:</strong> {detectionResult.tipo_detectado}</p>
            <p><strong>Confianza:</strong> {(detectionResult.confianza * 100).toFixed(0)}%</p>
            <p><strong>Razón:</strong> {detectionResult.razon}</p>
            
            {/* Top 3 Candidates */}
            {detectionResult.top3 && detectionResult.top3.length > 0 && (
              <div style={{ marginTop: '20px' }}>
                <h3 style={{ fontSize: '1.1rem', marginBottom: '10px' }}>Top 3 Candidatos</h3>
                {detectionResult.top3.map((candidate, idx) => (
                  <div key={idx} style={{
                    padding: '10px',
                    marginBottom: '10px',
                    background: idx === 0 ? '#e6fffa' : '#f7fafc',
                    borderLeft: `4px solid ${idx === 0 ? '#38b2ac' : '#cbd5e0'}`,
                    borderRadius: '4px'
                  }}>
                    <div style={{ fontWeight: 'bold' }}>
                      {idx + 1}. {candidate.type} - Score: {candidate.score}
                    </div>
                    <div style={{ fontSize: '0.9rem', color: '#666', marginTop: '5px' }}>
                      {candidate.why}
                    </div>
                  </div>
                ))}
              </div>
            )}
            
            {/* Conflict Name vs Content */}
            {detectionResult.conflict_name_vs_content && (
              <div style={{
                marginTop: '20px',
                padding: '15px',
                background: '#fffaf0',
                border: '2px solid #ed8936',
                borderRadius: '6px'
              }}>
                <h3 style={{ color: '#c05621', marginBottom: '10px' }}>
                  ⚠️ Conflicto: Nombre vs Contenido
                </h3>
                <p>
                  El nombre del archivo sugiere <strong>{detectionResult.filename_suggested_type}</strong>,
                  pero el contenido indica <strong>{detectionResult.tipo_detectado}</strong>.
                </p>
                <p style={{ marginTop: '10px', fontSize: '0.9rem' }}>
                  <strong>Recomendación:</strong> Verificar el nombre del archivo y actualizar
                  el control documental para evitar confusiones.
                </p>
              </div>
            )}
            
            {/* UNKNOWN Questions */}
            {detectionResult.tipo_detectado === 'UNKNOWN' && detectionResult.questions_to_classify && (
              <div style={{
                marginTop: '20px',
                padding: '15px',
                background: '#ebf8ff',
                border: '2px solid #4299e1',
                borderRadius: '6px'
              }}>
                <h3 style={{ color: '#2c5282', marginBottom: '10px' }}>
                  ❓ Preguntas para Clasificar
                </h3>
                <p style={{ marginBottom: '10px' }}>
                  No se pudo determinar el tipo de documento con confianza. 
                  Responde estas preguntas para ayudar a clasificarlo:
                </p>
                <ul style={{ paddingLeft: '20px' }}>
                  {detectionResult.questions_to_classify.map((q, idx) => (
                    <li key={idx} style={{ marginBottom: '8px' }}>{q}</li>
                  ))}
                </ul>
              </div>
            )}
            
            {/* Secondary Signals */}
            {detectionResult.secondary_signals && detectionResult.secondary_signals.length > 0 && (
              <div style={{ marginTop: '15px' }}>
                <p style={{ fontSize: '0.9rem', color: '#666' }}>
                  <strong>Señales secundarias:</strong> {detectionResult.secondary_signals.join(', ')}
                </p>
              </div>
            )}
          </div>
        </div>
      )}
              <div style={{ marginTop: '20px' }}>
                <h3 style={{ fontSize: '1.1rem', marginBottom: '10px' }}>Top 3 Candidatos:</h3>
                {detectionResult.top3.map((candidate, idx) => (
                  <div key={idx} style={{ 
                    padding: '10px', 
                    background: idx === 0 ? '#f0fff4' : '#f7fafc',
                    borderLeft: `4px solid ${idx === 0 ? '#48bb78' : '#cbd5e0'}`,
                    marginBottom: '10px',
                    borderRadius: '4px'
                  }}>
                    <div style={{ fontWeight: 'bold' }}>
                      {idx + 1}. {candidate.type} - Score: {candidate.score}
                    </div>
                    <div style={{ fontSize: '0.9rem', color: '#666', marginTop: '5px' }}>
                      {candidate.why}
                    </div>
                  </div>
                ))}
              </div>
            )}

            {/* Conflict Warning */}
            {detectionResult.conflict_name_vs_content && (
              <div style={{ 
                marginTop: '20px', 
                padding: '15px', 
                background: '#fffaf0',
                border: '2px solid #ed8936',
                borderRadius: '6px'
              }}>
                <h3 style={{ color: '#c05621', marginBottom: '10px' }}>
                  ⚠️ Conflicto: Nombre vs Contenido
                </h3>
                <p>
                  El nombre del archivo sugiere <strong>{detectionResult.filename_suggested_type}</strong>, 
                  pero el contenido indica <strong>{detectionResult.tipo_detectado}</strong>.
                </p>
                <p style={{ marginTop: '10px', fontSize: '0.9rem' }}>
                  <strong>Recomendación:</strong> Verificar el nombre del archivo y actualizar 
                  el control documental si es necesario.
                </p>
              </div>
            )}

            {/* UNKNOWN Questions */}
            {detectionResult.tipo_detectado === 'UNKNOWN' && detectionResult.questions_to_classify && (
              <div style={{ 
                marginTop: '20px', 
                padding: '15px', 
                background: '#ebf8ff',
                borderRadius: '6px'
              }}>
                <h3 style={{ marginBottom: '10px' }}>❓ Preguntas para Clasificar</h3>
                <p style={{ marginBottom: '10px' }}>
                  No se pudo determinar el tipo de documento. Responde estas preguntas:
                </p>
                <ul style={{ paddingLeft: '20px' }}>
                  {detectionResult.questions_to_classify.map((q, idx) => (
                    <li key={idx} style={{ marginBottom: '8px' }}>{q}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Fail-Fast */}
      {evaluation.fail_fast && evaluation.fail_fast.some(ff => ff.active) && (
        <div className="card" style={{ borderLeft: '4px solid #f56565' }}>
          <h2>⛔ Fail-Fast Activado</h2>
          {evaluation.fail_fast.filter(ff => ff.active).map(ff => (
            <div key={ff.code} style={{ 
              marginTop: '15px', 
              padding: '15px', 
              background: '#fff5f5',
              borderRadius: '6px'
            }}>
              <h3 style={{ color: '#c53030', marginBottom: '10px' }}>
                {ff.code}: {ff.name}
              </h3>
              <p><strong>Evidencia:</strong> {ff.evidencia}</p>
              <p style={{ marginTop: '10px' }}>{ff.explicacion}</p>
            </div>
          ))}
        </div>
      )}

      {/* Hallazgos */}
      <div className="card">
        <h2>Hallazgos ({evaluation.hallazgos?.length || 0})</h2>
        <p style={{ marginBottom: '20px', color: '#666' }}>
          Ordenados por severidad y prioridad
        </p>

        {evaluation.hallazgos && evaluation.hallazgos.length > 0 ? (
          evaluation.hallazgos.map(h => (
            <div key={h.id} className={`finding-card ${h.severidad}`}>
              <div style={{ display: 'flex', alignItems: 'center', marginBottom: '15px' }}>
                <span style={{ fontSize: '1.5rem', marginRight: '10px' }}>
                  {getSeverityIcon(h.severidad)}
                </span>
                <div>
                  <div style={{ fontWeight: 'bold', fontSize: '1.1rem' }}>
                    [{h.prioridad}] {h.titulo}
                  </div>
                  <div style={{ fontSize: '0.85rem', color: '#666', marginTop: '5px' }}>
                    Severidad: {h.severidad} • Impacto: +{h.impacto_estimado.toFixed(1)} puntos
                  </div>
                </div>
              </div>

              <div style={{ marginBottom: '15px' }}>
                <strong>Evidencia:</strong>
                <div style={{ 
                  marginTop: '5px', 
                  padding: '10px', 
                  background: 'rgba(0,0,0,0.05)',
                  borderRadius: '4px',
                  fontSize: '0.9rem'
                }}>
                  {h.evidencia_detalle}
                </div>
              </div>

              <div style={{ marginBottom: '15px' }}>
                <strong>Recomendación:</strong>
                <p style={{ marginTop: '5px' }}>{h.recomendacion}</p>
              </div>

              <div style={{ marginBottom: '15px' }}>
                <strong>Qué agregar:</strong>
                <p style={{ marginTop: '5px' }}>{h.que_agregar}</p>
              </div>

              <div style={{ marginBottom: '15px' }}>
                <strong>Dónde insertar:</strong>
                <p style={{ marginTop: '5px' }}>{h.donde_insertar}</p>
              </div>

              <div>
                <strong>Ejemplo de texto:</strong>
                <pre style={{ 
                  marginTop: '5px', 
                  padding: '10px', 
                  background: 'rgba(0,0,0,0.05)',
                  borderRadius: '4px',
                  fontSize: '0.85rem',
                  whiteSpace: 'pre-wrap',
                  overflow: 'auto'
                }}>
                  {h.ejemplo_texto}
                </pre>
              </div>
            </div>
          ))
        ) : (
          <div style={{ textAlign: 'center', padding: '40px', color: '#666' }}>
            ✅ No se encontraron hallazgos
          </div>
        )}
      </div>

      {/* Export Buttons */}
      <div className="card">
        <h2>Exportar Reporte</h2>
        <div className="export-buttons">
          <button className="btn btn-primary" onClick={handleExportJSON}>
            📄 Descargar JSON
          </button>
          <button className="btn btn-primary" onClick={handleExportMarkdown}>
            📝 Descargar Markdown
          </button>
        </div>
      </div>

      {/* Reset */}
      <div style={{ textAlign: 'center', marginTop: '30px' }}>
        <button className="btn btn-secondary" onClick={onReset}>
          ← Analizar Otro Documento
        </button>
      </div>
    </div>
  )
}

export default ReportStep
