"""Server-rendered UI routes."""

from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

router = APIRouter(include_in_schema=False)


# ---------------------------------------------------------------------------
# Landing page
# ---------------------------------------------------------------------------


@router.get("/", response_class=HTMLResponse)
async def index(request: Request) -> HTMLResponse:
    """Render the minimal landing page."""

    return templates.TemplateResponse(request, "index.html", {"request": request})


# ---------------------------------------------------------------------------
# Editor page helpers
# ---------------------------------------------------------------------------


def render_editor(
    request: Request,
    *,
    form_data: dict[str, str] | None = None,
) -> HTMLResponse:
    """Render the editor page with optional form state."""

    context = {
        "request": request,
        "form_data": form_data or {"text": "", "target_model": ""},
    }
    return templates.TemplateResponse(request, "editor.html", context)


# ---------------------------------------------------------------------------
# Editor routes
# ---------------------------------------------------------------------------


@router.get("/editor", response_class=HTMLResponse)
async def editor(request: Request) -> HTMLResponse:
    """Render the markdown editor page."""

    return render_editor(request)


@router.post("/editor", response_class=HTMLResponse)
async def editor_post(request: Request) -> HTMLResponse:
    """Re-render the editor page (evaluation is handled via the REST API by JS)."""

    return render_editor(request)
