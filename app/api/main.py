"""Privacy Gate FastAPI app.

Stateless API (architecture.md §4.2): every request carries the data it
needs. Endpoint handlers import `app.detector.detect`, `app.fixtures`,
and `app.reasoner.reason` defensively (lazily, inside the function body)
so this module can be imported -- and its own tests can run -- even
before those sibling modules exist or while they are mid-edit by other
agents (development-plan.md §7).

Serves the three static PWA entry points (ADR-013): /vault/,
/privacy-export/, /theme/. Root redirects to /vault/.
"""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

from app.api.contracts import (
    AuditRequest,
    AuditResponse,
    DetectionResultModel,
    DetectRequest,
    DetectResponse,
    DocumentsResponse,
    DocumentSummary,
    ReasonRequest,
    SanitiseRequest,
    SanitiseResponse,
)

STATIC_DIR = Path(__file__).resolve().parent.parent / "static"

DEFAULT_MANIFEST = {
    "name": "Privacy Gate",
    "short_name": "PrivacyGate",
    "description": "Assisted redaction with human approval",
    "start_url": "/",
    "display": "standalone",
    "background_color": "#111214",
    "theme_color": "#1a7f4b",
    "icons": [
        {"src": "/static/icons/icon-192.png", "sizes": "192x192", "type": "image/png"},
        {"src": "/static/icons/icon-512.png", "sizes": "512x512", "type": "image/png"},
    ],
}

app = FastAPI(title="Privacy Gate API")


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Consistent error shape (api.md §7): {"error": ..., "detail": ...}."""
    detail = exc.detail
    if isinstance(detail, dict) and "error" in detail:
        return JSONResponse(status_code=exc.status_code, content=detail)
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": str(detail), "detail": None},
    )


# --- API routes ------------------------------------------------------


@app.get("/api/documents", response_model=DocumentsResponse)
def get_documents() -> DocumentsResponse:
    try:
        from app.fixtures import DOCUMENTS
    except ImportError:
        DOCUMENTS = {}

    documents = [
        DocumentSummary(id=doc_id, name=_display_name(doc_id), text=text)
        for doc_id, text in DOCUMENTS.items()
    ]
    return DocumentsResponse(documents=documents)


def _display_name(doc_id: str) -> str:
    return doc_id.replace("_", " ").title()


@app.post("/api/detect", response_model=DetectResponse)
def post_detect(req: DetectRequest) -> DetectResponse:
    if not req.documents:
        raise HTTPException(400, "documents array is empty or missing")

    try:
        from app.detector import detect
    except ImportError:
        detect = None

    results: dict[str, DetectionResultModel] = {}
    for doc in req.documents:
        if detect is None:
            results[doc.id] = DetectionResultModel(
                text=doc.text,
                documentName=doc.id,
                warning="detector module unavailable",
            )
            continue
        raw = detect(doc.text)
        results[doc.id] = DetectionResultModel(
            text=raw.get("text", doc.text),
            spans=raw.get("spans", []),
            images=raw.get("images", []),
            documentName=raw.get("documentName", doc.id),
            fallback_triggered=raw.get("fallback_triggered", False),
            warning=raw.get("warning", ""),
        )

    return DetectResponse(results=results)


@app.post("/api/sanitise", response_model=SanitiseResponse)
def post_sanitise(req: SanitiseRequest) -> SanitiseResponse:
    if req.toggles is None:
        raise HTTPException(400, "toggles is missing")

    doc_ids = {d.id for d in req.documents}
    for doc_id in req.spans:
        if doc_id not in doc_ids:
            raise HTTPException(
                422, f"spans reference document id '{doc_id}' not in documents"
            )

    documents = {d.id: d.text for d in req.documents}
    all_spans = {
        doc_id: [s.model_dump() for s in spans] for doc_id, spans in req.spans.items()
    }

    from app.sanitiser import sanitise_multi

    payload = sanitise_multi(documents, all_spans, req.toggles)
    return SanitiseResponse(sanitised_payload=payload)


@app.post("/api/reason")
def post_reason(req: ReasonRequest) -> dict:
    if not req.sanitised_payload:
        raise HTTPException(400, "sanitised_payload is empty or missing")

    try:
        from app.reasoner import reason
    except ImportError:
        reason = None

    if reason is None:
        return {
            "inconsistency_detected": False,
            "analysis": "Cloud reasoning failed: reasoner module unavailable",
            "draft_letter": "",
        }

    return reason(req.sanitised_payload)


@app.post("/api/audit", response_model=AuditResponse)
def post_audit(req: AuditRequest) -> AuditResponse:
    from app.audit import build_audit

    all_spans = {
        doc_id: [s.model_dump() for s in spans] for doc_id, spans in req.spans.items()
    }
    detection_results = {
        doc_id: dr.model_dump() for doc_id, dr in req.detection_results.items()
    }
    entries = build_audit(all_spans, req.toggles, detection_results)
    return AuditResponse(audit_log=entries)


# --- Static / PWA routes ----------------------------------------------


@app.get("/")
def root() -> RedirectResponse:
    return RedirectResponse(url="/vault/")


@app.get("/manifest.json")
def manifest() -> JSONResponse:
    manifest_path = STATIC_DIR / "manifest.json"
    if manifest_path.is_file():
        import json

        return JSONResponse(json.loads(manifest_path.read_text()))
    return JSONResponse(DEFAULT_MANIFEST)


@app.get("/service-worker.js")
def service_worker():
    from fastapi.responses import FileResponse, PlainTextResponse

    sw_path = STATIC_DIR / "service-worker.js"
    if sw_path.is_file():
        return FileResponse(sw_path, media_type="application/javascript")
    return PlainTextResponse("", media_type="application/javascript")


if STATIC_DIR.is_dir():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

    for route_name in ("vault", "privacy-export", "theme"):
        route_dir = STATIC_DIR / route_name
        if route_dir.is_dir():
            app.mount(
                f"/{route_name}",
                StaticFiles(directory=str(route_dir), html=True),
                name=route_name,
            )
