"""
Detector determinístico de tipo de documento
Basado en document_type_detection_rhino.json (Gobierno)
"""
import json
import logging
import re
from typing import Dict, List, Tuple, Any
from pathlib import Path

logger = logging.getLogger(__name__)

# Load detection config
CONFIG_PATH = Path(__file__).parent.parent / "config" / "document_type_detection_rhino.json"
with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    DETECTION_CONFIG = json.load(f)


def extract_features(filename: str, headings: List[str], tables: List[Dict], 
                    full_text: str) -> Dict[str, Any]:
    """
    Extract features from document for type detection
    Returns: features dict with signals and evidence
    """
    features = {
        "filename": filename.lower(),
        "filename_tokens": set(re.findall(r'\w+', filename.lower())),
        "headings": [h.lower() for h in headings],
        "headings_text": " ".join(headings).lower(),
        "tables_count": len(tables),
        "full_text_lower": full_text.lower(),
        "word_count": len(full_text.split()),
        "signals_found": {},
        "evidence": {}
    }
    
    return features


def has_at_least_one_strong_indicator(doc_type: str, features: Dict, 
                                      config: Dict) -> Tuple[bool, List[str]]:
    """
    Check if document has at least one strong indicator for the type
    Returns: (has_indicator, list_of_found_indicators)
    """
    type_config = config["document_types"][doc_type]
    strong_indicators = type_config["strong_indicators"]
    found = []
    
    # Check headings
    for indicator in strong_indicators["headings"]:
        indicator_lower = indicator.lower()
        for heading in features["headings"]:
            if indicator_lower in heading:
                found.append(f"heading:{indicator}")
                break
    
    # Check tables (by keywords in table context)
    for indicator in strong_indicators["tables"]:
        indicator_lower = indicator.lower()
        if indicator_lower in features["full_text_lower"]:
            # Simple heuristic: if keyword appears near table context
            found.append(f"table:{indicator}")
    
    # Check keywords with density
    keyword_matches = 0
    for keyword in strong_indicators["keywords"]:
        keyword_lower = keyword.lower()
        count = features["full_text_lower"].count(keyword_lower)
        if count > 0:
            keyword_matches += count
            if count >= 2:  # Strong signal if appears multiple times
                found.append(f"keyword:{keyword}({count}x)")
    
    return len(found) > 0, found


def check_structural_patterns(doc_type: str, features: Dict, config: Dict) -> List[str]:
    """
    Check structural patterns for document type
    Returns: list of matched patterns
    """
    type_config = config["document_types"][doc_type]
    patterns = type_config.get("structural_patterns", [])
    matched = []
    
    text = features["full_text_lower"]
    headings_text = features["headings_text"]
    
    # Pattern detection heuristics
    pattern_checks = {
        "tiene_seccion_rollback": lambda: "rollback" in headings_text,
        "tiene_inventario_datos": lambda: "inventario" in text and "datos" in text,
        "tiene_cronograma_migracion": lambda: "cronograma" in text or "timeline" in text,
        "tiene_matriz_trazabilidad_RF_TC": lambda: ("rf" in text or "requisito" in text) and ("tc" in text or "caso" in text) and "trazabilidad" in text,
        "tiene_arquitectura": lambda: "arquitectura" in headings_text or "diagrama" in text,
        "tiene_requisitos_funcionales": lambda: "requisitos funcionales" in text or "rf-" in text,
        "tiene_modelo_datos": lambda: "modelo de datos" in text or "entidades" in text,
        "tiene_escenarios_negocio": lambda: "escenario" in text and ("negocio" in text or "uso" in text),
        "tiene_tabla_parametros": lambda: "parámetros" in text or "configuración" in text,
        "tiene_comandos_scripts": lambda: "comando" in text or "script" in text,
        "tiene_endpoints_apis": lambda: ("endpoint" in text or "api" in text) and features["tables_count"] > 0,
        "tiene_codigos_error": lambda: "código" in text and "error" in text,
        "tiene_checklist": lambda: "checklist" in text or "☐" in text or "[ ]" in text,
        "tiene_criterios_aceptacion": lambda: "criterios" in text and "aceptación" in text,
        "tiene_casos_prueba_con_pasos": lambda: "casos de prueba" in text and "pasos" in text,
        "tiene_datos_prueba": lambda: "datos de prueba" in text or "test data" in text,
        "tiene_resultados_evidencia": lambda: "resultado" in text and ("esperado" in text or "evidencia" in text),
        "tiene_procedimientos_inicio_parada": lambda: ("inicio" in text or "start" in text) and ("parada" in text or "stop" in text),
        "tiene_monitoreo_alertas": lambda: "monitoreo" in text or "alertas" in text,
        "tiene_ventanas_mantenimiento": lambda: "ventana" in text and "mantenimiento" in text,
        "tiene_troubleshooting": lambda: "troubleshooting" in text or "solución de problemas" in text,
        "tiene_timeline_cronologia": lambda: "timeline" in text or "cronología" in text,
        "tiene_causa_raiz": lambda: "causa raíz" in text or "root cause" in text or "5 whys" in text,
        "tiene_acciones_preventivas": lambda: "acciones preventivas" in text or "prevención" in text,
    }
    
    for pattern in patterns:
        if pattern in pattern_checks and pattern_checks[pattern]():
            matched.append(pattern)
    
    return matched


