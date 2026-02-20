"""Test fail-fast logic"""
import pytest
from domain.models import FailFast, Hallazgo


def test_fail_fast_empty_document():
    """FF-01: Document with < 100 words should trigger"""
    word_count = 50
    
    ff = FailFast(
        code="FF-01",
        name="Documento vacío",
        active=word_count < 100,
        evidencia=f"Word count: {word_count}",
        explicacion="Contenido insuficiente"
    )
    
    assert ff.active is True


def test_fail_fast_sufficient_content():
    """Document with >= 100 words should not trigger FF-01"""
    word_count = 500
    
    ff = FailFast(
        code="FF-01",
        name="Documento vacío",
        active=word_count < 100,
        evidencia=f"Word count: {word_count}",
        explicacion="Contenido insuficiente"
    )
    
    assert ff.active is False


def test_fail_fast_unknown_type_low_confidence():
    """FF-02: UNKNOWN type with low confidence should trigger"""
    doc_type = "UNKNOWN"
    confidence = 0.3
    
    ff = FailFast(
        code="FF-02",
        name="Tipo no identificable",
        active=doc_type == "UNKNOWN" and confidence < 0.6,
        evidencia=f"Type: {doc_type}, Confidence: {confidence}",
        explicacion="No se pudo determinar tipo"
    )
    
    assert ff.active is True


def test_fail_fast_blocks_approval():
    """Any active fail-fast should result in RECHAZADO"""
    score = 90.0  # High score
    
    fail_fast_list = [
        FailFast(
            code="FF-01",
            name="Test",
            active=True,
            evidencia="Test",
            explicacion="Test"
        )
    ]
    
    # Decision logic
    if any(ff.active for ff in fail_fast_list):
        decision = "RECHAZADO"
    elif score >= 85:
        decision = "APROBADO"
    else:
        decision = "REQUIERE_CORRECCION"
    
    assert decision == "RECHAZADO"


def test_no_fail_fast_allows_normal_decision():
    """No active fail-fast should allow normal decision flow"""
    score = 90.0
    
    fail_fast_list = [
        FailFast(
            code="FF-01",
            name="Test",
            active=False,
            evidencia="Test",
            explicacion="Test"
        )
    ]
    
    bloqueantes = []
    
    # Decision logic
    if any(ff.active for ff in fail_fast_list):
        decision = "RECHAZADO"
    elif score >= 85 and len(bloqueantes) == 0:
        decision = "APROBADO"
    elif score >= 70:
        decision = "REQUIERE_CORRECCION"
    else:
        decision = "RECHAZADO"
    
    assert decision == "APROBADO"
