import { useState } from 'react'
import UploadStep from './components/UploadStep'
import QuestionsStep from './components/QuestionsStep'
import ReportStep from './components/ReportStep'

function App() {
  const [currentStep, setCurrentStep] = useState(1)
  const [runData, setRunData] = useState(null)
  const [evaluation, setEvaluation] = useState(null)
  const [detectionResult, setDetectionResult] = useState(null)  // MVP1.1

  const handleUploadComplete = (data) => {
    setRunData(data)
    setDetectionResult(data.detection_result)  // MVP1.1: Store detection result
    if (data.preguntas && data.preguntas.length > 0) {
      setCurrentStep(2)
    } else {
      // No questions, go directly to report
      setEvaluation(data.preliminary_evaluation)
      setCurrentStep(3)
    }
  }

  const handleQuestionsComplete = (evalData) => {
    setEvaluation(evalData)
    setCurrentStep(3)
  }

  const handleReset = () => {
    setCurrentStep(1)
    setRunData(null)
    setEvaluation(null)
    setDetectionResult(null)  // MVP1.1
  }

  return (
    <div className="container">
      <div className="header">
        <h1>🦏 Rhino AI</h1>
        <p>Pre-check de Entregables con Evaluación Inteligente</p>
      </div>

      <div className="stepper">
        <div className={`step ${currentStep >= 1 ? 'active' : ''} ${currentStep > 1 ? 'completed' : ''}`}>
          <div className="step-number">1</div>
          <div>Upload</div>
        </div>
        <div className={`step ${currentStep >= 2 ? 'active' : ''} ${currentStep > 2 ? 'completed' : ''}`}>
          <div className="step-number">2</div>
          <div>Preguntas</div>
        </div>
        <div className={`step ${currentStep >= 3 ? 'active' : ''}`}>
          <div className="step-number">3</div>
          <div>Reporte</div>
        </div>
      </div>

      {currentStep === 1 && (
        <UploadStep onComplete={handleUploadComplete} />
      )}

      {currentStep === 2 && runData && (
        <QuestionsStep 
          runId={runData.run_id}
          questions={runData.preguntas}
          onComplete={handleQuestionsComplete}
        />
      )}

      {currentStep === 3 && evaluation && runData && (
        <ReportStep 
          runId={runData.run_id}
          filename={runData.filename}
          docType={runData.doc_type}
          evaluation={evaluation}
          detectionResult={detectionResult}
          onReset={handleReset}
        />
      )}
    </div>
  )
}

export default App
