"""Test document type detector - MVP1.1"""
import pytest
from services.doc_type_detector import (
    extract_features,
    has_at_least_one_strong_indicator,
    check_structural_patterns,
    score_each_type,
    select_type,
    detect_document_type,
    DETECTION_CONFIG
)


def test_dtm_vs_plan_pruebas_with_matriz_trazabilidad():
    """DTM should win if has matriz RF↔TC↔release"""
    filename = "plan_migracion_v1.docx"
    headings = [
        "Plan de Migración",
        "Inventario de Datos",
        "Matriz de Trazabilidad RF-TC-Release",
        "Plan de Rollback"
    ]
    tables = [{"context": "matriz"}]
    full_text = """
    Plan de migración de datos.
    Inventario completo de datos origen y destino.
    Matriz de trazabilidad: RF-001 ↔ TC-001 ↔ Release 1.0
    Requisitos funcionales mapeados a casos de prueba.
    Plan de rollback detallado con procedimientos.
    """
    
    result = detect_document_type(filename, headings, tables, full_text)
    
    assert result["tipo_detectado"] == "DTM"
    assert result["confianza"] > 0.6
    assert "matriz" in result["razon"].lower() or "trazabilidad" in result["razon"].lower()


def test_plan_pruebas_with_pasos_datos_resultados():
    """PLAN_PRUEBAS should win if has pasos/datos/resultados"""
    filename = "plan_pruebas_integracion.docx"
    headings = [
        "Plan de Pruebas",
        "Casos de Prueba",
        "Datos de Prueba",
        "Resultados Esperados"
    ]
    tables = [{"context": "casos"}]
    full_text = """
    Plan de pruebas de integración.
    Casos de prueba:
    TC-001: Validar login
    Pasos:
    1. Ingresar usuario
    2. Ingresar contraseña
    3. Click en Login
    Datos de prueba: usuario=test, password=test123
    Resultado esperado: Usuario autenticado correctamente
    Resultado obtenido: OK
    """
    
    result = detect_document_type(filename, headings, tables, full_text)
    
    assert result["tipo_detectado"] == "PLAN_PRUEBAS_EVIDENCIA"
    assert result["confianza"] > 0.5


def test_dsp_vs_dtc_with_apis_endpoints():
    """DTC should win if has APIs/endpoints/códigos error"""
    filename = "configuracion_api_gateway.docx"
    headings = [
        "Configuración API Gateway",
        "Endpoints",
        "Autenticación",
        "Códigos de Error"
    ]
    tables = [{"context": "endpoints"}]
    full_text = """
    Configuración de API Gateway.
    Endpoints disponibles:
    GET /api/users - Obtener usuarios
    POST /api/users - Crear usuario
    Autenticación: OAuth2
    Códigos de error:
    400 - Bad Request
    401 - Unauthorized
    500 - Internal Server Error
    """
    
    result = detect_document_type(filename, headings, tables, full_text)
    
    assert result["tipo_detectado"] == "DTC"
    assert result["confianza"] > 0.6


def test_dsp_with_escenarios_negocio():
    """DSP should win if has escenarios/reglas negocio"""
    filename = "propuesta_sistema_inventario.docx"
    headings = [
        "Solución Propuesta",
        "Arquitectura",
        "Escenarios de Uso",
        "Reglas de Negocio"
    ]
    tables = [{"context": "requisitos"}]
    full_text = """
    Documento de solución propuesta para sistema de inventario.
    Arquitectura de microservicios con API Gateway.
    Escenarios de uso:
    - Usuario consulta stock disponible
    - Sistema valida reglas de negocio
    Reglas de negocio:
    - Stock mínimo: 10 unidades
    - Alerta automática si stock < mínimo
    """
    
    result = detect_document_type(filename, headings, tables, full_text)
    
    assert result["tipo_detectado"] == "DSP"
    assert result["confianza"] > 0.5


def test_runbook_vs_dtc_with_ventanas_monitoreo():
    """RUNBOOK should win if has ventanas/monitoreo/rollback operativo"""
    filename = "runbook_produccion.docx"
    headings = [
        "Runbook de Producción",
        "Procedimientos de Inicio y Parada",
        "Monitoreo y Alertas",
        "Ventanas de Mantenimiento"
    ]
    tables = [{"context": "procedimientos"}]
    full_text = """
    Runbook para operación en producción.
    Procedimientos de inicio:
    1. Verificar servicios
    2. Iniciar aplicación
    Monitoreo: Dashboard en Grafana
    Alertas: CPU > 80%, Memoria > 90%
    Ventanas de mantenimiento: Domingos 2-4 AM
    Rollback operativo: Revertir a versión anterior
    """
    
    result = detect_document_type(filename, headings, tables, full_text)
    
    assert result["tipo_detectado"] == "RUNBOOK_MANUAL_OPERACION"
    assert result["confianza"] > 0.5


