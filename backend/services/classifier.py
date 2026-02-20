"""Document type classifier - MVP1.1 with deterministic detector"""
import json
import logging
from typing import Tuple
from domain.models import DocumentOutline, DocumentType
from adapters.llm_factory import get_llm
from services.doc_type_detector import detect_document_type

logger = logging.getLogger(__name__)


# Load rubrica
with open("config/rubrica_government.json", "r", encoding="utf-8") as f:
    RUBRICA = json.load(f)


def heuristic_classification(outline: DocumentOutline) -> Tuple[DocumentType, float]:
    """
    Deterministic heuristic classification based on keywords
    Returns: (doc_type, confidence)
    """
    content_lower = " ".join([s.content.lower() for s in outline.sections])
    title_lower = outline.metadata.get("title", "").lower()
    combined = f"{title_lower} {content_lower}"
    
    scores = {}
    
    for doc_type, config in RUBRICA["tipos_documentos_entregables"].items():
        if doc_type == "UNKNOWN":
            continue
        
        keywords = config.get("keywords", [])
        score = sum(1 for kw in keywords if kw.lower() in combined)
        
        # Bonus for title match
        if any(kw.lower() in title_lower for kw in keywords):
            score += 2
        
        scores[doc_type] = score
    
    if not scores or max(scores.values()) == 0:
        return "UNKNOWN", 0.0
    
    best_type = max(scores, key=scores.get)
    max_score = scores[best_type]
    total_keywords = len(RUBRICA["tipos_documentos_entregables"][best_type]["keywords"])
    
    confidence = min(max_score / max(total_keywords, 1), 1.0)
    
    # Threshold: if confidence < 0.4, use LLM as tiebreaker
    if confidence < 0.4:
        return "UNKNOWN", confidence
    
    return best_type, confidence


async def classify_document(outline: DocumentOutline, run_id: str) -> Tuple[DocumentType, float, dict]:
    """
    Classify document type with deterministic detector + LLM tiebreaker
    MVP1.1: Uses doc_type_detector.py (Gobierno rules)
    Returns: (doc_type, confidence, detection_result)
    """
    logger.info(f"Classifying document with deterministic detector", extra={"run_id": run_id})
    
    # Prepare data for detector
    headings = [s.title for s in outline.sections]
    tables = [{"context": "table_data"}] * outline.tables_count  # Simplified
    full_text = "\n".join([s.content for s in outline.sections])
    
    # Run deterministic detector
    detection_result = detect_document_type(
        filename=outline.filename,
        headings=headings,
        tables=tables,
        full_text=full_text
    )
    
    doc_type = detection_result["tipo_detectado"]
    confidence = detection_result["confianza"]
    
    logger.info(f"Deterministic detection: {doc_type} ({confidence:.2f})", 
               extra={"run_id": run_id, "doc_type": doc_type, "confidence": confidence})
    
    # Check if LLM tiebreaker is needed
    top3 = detection_result.get("top3", [])
    if len(top3) >= 2 and doc_type != "UNKNOWN":
        top1_score = top3[0]["score"]
        top2_score = top3[1]["score"]
        
        # Tie within 5 points => use LLM
        if abs(top1_score - top2_score) <= 5:
            logger.info(f"Close tie detected ({top1_score} vs {top2_score}), using LLM tiebreaker", 
                       extra={"run_id": run_id})
            
            try:
                llm = get_llm()
                
                # Prepare context for LLM
                sections_summary = "\n".join([f"- {s.title}" for s in outline.sections[:15]])
                
                prompt = f"""Desempate entre dos tipos de documento muy cercanos:

Candidato 1: {top3[0]['type']} (score: {top1_score})
Candidato 2: {top3[1]['type']} (score: {top2_score})

Documento:
Título: {outline.metadata.get('title', 'Sin título')}
Secciones: {sections_summary}

Señales detectadas:
- {top3[0]['type']}: {top3[0]['why']}
- {top3[1]['type']}: {top3[1]['why']}

Responde SOLO con el ganador en JSON:
{{
  "winner": "{top3[0]['type']}" o "{top3[1]['type']}",
  "reasoning": "..."
}}"""
                
                response = await llm.generate_json(prompt)
                llm_winner = response.get("winner", doc_type)
                
                if llm_winner in [top3[0]['type'], top3[1]['type']]:
                    doc_type = llm_winner
                    detection_result["tipo_detectado"] = llm_winner
                    detection_result["razon"] += f" | LLM tiebreaker: {response.get('reasoning', '')}"
                    logger.info(f"LLM tiebreaker selected: {llm_winner}", extra={"run_id": run_id})
                
            except Exception as e:
                logger.error(f"LLM tiebreaker failed: {e}", extra={"run_id": run_id})
    
    return doc_type, confidence, detection_result