def score_each_type(features: Dict, config: Dict) -> Tuple[Dict[str, float], Dict[str, List[str]]]:
    """
    Score each document type based on features
    Returns: (scores dict, evidence dict)
    """
    scores = {}
    evidence_per_type = {}
    weights = config["pseudocode_scoring_0_100"]["signal_weights"]
    
    for doc_type in config["document_types"].keys():
        if doc_type == "UNKNOWN":
            continue
        
        score = 0
        evidence = []
        type_config = config["document_types"][doc_type]
        
        # 1. Filename exact match
        filename_tokens = type_config["filename_tokens"]
        for token in filename_tokens:
            if token in features["filename_tokens"]:
                score += weights["filename_exact_match"]
                evidence.append(f"filename_match:{token}")
                break
        
        # 2. Strong indicators
        has_strong, strong_found = has_at_least_one_strong_indicator(doc_type, features, config)
        if has_strong:
            # Count heading matches
            heading_matches = [e for e in strong_found if e.startswith("heading:")]
            if heading_matches:
                score += weights["strong_indicator_heading"] * min(len(heading_matches), 3)
                evidence.extend(heading_matches[:3])
            
            # Count table matches
            table_matches = [e for e in strong_found if e.startswith("table:")]
            if table_matches:
                score += weights["strong_indicator_table"] * min(len(table_matches), 2)
                evidence.extend(table_matches[:2])
            
            # Keyword density
            keyword_matches = [e for e in strong_found if e.startswith("keyword:")]
            if len(keyword_matches) >= 5:
                score += weights["keyword_density_high"]
                evidence.append(f"high_keyword_density:{len(keyword_matches)}")
            elif len(keyword_matches) >= 2:
                score += weights["keyword_density_medium"]
                evidence.append(f"medium_keyword_density:{len(keyword_matches)}")
        
        # 3. Structural patterns
        patterns_matched = check_structural_patterns(doc_type, features, config)
        if patterns_matched:
            score += weights["structural_pattern"] * min(len(patterns_matched), 3)
            evidence.extend([f"pattern:{p}" for p in patterns_matched[:3]])
        
        scores[doc_type] = min(score, 100)  # Cap at 100
        evidence_per_type[doc_type] = evidence
    
    return scores, evidence_per_type


def apply_dominancia_estructural(scores: Dict[str, float], features: Dict, 
                                 config: Dict) -> Tuple[str, str]:
    """
    Apply structural dominance rules
    Returns: (winner_type, reason) or (None, None)
    """
    rules = config["dominancia_estructural"]["rules"]
    
    # Get matched patterns from features
    matched_patterns = set()
    for doc_type in config["document_types"].keys():
        if doc_type != "UNKNOWN":
            patterns = check_structural_patterns(doc_type, features, config)
            matched_patterns.update(patterns)
    
    for rule in rules:
        condition = rule["condition"]
        # Simple condition parser (AND logic)
        required_patterns = [p.strip() for p in condition.split(" AND ")]
        if all(p in matched_patterns for p in required_patterns):
            return rule["winner"], rule["reason"]
    
    return None, None


def resolve_conflict(type1: str, type2: str, scores: Dict, evidence: Dict, 
                    config: Dict) -> Tuple[str, str]:
    """
    Resolve conflict between two types using conflict resolution rules
    Returns: (winner, reason)
    """
    conflict_key = f"{type1}_vs_{type2}"
    reverse_key = f"{type2}_vs_{type1}"
    
    conflict_rules = config["conflict_resolution"]
    
    if conflict_key in conflict_rules:
        rule = conflict_rules[conflict_key]
        signals_1 = rule.get(f"signals_favor_{type1.split('_')[0]}", [])
        signals_2 = rule.get(f"signals_favor_{type2.split('_')[0]}", [])
        
        # Count signals for each type
        count_1 = sum(1 for sig in signals_1 if any(sig in e for e in evidence.get(type1, [])))
        count_2 = sum(1 for sig in signals_2 if any(sig in e for e in evidence.get(type2, [])))
        
        if count_1 > count_2:
            return type1, f"Conflict resolution: {rule['rule']}"
        elif count_2 > count_1:
            return type2, f"Conflict resolution: {rule['rule']}"
    
    elif reverse_key in conflict_rules:
        # Try reverse
        winner, reason = resolve_conflict(type2, type1, scores, evidence, config)
        return winner, reason
    
    # Default: higher score wins
    if scores[type1] > scores[type2]:
        return type1, f"Higher score ({scores[type1]:.1f} vs {scores[type2]:.1f})"
    else:
        return type2, f"Higher score ({scores[type2]:.1f} vs {scores[type1]:.1f})"


