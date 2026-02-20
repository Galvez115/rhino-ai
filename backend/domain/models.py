"""Domain models"""
from datetime import datetime
from typing import List, Dict, Any, Optional, Literal
from pydantic import BaseModel, Field


# Enums
DocumentType = Literal["DTM", "DSP", "DTC", "DoD", "PLAN_PRUEBAS_EVIDENCIA", 
                       "RUNBOOK_MANUAL_OPERACION", "SOPORTE_EVOLUTIVO_RCA", "UNKNOWN"]
Decision = Literal["APROBADO", "REQUIERE_CORRECCION", "RECHAZADO"]
CriterioEstado = Literal["CUMPLE", "PARCIAL", "NO", "NA"]
Severidad = Literal["bloqueante", "mayor", "menor", "sugerencia"]
Evidencia = Literal["found", "missing", "inconsistent"]
Prioridad = Literal["P0", "P1", "P2", "P3"]


# Document Structure
class DocumentSection(BaseModel):
    title: str
    level: int
    content: str
    location: str  # "Section 2.1"


class DocumentOutline(BaseModel):
    filename: str
    word_count: int
    sections: List[DocumentSection]
    tables_count: int
    has_toc: bool
    metadata: Dict[str, Any] = {}


# Evaluation Models
class CriterioEvaluacion(BaseModel):
    criterio_id: str
    nombre: str
    peso: int
    estado: CriterioEstado
    puntos_obtenidos: float
    evidencia: List[Dict[str, str]] = []  # [{"location": "...", "snippet": "..."}]
    justificacion: str
    severidad_si_falta: Severidad


class FailFast(BaseModel):
    code: str
    name: str
    active: bool
    evidencia: str
    explicacion: str


class Hallazgo(BaseModel):
    id: str
    criterio_id: str
    severidad: Severidad
    prioridad: Prioridad
    titulo: str
    evidencia_tipo: Evidencia
    evidencia_detalle: str  # location + snippet o "No se encontró"
    recomendacion: str
    que_agregar: str
    donde_insertar: str
    ejemplo_texto: str
    impacto_estimado: float  # puntos que sumaría


class Pregunta(BaseModel):
    id: str
    pregunta: str
    prioridad: Prioridad
    categoria: str
    por_que_importa: str
    si_no_responde: str
    criterio_relacionado: str


class ScorePotencial(BaseModel):
    actual: float
    si_corrige_p0: float
    si_corrige_p0_p1: float
    si_corrige_todo: float


class EvaluationResult(BaseModel):
    run_id: str
    doc_type: DocumentType
    doc_type_confidence: float
    score: float
    decision: Decision
    fail_fast: List[FailFast]
    criterios: List[CriterioEvaluacion]
    hallazgos: List[Hallazgo]
    preguntas: List[Pregunta]
    score_potencial: ScorePotencial
    penalizaciones_aplicadas: List[Dict[str, Any]] = []
    peso_total_aplicable: float
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# Q&A
class Answer(BaseModel):
    question_id: str
    answer: str


class AnswersSubmission(BaseModel):
    answers: List[Answer]


# Export
class ReportExport(BaseModel):
    run_id: str
    filename: str
    doc_type: DocumentType
    decision: Decision
    score: float
    score_potencial: ScorePotencial
    fail_fast: List[FailFast]
    hallazgos: List[Hallazgo]
    criterios: List[CriterioEvaluacion]
    generated_at: datetime
