import math
from pathlib import Path
from typing import Any

import httpx
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.config import get_settings
from app.schemas import ApplyOption, JobHighlight, JobResult, JobSearchRequest, JobSearchResponse

SERPAPI_ENDPOINT = "https://serpapi.com/search.json"
MAX_PAGE_SIZE = 10
PROJECT_ROOT = Path(__file__).resolve().parents[2]
FRONTEND_DIR = PROJECT_ROOT / "frontend"

app = FastAPI(
    title="Careerify Job Search Backend",
    description="Local Careerify job-search website and SerpApi backend.",
    version="0.1.0",
)
app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")


@app.get("/", include_in_schema=False)
async def home() -> FileResponse:
    return FileResponse(FRONTEND_DIR / "index.html")


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/v1/jobs/search", response_model=JobSearchResponse)
async def search_jobs(request: JobSearchRequest) -> JobSearchResponse:
    settings = get_settings()
    api_key = settings.serpapi_api_key.get_secret_value() if settings.serpapi_api_key else ""
    if not api_key:
        raise HTTPException(status_code=503, detail="SerpApi key is not configured in the backend.")

    roles = [role.strip() for role in request.target_roles if role.strip()]
    if not roles:
        raise HTTPException(status_code=422, detail="Add at least one target role.")

    quoted_roles = [f'"{role}"' for role in roles]
    query = "(" + " OR ".join(quoted_roles) + ")"
    arrangement = request.work_arrangement.casefold()
    if "remote" in arrangement and "hybrid" in arrangement:
        query += " (remote OR hybrid)"
    elif "remote" in arrangement:
        query += " remote"
    elif "hybrid" in arrangement:
        query += " hybrid"

    pages_needed = math.ceil(request.job_count / MAX_PAGE_SIZE)
    jobs: list[JobResult] = []
    searches_used = 0
    next_page_token: str | None = None
    seen: set[str] = set()

    timeout = httpx.Timeout(30.0, connect=8.0)
    async with httpx.AsyncClient(timeout=timeout) as client:
        for _ in range(pages_needed):
            params: dict[str, Any] = {
                "engine": "google_jobs",
                "q": query,
                "location": request.location,
                "gl": request.country_code.lower(),
                "hl": request.language,
                "api_key": api_key,
            }
            if next_page_token:
                params["next_page_token"] = next_page_token

            try:
                response = await client.get(SERPAPI_ENDPOINT, params=params)
                searches_used += 1
                response.raise_for_status()
                payload = response.json()
            except (httpx.HTTPError, ValueError) as exc:
                provider_error = None
                if isinstance(exc, httpx.HTTPStatusError):
                    try:
                        error_payload = exc.response.json()
                    except ValueError:
                        error_payload = None
                    if isinstance(error_payload, dict):
                        message = error_payload.get("error")
                        if isinstance(message, str) and message:
                            provider_error = message.replace(api_key, "[redacted]")
                # Provider error bodies are useful diagnostics, but must not expose the key.
                raise HTTPException(
                    status_code=502,
                    detail=(
                        f"SerpApi rejected the search: {provider_error}"
                        if provider_error
                        else "SerpApi search failed. Check the backend key, account quota, and provider status."
                    ),
                ) from exc

            if payload.get("error"):
                message = payload["error"]
                detail = (
                    f"SerpApi returned a search error: {message.replace(api_key, '[redacted]')}"
                    if isinstance(message, str) and message
                    else "SerpApi returned a search error."
                )
                raise HTTPException(status_code=502, detail=detail)

            for raw_job in payload.get("jobs_results", []):
                job = normalize_job(raw_job)
                if job is None or is_excluded(job, request.excluded_employers):
                    continue
                dedupe_key = job.job_id or "|".join(
                    [(job.title or "").casefold(), (job.company or "").casefold(), (job.location or "").casefold()]
                )
                if dedupe_key not in seen:
                    seen.add(dedupe_key)
                    jobs.append(job)

            next_page_token = (payload.get("serpapi_pagination") or {}).get("next_page_token")
            if len(jobs) >= request.job_count or not next_page_token:
                break

    warnings = [
        "Google Jobs does not provide a dedicated salary filter; compare salary manually and treat missing salary as not disclosed.",
        "Search results are not independently verified active vacancies. Open the employer posting to confirm location, eligibility, dates, and application status.",
        "Returned description text may be a snippet, not the complete original employer description.",
        "Client name, contact details, CV text, work authorization, salary target, and custom fields were not sent to SerpApi.",
    ]
    return JobSearchResponse(
        jobs=jobs[: request.job_count],
        searches_used=searches_used,
        requested_count=request.job_count,
        warnings=warnings,
    )


def normalize_job(raw: dict[str, Any]) -> JobResult | None:
    title = raw.get("title")
    if not title:
        return None
    detected = raw.get("detected_extensions") or {}
    apply_options = []
    for option in raw.get("apply_options") or []:
        if option.get("link"):
            apply_options.append(ApplyOption(title=option.get("title"), link=option["link"]))
    highlights = [
        JobHighlight(title=highlight.get("title"), items=highlight.get("items") or [])
        for highlight in (raw.get("job_highlights") or [])
    ]

    return JobResult(
        job_id=raw.get("job_id"),
        title=title,
        company=raw.get("company_name"),
        location=raw.get("location"),
        via=raw.get("via"),
        posted_at=detected.get("posted_at") or raw.get("posted_at"),
        salary_text=detected.get("salary") or raw.get("salary"),
        work_arrangement=(
            "Remote" if detected.get("work_from_home") else
            detected.get("schedule_type") or
            next((value for value in (raw.get("extensions") or []) if "hybrid" in value.casefold()), None)
        ),
        description=raw.get("description"),
        google_jobs_url=raw.get("share_link"),
        apply_options=apply_options,
        highlights=highlights,
    )


def is_excluded(job: JobResult, excluded_employers: list[str]) -> bool:
    company = (job.company or "").casefold()
    return any(employer.strip().casefold() in company for employer in excluded_employers if employer.strip())