def select_type(scores: Dict[str, float], evidence: Dict[str, List[str]], 
               config: Dict, filename_tokens: set, features: Dict) -> Dict[str, Any]:
    """
    Select document type based on scores, evidence, and rules
    Returns: result dict with tipo_detectado, confianza, razon, top3, etc.
    """
    thresholds = config["type_thresholds"]
    
    # Filter candidates: score >= threshold AND has strong indicator
    candidates = []
    for doc_type, score in scores.items():
        if score >= thresholds[doc_type]:
            has_strong, _ = has_at_least_one_strong_indicator(doc_type, features, config)
            if has_strong:
                candidates.append((doc_type, score))
    
    # Sort by score descending
    candidates.sort(key=lambda x: x[1], reverse=True)
    
    # Get top 3 for reporting
    top3 = [
        {
            "type": t,
            "score": round(s, 1),
            "why": f"{len(evidence.get(t, []))} signals: " + ", ".join(evidence.get(t, [])[:3])
        }
        for t, s in sorted(scores.items(), key=lambda x: x[1], reverse=True)[:3]
    ]
    
    # No candidates => UNKNOWN
    if not candidates:
        return {
            "tipo_detectado": "UNKNOWN",
            "confianza": 0.0,
            "razon": "Ningún tipo supera umbral o tiene indicadores fuertes",
            "top3": top3,
            "conflict_name_vs_content": False,
            "secondary_signals": [],
            "questions_to_classify": config["unknown_handling"]["questions_to_classify"]
        }
    
    # Apply dominancia estructural
    dom_winner, dom_reason = apply_dominancia_estructural(scores, features, config)
    if dom_winner and dom_winner in [c[0] for c in candidates]:
        winner = dom_winner
        reason = f"Dominancia estructural: {dom_reason}"
        confidence = min(scores[winner] / 100, 0.95)
    
    # Single candidate
    elif len(candidates) == 1:
        winner = candidates[0][0]
        reason = f"Único candidato con score {candidates[0][1]:.1f} >= threshold"
        confidence = min(scores[winner] / 100, 0.9)
    
    # Multiple candidates - check for tie
    elif len(candidates) >= 2:
        top1_type, top1_score = candidates[0]
        top2_type, top2_score = candidates[1]
        
        # Tie within 5 points => needs LLM tiebreaker (handled by caller)
        if abs(top1_score - top2_score) <= 5:
            # Check conflict resolution first
            winner, reason = resolve_conflict(top1_type, top2_type, scores, evidence, config)
            confidence = min(scores[winner] / 100, 0.75)
            reason += " (empate cercano, aplicada regla de conflicto)"
        else:
            # Clear winner
            winner = top1_type
            reason = f"Score más alto: {top1_score:.1f} vs {top2_score:.1f}"
            confidence = min(scores[winner] / 100, 0.85)
    
    # Check filename vs content conflict
    conflict_name_vs_content = False
    filename_suggested_type = None
    
    for doc_type in config["document_types"].keys():
        if doc_type == "UNKNOWN":
            continue
        tokens = config["document_types"][doc_type]["filename_tokens"]
        if any(token in filename_tokens for token in tokens):
            filename_suggested_type = doc_type
            break
    
    if filename_suggested_type and filename_suggested_type != winner:
        policy = config["filename_vs_content_policy"]
        score_diff = abs(scores[winner] - scores.get(filename_suggested_type, 0))
        has_strong, _ = has_at_least_one_strong_indicator(winner, features, config)
        strong_count = len(evidence.get(winner, []))
        
        if (score_diff > policy["threshold_difference"] and 
            strong_count >= policy["min_strong_indicators_content"]):
            conflict_name_vs_content = True
            reason += f" | CONFLICTO: nombre sugiere {filename_suggested_type} pero contenido gana por {score_diff:.1f} puntos"
    
    # Secondary signals
    secondary_signals = []
    patterns = check_structural_patterns(winner, features, config)
    if patterns:
        secondary_signals.extend([f"structural:{p}" for p in patterns])
    
    return {
        "tipo_detectado": winner,
        "confianza": round(confidence, 2),
        "razon": reason,
        "top3": top3,
        "conflict_name_vs_content": conflict_name_vs_content,
        "secondary_signals": secondary_signals[:5],
        "filename_suggested_type": filename_suggested_type if conflict_name_vs_content else None
    }


def detect_document_type(filename: str, headings: List[str], tables: List[Dict], 
                        full_text: str) -> Dict[str, Any]:
    """
    Main entry point for document type detection
    Returns: detection result with tipo_detectado, confianza, etc.
    """
    logger.info(f"Detecting document type for: {filename}")
    
    # Extract features
    features = extract_features(filename, headings, tables, full_text)
    
    # Score each type
    scores, evidence = score_each_type(features, DETECTION_CONFIG)
    
    # Select type
    result = select_type(scores, evidence, DETECTION_CONFIG, features["filename_tokens"], features)
    
    logger.info(f"Detection result: {result['tipo_detectado']} (confidence: {result['confianza']})")
    
    return result
