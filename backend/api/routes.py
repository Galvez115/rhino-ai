"""API routes"""
import os
import uuid
import logging
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import JSONResponse, PlainTextResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from domain.models import AnswersSubmission, EvaluationResult
from storage.database import get_session, Run, Question
from utils.docx_parser import extract_document_structure
from services.doc_type_detector import detect_document_type
from services.evaluator import DocumentEvaluator
from utils.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/runs")
async def create_run(
    file: UploadFile = File(...),
    session: AsyncSession = Depends(get_session)
):
    """
    Upload DOCX and create evaluation run
    Returns: run_id, outline, preliminary score, questions
    """
    run_id = str(uuid.uuid4())
    logger.info(f"Creating run", extra={"run_id": run_id, "filename": file.filename})
    
    # Validate file type
    if not file.filename.endswith('.docx'):
        raise HTTPException(400, "Only DOCX files are supported")
    
    # Save file
    file_path = os.path.join(settings.UPLOAD_DIR, f"{run_id}_{file.filename}")
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)
    
    try:
        # Extract structure
        outline = extract_document_structure(file_path)
        
        # Detect document type with new deterministic detector
        headings = [s.title for s in outline.sections]
        tables = [{"context": "table"} for _ in range(outline.tables_count)]
        full_text = "\n".join([s.content for s in outline.sections])
        
        detection_result = detect_document_type(
            filename=file.filename,
            headings=headings,
            tables=tables,
            full_text=full_text
        )
        
        doc_type = detection_result["tipo_detectado"]
        confidence = detection_result["confianza"]
        
        # Initial evaluation
        evaluator = DocumentEvaluator(outline, doc_type, run_id, detection_result)
        evaluation = await evaluator.evaluate()
        evaluation.doc_type_confidence = confidence
        
        # Save to database
        db_run = Run(
            id=run_id,
            filename=file.filename,
            doc_type=doc_type,
            doc_type_confidence=confidence,
            decision=evaluation.decision,
            score=evaluation.score,
            outline_json=outline.model_dump(),
            evaluation_json=evaluation.model_dump(),
            detection_result_json=detection_result  # MVP1.1
        )
        session.add(db_run)
        
        # Save questions
        for q in evaluation.preguntas:
            db_question = Question(
                run_id=run_id,
                question_id=q.id,
                question=q.pregunta,
                priority=q.prioridad
            )
            session.add(db_question)
        
        await session.commit()
        
        logger.info(f"Run created successfully", extra={
            "run_id": run_id,
            "doc_type": doc_type,
            "score": evaluation.score,
            "decision": evaluation.decision
        })
        
        return {
            "run_id": run_id,
            "filename": file.filename,
            "doc_type": doc_type,
            "doc_type_confidence": confidence,
            "detection_result": detection_result,  # MVP1.1: Include full detection result
            "outline": outline.model_dump(),
            "preliminary_evaluation": {
                "score": evaluation.score,
                "decision": evaluation.decision,
                "fail_fast": [ff.model_dump() for ff in evaluation.fail_fast],
                "score_potencial": evaluation.score_potencial.model_dump()
            },
            "preguntas": [q.model_dump() for q in evaluation.preguntas]
        }
        
    except Exception as e:
        logger.error(f"Error processing document: {e}", extra={"run_id": run_id})
        raise HTTPException(500, f"Error processing document: {str(e)}")


@router.post("/runs/{run_id}/answers")
async def submit_answers(
    run_id: str,
    submission: AnswersSubmission,
    session: AsyncSession = Depends(get_session)
):
    """
    Submit answers and re-evaluate
    Returns: complete evaluation report
    """
    logger.info(f"Submitting answers", extra={"run_id": run_id})
    
    # Get run
    result = await session.execute(select(Run).where(Run.id == run_id))
    run = result.scalar_one_or_none()
    
    if not run:
        raise HTTPException(404, "Run not found")
    
    # Update answers in database
    for answer in submission.answers:
        result = await session.execute(
            select(Question).where(
                Question.run_id == run_id,
                Question.question_id == answer.question_id
            )
        )
        question = result.scalar_one_or_none()
        if question:
            question.answer = answer.answer
    
    await session.commit()
    
    # Re-evaluate with answers
    from domain.models import DocumentOutline
    outline = DocumentOutline(**run.outline_json)
    detection_result = run.detection_result_json  # MVP1.1
    
    user_answers = {
        f"answer_{a.question_id.split('-')[1]}": a.answer
        for a in submission.answers
    }
    
    evaluator = DocumentEvaluator(outline, run.doc_type, run_id, detection_result)  # MVP1.1: Pass detection_result
    evaluation = await evaluator.evaluate(user_answers)
    
    # Update run
    run.decision = evaluation.decision
    run.score = evaluation.score
    run.evaluation_json = evaluation.model_dump()
    run.report_json = evaluation.model_dump()
    await session.commit()
    
    logger.info(f"Re-evaluation complete", extra={
        "run_id": run_id,
        "score": evaluation.score,
        "decision": evaluation.decision
    })
    
    return evaluation.model_dump()


