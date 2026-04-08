"""Server-rendered UI routes."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, Form, Request, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from urban_garbanzo.dependencies import get_evaluator
from urban_garbanzo.exceptions import AppError
from urban_garbanzo.models import Evaluation, Prompt
from urban_garbanzo.schemas.evaluation import build_evaluation_read
from urban_garbanzo.services import EvaluatorService
from urban_garbanzo.services.evaluator import to_decimal

BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

router = APIRouter(include_in_schema=False)


def render_index(
    request: Request,
    *,
    form_data: dict[str, str] | None = None,
    result: dict[str, object] | None = None,
    error_message: str | None = None,
    status_code: int = status.HTTP_200_OK,
) -> HTMLResponse:
    """Render the landing page with optional form state and results."""

    context = {
        "request": request,
        "form_data": form_data or {"text": "", "target_model": ""},
        "result": result,
        "error_message": error_message,
    }
    return templates.TemplateResponse(request, "index.html", context, status_code=status_code)


@router.get("/", response_class=HTMLResponse)
async def index(request: Request) -> HTMLResponse:
    """Render the anonymous evaluation UI."""

    return render_index(request)


@router.post("/", response_class=HTMLResponse)
async def submit_prompt(
    request: Request,
    text: Annotated[str, Form(...)],
    target_model: Annotated[str, Form(...)],
    evaluator: Annotated[EvaluatorService, Depends(get_evaluator)],
) -> HTMLResponse:
    """Create and evaluate a prompt submission from the root UI."""

    normalized_text = text.strip()
    normalized_target_model = target_model.strip()
    form_data = {"text": normalized_text, "target_model": normalized_target_model}

    if len(normalized_text) < 10:
        return render_index(
            request,
            form_data=form_data,
            error_message="Prompt text must be at least 10 characters long.",
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )

    if len(normalized_target_model) < 2:
        return render_index(
            request,
            form_data=form_data,
            error_message="Target model must be at least 2 characters long.",
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )

    try:
        prompt = await Prompt.create(text=normalized_text, target_model=normalized_target_model)
        result = await evaluator.evaluate(prompt.text, prompt.target_model)
        evaluation = await Evaluation.create(
            prompt=prompt,
            clarity=to_decimal(result.clarity),
            correctness=to_decimal(result.correctness),
            information_density=to_decimal(result.information_density),
            hallucination_risk=to_decimal(result.hallucination_risk),
            redundancy=to_decimal(result.redundancy),
            total_score=to_decimal(result.total_score),
            heuristic_scores=result.heuristic_scores,
            llm_scores=result.llm_scores,
            rationale=result.rationale,
            llm_provider=result.llm_provider,
        )
    except AppError as exc:
        return render_index(
            request,
            form_data=form_data,
            error_message=exc.detail,
            status_code=exc.status_code,
        )

    result_payload = {
        "prompt": prompt,
        "evaluation": build_evaluation_read(evaluation),
    }
    return render_index(request, form_data=form_data, result=result_payload)
