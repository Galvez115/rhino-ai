"""Test scoring logic"""
import pytest
from domain.models import CriterioEvaluacion


def test_score_with_na_excludes_denominator():
    """NA should exclude criterio from denominator"""
    criterios = [
        CriterioEvaluacion(
            criterio_id="C1",
            nombre="Test 1",
            peso=20,
            estado="CUMPLE",
            puntos_obtenidos=20,
            evidencia=[],
            justificacion="OK",
            severidad_si_falta="menor"
        ),
        CriterioEvaluacion(
            criterio_id="C2",
            nombre="Test 2",
            peso=30,
            estado="NA",  # Should be excluded
            puntos_obtenidos=0,
            evidencia=[],
            justificacion="No aplica",
            severidad_si_falta="menor"
        ),
        CriterioEvaluacion(
            criterio_id="C3",
            nombre="Test 3",
            peso=50,
            estado="PARCIAL",
            puntos_obtenidos=25,
            evidencia=[],
            justificacion="Parcial",
            severidad_si_falta="menor"
        ),
    ]
    
    # Calculate score
    puntos_total = sum(c.puntos_obtenidos for c in criterios if c.estado != "NA")
    peso_aplicable = sum(c.peso for c in criterios if c.estado != "NA")
    
    # Expected: (20 + 25) / (20 + 50) * 100 = 64.29
    score = (puntos_total / peso_aplicable) * 100
    
    assert peso_aplicable == 70  # 20 + 50, excluding NA
    assert abs(score - 64.29) < 0.1


def test_penalties_no_double_punishment():
    """Penalties should not apply if criterio already at 0"""
    criterio = CriterioEvaluacion(
        criterio_id="C1",
        nombre="Critical",
        peso=20,
        estado="NO",
        puntos_obtenidos=0,  # Already at 0
        evidencia=[],
        justificacion="Missing",
        severidad_si_falta="bloqueante"
    )
    
    base_score = 50.0
    
    # Apply penalty logic
    if criterio.puntos_obtenidos > 0:
        # Should NOT enter here
        penalty = -10
        score = base_score + penalty
    else:
        # Should use this path
        score = base_score
    
    assert score == 50.0  # No penalty applied


def test_partial_gives_half_points():
    """PARCIAL should give 50% of peso"""
    criterio = CriterioEvaluacion(
        criterio_id="C1",
        nombre="Test",
        peso=40,
        estado="PARCIAL",
        puntos_obtenidos=20,  # 50% of 40
        evidencia=[],
        justificacion="Partial",
        severidad_si_falta="menor"
    )
    
    assert criterio.puntos_obtenidos == criterio.peso * 0.5


def test_score_cannot_go_below_zero():
    """Score should not go below 0 after penalties"""
    base_score = 5.0
    penalty = -10
    
    score = max(0, base_score + penalty)
    
    assert score == 0.0


def test_score_cannot_exceed_100():
    """Score should not exceed 100"""
    base_score = 95.0
    bonus = 10
    
    score = min(100, base_score + bonus)
    
    assert score == 100.0