@router.get("/runs/{run_id}")
async def get_run(run_id: str, session: AsyncSession = Depends(get_session)):
    """Get run status and report"""
    result = await session.execute(select(Run).where(Run.id == run_id))
    run = result.scalar_one_or_none()
    
    if not run:
        raise HTTPException(404, "Run not found")
    
    return {
        "run_id": run.id,
        "filename": run.filename,
        "doc_type": run.doc_type,
        "decision": run.decision,
        "score": run.score,
        "created_at": run.created_at.isoformat(),
        "evaluation": run.evaluation_json,
        "report": run.report_json
    }


@router.get("/runs/{run_id}/export.json")
async def export_json(run_id: str, session: AsyncSession = Depends(get_session)):
    """Export report as JSON"""
    result = await session.execute(select(Run).where(Run.id == run_id))
    run = result.scalar_one_or_none()
    
    if not run or not run.report_json:
        raise HTTPException(404, "Report not found")
    
    return JSONResponse(content=run.report_json)


@router.get("/runs/{run_id}/export.md")
async def export_markdown(run_id: str, session: AsyncSession = Depends(get_session)):
    """Export report as Markdown"""
    result = await session.execute(select(Run).where(Run.id == run_id))
    run = result.scalar_one_or_none()
    
    if not run or not run.report_json:
        raise HTTPException(404, "Report not found")
    
    # Generate markdown
    report = run.report_json
    md = f"""# Rhino AI - Reporte de Evaluación

**Documento:** {run.filename}  
**Tipo:** {run.doc_type}  
**Fecha:** {run.created_at.strftime('%Y-%m-%d %H:%M')}  

---

## Resultado

**Score:** {report['score']:.2f}/100  
**Decisión:** {report['decision']}  

### Score Potencial
- Actual: {report['score_potencial']['actual']}
- Si corrige P0: {report['score_potencial']['si_corrige_p0']}
- Si corrige P0+P1: {report['score_potencial']['si_corrige_p0_p1']}
- Si corrige todo: {report['score_potencial']['si_corrige_todo']}

---

## Fail-Fast

"""
    
    for ff in report.get('fail_fast', []):
        if ff['active']:
            md += f"### ⛔ {ff['name']}\n"
            md += f"**Evidencia:** {ff['evidencia']}\n\n"
            md += f"{ff['explicacion']}\n\n"
    
    md += "\n---\n\n## Hallazgos\n\n"
    
    for h in report.get('hallazgos', []):
        icon = {"bloqueante": "🔴", "mayor": "🟠", "menor": "🟡", "sugerencia": "🔵"}[h['severidad']]
        md += f"### {icon} [{h['prioridad']}] {h['titulo']}\n\n"
        md += f"**Severidad:** {h['severidad']}  \n"
        md += f"**Evidencia:** {h['evidencia_detalle']}  \n\n"
        md += f"**Recomendación:** {h['recomendacion']}\n\n"
        md += f"**Qué agregar:** {h['que_agregar']}\n\n"
        md += f"**Dónde:** {h['donde_insertar']}\n\n"
        md += f"**Ejemplo:**\n```\n{h['ejemplo_texto']}\n```\n\n"
        md += f"**Impacto estimado:** +{h['impacto_estimado']:.1f} puntos\n\n"
        md += "---\n\n"
    
    return PlainTextResponse(content=md, media_type="text/markdown")