def test_rca_vs_runbook_with_timeline_causa_raiz():
    """RCA should win if has timeline/causa raíz"""
    filename = "rca_incidente_20260220.docx"
    headings = [
        "Root Cause Analysis",
        "Timeline del Incidente",
        "Análisis de Causa Raíz",
        "Acciones Preventivas"
    ]
    tables = [{"context": "timeline"}]
    full_text = """
    Análisis de causa raíz del incidente del 20/02/2026.
    Timeline:
    14:00 - Inicio del incidente
    14:15 - Detección de error
    14:30 - Mitigación aplicada
    Análisis de causa raíz usando 5 Whys:
    1. ¿Por qué falló? - Timeout en base de datos
    2. ¿Por qué timeout? - Consulta lenta
    3. ¿Por qué lenta? - Falta índice
    Causa raíz: Índice faltante en tabla usuarios
    Acciones preventivas: Crear índice, monitoreo de queries lentas
    """
    
    result = detect_document_type(filename, headings, tables, full_text)
    
    assert result["tipo_detectado"] == "SOPORTE_EVOLUTIVO_RCA"
    assert result["confianza"] > 0.6


def test_conflict_name_vs_content():
    """Content should win if differs >15 points and has >=2 strong indicators"""
    filename = "documento_DTC_configuracion.docx"  # Name suggests DTC
    headings = [
        "Plan de Migración",  # Content suggests DTM
        "Inventario de Datos",
        "Estrategia de Migración",
        "Plan de Rollback"
    ]
    tables = [{"context": "inventario"}]
    full_text = """
    Plan de migración completo.
    Inventario de datos origen y destino.
    Estrategia: migración por fases.
    Plan de rollback con procedimientos detallados.
    Validación post-migración.
    """
    
    result = detect_document_type(filename, headings, tables, full_text)
    
    # Content should win (DTM) over filename (DTC)
    assert result["tipo_detectado"] == "DTM"
    assert result["conflict_name_vs_content"] == True
    assert result["filename_suggested_type"] == "DTC"


def test_unknown_without_threshold():
    """UNKNOWN if no type reaches threshold"""
    filename = "documento_generico.docx"
    headings = ["Introducción", "Contenido", "Conclusión"]
    tables = []
    full_text = """
    Este es un documento genérico sin estructura específica.
    Contiene información general sin keywords específicos.
    """
    
    result = detect_document_type(filename, headings, tables, full_text)
    
    assert result["tipo_detectado"] == "UNKNOWN"
    assert result["confianza"] == 0.0
    assert "questions_to_classify" in result
    assert len(result["questions_to_classify"]) > 0


def test_unknown_without_strong_indicators():
    """UNKNOWN if no strong indicators even with some keywords"""
    filename = "notas.docx"
    headings = ["Notas de Reunión"]
    tables = []
    full_text = """
    Notas de la reunión del equipo.
    Se discutió sobre migración y configuración.
    Pendientes: revisar documentación.
    """
    
    result = detect_document_type(filename, headings, tables, full_text)
    
    # Should be UNKNOWN because no strong indicators
    assert result["tipo_detectado"] == "UNKNOWN"


def test_top3_candidates():
    """Top 3 candidates should be returned"""
    filename = "documento_tecnico.docx"
    headings = ["Arquitectura", "Configuración"]
    tables = []
    full_text = """
    Documento técnico con arquitectura y configuración.
    """
    
    result = detect_document_type(filename, headings, tables, full_text)
    
    assert "top3" in result
    assert len(result["top3"]) == 3
    assert all("type" in c and "score" in c and "why" in c for c in result["top3"])


def test_has_at_least_one_strong_indicator():
    """Test strong indicator detection"""
    features = {
        "headings": ["plan de migración", "rollback"],
        "full_text_lower": "migración de datos rollback cutover",
        "headings_text": "plan de migración rollback"
    }
    
    has_indicator, found = has_at_least_one_strong_indicator("DTM", features, DETECTION_CONFIG)
    
    assert has_indicator == True
    assert len(found) > 0


def test_structural_patterns():
    """Test structural pattern detection"""
    features = {
        "headings_text": "plan de rollback inventario de datos",
        "full_text_lower": "rollback inventario datos cronograma timeline",
        "tables_count": 2
    }
    
    patterns = check_structural_patterns("DTM", features, DETECTION_CONFIG)
    
    assert len(patterns) > 0
    assert "tiene_seccion_rollback" in patterns or "tiene_inventario_datos" in patterns
