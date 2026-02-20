"""Document evaluator with rubrica"""
import json
import logging
import uuid
from typing import List, Dict, Any, Tuple
from datetime import datetime

from domain.models import (
    DocumentOutline, DocumentType, EvaluationResult, CriterioEvaluacion,
    FailFast, Hallazgo, Pregunta, ScorePotencial, CriterioEstado, Decision
)
from utils.docx_parser import search_in_document
from adapters.llm_factory import get_llm

logger = logging.getLogger(__name__)

# Load rubrica
with open("config/rubrica_government.json", "r", encoding="utf-8") as f:
    RUBRICA = json.load(f)


class DocumentEvaluator:
    def __init__(self, outline: DocumentOutline, doc_type: DocumentType, run_id: str, detection_result: Dict = None):
        self.outline = outline
        self.doc_type = doc_type
        self.run_id = run_id
        self.detection_result = detection_result  # MVP1.1
        self.llm = get_llm()
        self.criterios_config = RUBRICA["tipos_documentos_entregables"][doc_type]["criterios"]
    
    async def evaluate(self, user_answers: Dict[str, str] = None) -> EvaluationResult:
        """Main evaluation flow"""
        logger.info(f"Starting evaluation", extra={"run_id": self.run_id, "doc_type": self.doc_type})
        
        # 1. Check fail-fast conditions
        fail_fast_results = self.check_fail_fast()
        
        # 2. Evaluate each criterio
        criterios_eval = await self.evaluate_criterios(user_answers or {})
        
        # 3. Calculate score
        score, peso_aplicable = self.calculate_score(criterios_eval)
        
        # 4. Apply penalties
        score, penalties = self.apply_penalties(score, criterios_eval)
        
        # 5. Generate findings
        hallazgos = self.generate_findings(criterios_eval)
        
        # 6. Generate questions (only for gaps P0/P1/P2)
        preguntas = self.generate_questions(criterios_eval, hallazgos)
        
        # 7. Calculate potential scores
        score_potencial = self.calculate_potential_scores(score, hallazgos)
        
        # 8. Make decision
        decision = self.make_decision(score, fail_fast_results, hallazgos)
        
        return EvaluationResult(
            run_id=self.run_id,
            doc_type=self.doc_type,
            doc_type_confidence=1.0,  # Set by caller
            score=score,
            decision=decision,
            fail_fast=fail_fast_results,
            criterios=criterios_eval,
            hallazgos=sorted(hallazgos, key=lambda h: (
                {"bloqueante": 0, "mayor": 1, "menor": 2, "sugerencia": 3}[h.severidad],
                h.prioridad
            )),
            preguntas=preguntas,
            score_potencial=score_potencial,
            penalizaciones_aplicadas=penalties,
            peso_total_aplicable=peso_aplicable
        )
    
    def check_fail_fast(self) -> List[FailFast]:
        """Check fail-fast conditions"""
        results = []
        
        # FF-01: Empty or unreadable
        if self.outline.word_count < 100:
            results.append(FailFast(
                code="FF-01",
                name="Documento vacío o ilegible",
                active=True,
                evidencia=f"Word count: {self.outline.word_count}",
                explicacion="El documento no contiene contenido suficiente"
            ))
        
        # FF-02: Unknown type (checked by caller)
        
        # FF-03 and FF-04 will be checked during evaluation
        
        return results
    
    async def evaluate_criterios(self, user_answers: Dict[str, str]) -> List[CriterioEvaluacion]:
        """Evaluate all criterios"""
        results = []
        
        for criterio_config in self.criterios_config:
            eval_result = await self.evaluate_single_criterio(criterio_config, user_answers)
            results.append(eval_result)
        
        return results
    
    async def evaluate_single_criterio(self, criterio_config: Dict, 
                                      user_answers: Dict[str, str]) -> CriterioEvaluacion:
        """Evaluate single criterio with LLM"""
        criterio_id = criterio_config["id"]
        
        # Search for evidence in document
        evidencia_requerida = criterio_config.get("evidencia_requerida", [])
        evidencia_found = search_in_document(self.outline, evidencia_requerida)
        
        # Check user answers
        answer_key = f"answer_{criterio_id}"
        user_evidence = user_answers.get(answer_key, "")
        
        # Prepare LLM prompt
        prompt = self._build_criterio_prompt(criterio_config, evidencia_found, user_evidence)
        
        try:
            response = await self.llm.generate_json(prompt)
            
            estado = response.get("estado", "NO")
            justificacion = response.get("justificacion", "")
            
            # Calculate points
            peso = criterio_config["peso"]
            if estado == "CUMPLE":
                puntos = peso
            elif estado == "PARCIAL":
                puntos = peso * 0.5
            elif estado == "NA":
                puntos = 0  # NA excludes from denominator
            else:  # NO
                puntos = 0
            
            return CriterioEvaluacion(
                criterio_id=criterio_id,
                nombre=criterio_config["nombre"],
                peso=peso,
                estado=estado,
                puntos_obtenidos=puntos,
                evidencia=evidencia_found if evidencia_found else [],
                justificacion=justificacion,
                severidad_si_falta=criterio_config.get("severidad_si_falta", "menor")
            )
            
        except Exception as e:
            logger.error(f"Error evaluating criterio {criterio_id}: {e}", 
                        extra={"run_id": self.run_id})
            # Default to NO on error
            return CriterioEvaluacion(
                criterio_id=criterio_id,
                nombre=criterio_config["nombre"],
                peso=criterio_config["peso"],
                estado="NO",
                puntos_obtenidos=0,
                evidencia=[],
                justificacion=f"Error en evaluación: {str(e)}",
                severidad_si_falta=criterio_config.get("severidad_si_falta", "menor")
            )
    
    def _build_criterio_prompt(self, criterio_config: Dict, 
                              evidencia_found: List[Dict], user_evidence: str) -> str:
        """Build prompt for criterio evaluation"""
        sections_text = "\n\n".join([
            f"[{s.location}] {s.title}\n{s.content[:500]}"
            for s in self.outline.sections[:10]
        ])
        
        evidencia_text = "\n".join([
            f"- {e['location']}: {e['snippet']}"
            for e in evidencia_found
        ]) if evidencia_found else "No se encontró evidencia automática"
        
        user_text = f"\n\nEvidencia aportada por usuario:\n{user_evidence}" if user_evidence else ""
        
        return f"""Evalúa el siguiente criterio del documento:

CRITERIO: {criterio_config['nombre']}
DESCRIPCIÓN: {criterio_config['descripcion']}
EVIDENCIA REQUERIDA: {', '.join(criterio_config.get('evidencia_requerida', []))}

DOCUMENTO (primeras secciones):
{sections_text}

EVIDENCIA ENCONTRADA:
{evidencia_text}{user_text}

REGLAS ANTI-ALUCINACIÓN:
- Solo afirmar que existe si hay evidencia con location + snippet
- Si no hay evidencia, estado = NO
- NA solo si el criterio genuinamente no aplica (con justificación)
- No inferir ni inventar contenido

Responde en JSON:
{{
  "estado": "CUMPLE|PARCIAL|NO|NA",
  "justificacion": "Explicación detallada con referencias a evidencia o 'No se encontró'"
}}"""
    
    def calculate_score(self, criterios: List[CriterioEvaluacion]) -> Tuple[float, float]:
        """Calculate base score (NA excludes denominator)"""
        puntos_total = 0
        peso_aplicable = 0
        
        for c in criterios:
            if c.estado != "NA":
                peso_aplicable += c.peso
                puntos_total += c.puntos_obtenidos
        
        if peso_aplicable == 0:
            return 0.0, 0
        
        score = (puntos_total / peso_aplicable) * 100
        return score, peso_aplicable
    
    def apply_penalties(self, base_score: float, 
                       criterios: List[CriterioEvaluacion]) -> Tuple[float, List[Dict]]:
        """Apply penalties without double punishment"""
        penalties = []
        score = base_score
        
        penalizaciones_config = RUBRICA.get("penalizaciones_tipicas", {})
        
        # Penalty: critical evidence missing
        for c in criterios:
            if c.peso >= 15 and c.estado == "NO":
                # Only apply if not already at 0
                if c.puntos_obtenidos > 0:
                    penalty = penalizaciones_config["falta_evidencia_critica"]["penalizacion"]
                    score += penalty
                    penalties.append({
                        "tipo": "falta_evidencia_critica",
                        "criterio": c.criterio_id,
                        "penalizacion": penalty
                    })
        
        # Ensure score doesn't go below 0
        score = max(0, score)
        
        return score, penalties
    
    def generate_findings(self, criterios: List[CriterioEvaluacion]) -> List[Hallazgo]:
        """Generate findings from criterios"""
        hallazgos = []
        
        for c in criterios:
            if c.estado in ["NO", "PARCIAL"]:
                hallazgo_id = f"H-{c.criterio_id}-{uuid.uuid4().hex[:6]}"
                
                # Determine evidence type
                if not c.evidencia:
                    evidencia_tipo = "missing"
                    evidencia_detalle = "No se encontró evidencia en el documento"
                elif c.estado == "PARCIAL":
                    evidencia_tipo = "inconsistent"
                    evidencia_detalle = f"Evidencia parcial: {c.evidencia[0]['snippet']}"
                else:
                    evidencia_tipo = "found"
                    evidencia_detalle = f"{c.evidencia[0]['location']}: {c.evidencia[0]['snippet']}"
                
                # Generate recommendation
                recomendacion, que_agregar, donde, ejemplo = self._generate_recommendation(c)
                
                # Estimate impact
                impacto = c.peso if c.estado == "NO" else c.peso * 0.5
                
                hallazgos.append(Hallazgo(
                    id=hallazgo_id,
                    criterio_id=c.criterio_id,
                    severidad=c.severidad_si_falta,
                    prioridad=self._severidad_to_priority(c.severidad_si_falta),
                    titulo=c.nombre,
                    evidencia_tipo=evidencia_tipo,
                    evidencia_detalle=evidencia_detalle,
                    recomendacion=recomendacion,
                    que_agregar=que_agregar,
                    donde_insertar=donde,
                    ejemplo_texto=ejemplo,
                    impacto_estimado=impacto
                ))
        
        # MVP1.1: Add finding for filename vs content conflict
        if self.detection_result and self.detection_result.get("conflict_name_vs_content"):
            conflict_hallazgo = Hallazgo(
                id=f"H-CONFLICT-{uuid.uuid4().hex[:6]}",
                criterio_id="CONTROL_DOCUMENTAL",
                severidad="mayor",
                prioridad="P1",
                titulo="Conflicto: Nombre de archivo vs Contenido",
                evidencia_tipo="inconsistent",
                evidencia_detalle=f"Nombre sugiere {self.detection_result.get('filename_suggested_type')} pero contenido indica {self.doc_type}",
                recomendacion="Actualizar el nombre del archivo para que coincida con el tipo de documento real y mejorar el control documental",
                que_agregar=f"Renombrar archivo para incluir '{self.doc_type}' en lugar de '{self.detection_result.get('filename_suggested_type')}'",
                donde_insertar="Nombre del archivo",
                ejemplo_texto=f"Ejemplo: documento_{self.doc_type}_v1.docx",
                impacto_estimado=5.0
            )
            hallazgos.append(conflict_hallazgo)
        
        return hallazgos
    
    def _generate_recommendation(self, criterio: CriterioEvaluacion) -> Tuple[str, str, str, str]:
        """Generate detailed recommendation"""
        # This is simplified - in production, use LLM for better recommendations
        recomendacion = f"Agregar {criterio.nombre} al documento"
        que_agregar = f"Incluir: {', '.join(criterio.evidencia or ['información requerida'])}"
        donde = "En una sección dedicada o al inicio del documento"
        ejemplo = f"Ejemplo:\n\n## {criterio.nombre}\n[Contenido detallado aquí]"
        
        return recomendacion, que_agregar, donde, ejemplo
    
    def _severidad_to_priority(self, severidad: str) -> str:
        """Map severidad to priority"""
        mapping = {
            "bloqueante": "P0",
            "mayor": "P1",
            "menor": "P2",
            "sugerencia": "P3"
        }
        return mapping.get(severidad, "P2")
    
    def generate_questions(self, criterios: List[CriterioEvaluacion], 
                          hallazgos: List[Hallazgo]) -> List[Pregunta]:
        """Generate intelligent questions for critical gaps"""
        preguntas = []
        
        # Only ask for P0/P1/P2 gaps
        critical_hallazgos = [h for h in hallazgos if h.prioridad in ["P0", "P1", "P2"]]
        
        for h in critical_hallazgos[:5]:  # Limit to 5 questions
            pregunta_id = f"Q-{h.criterio_id}"
            
            preguntas.append(Pregunta(
                id=pregunta_id,
                pregunta=f"¿Puede proporcionar información sobre: {h.titulo}?",
                prioridad=h.prioridad,
                categoria=h.criterio_id.split("-")[0],
                por_que_importa=f"Este criterio tiene severidad {h.severidad} y puede impactar el score en {h.impacto_estimado:.1f} puntos",
                si_no_responde=f"El documento será evaluado sin esta información, resultando en {h.evidencia_tipo}",
                criterio_relacionado=h.criterio_id
            ))
        
        return preguntas
    
    def calculate_potential_scores(self, current_score: float, 
                                   hallazgos: List[Hallazgo]) -> ScorePotencial:
        """Calculate potential scores if corrections are made"""
        p0_impact = sum(h.impacto_estimado for h in hallazgos if h.prioridad == "P0")
        p1_impact = sum(h.impacto_estimado for h in hallazgos if h.prioridad == "P1")
        all_impact = sum(h.impacto_estimado for h in hallazgos)
        
        return ScorePotencial(
            actual=round(current_score, 2),
            si_corrige_p0=round(min(current_score + p0_impact, 100), 2),
            si_corrige_p0_p1=round(min(current_score + p0_impact + p1_impact, 100), 2),
            si_corrige_todo=round(min(current_score + all_impact, 100), 2)
        )
    
    def make_decision(self, score: float, fail_fast: List[FailFast], 
                     hallazgos: List[Hallazgo]) -> Decision:
        """Make final decision"""
        # Check fail-fast
        if any(ff.active for ff in fail_fast):
            return "RECHAZADO"
        
        # Check bloqueantes
        bloqueantes = [h for h in hallazgos if h.severidad == "bloqueante"]
        
        # Decision logic
        if score >= 85 and len(bloqueantes) == 0:
            return "APROBADO"
        elif score >= 70:
            return "REQUIERE_CORRECCION"
        else:
            return "RECHAZADO"
