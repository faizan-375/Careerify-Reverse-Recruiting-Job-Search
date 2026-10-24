from pydantic import BaseModel, Field


class JobSearchRequest(BaseModel):
    target_roles: list[str] = Field(min_length=1, max_length=20)
    location: str = Field(min_length=2, max_length=120)
    country_code: str = Field(default="us", min_length=2, max_length=2, pattern=r"^[A-Za-z]{2}$")
    language: str = Field(default="en", min_length=2, max_length=8)
    work_arrangement: str = "Remote or Hybrid"
    excluded_employers: list[str] = Field(default_factory=list)
    job_count: int = Field(default=10, ge=1, le=50)


class ApplyOption(BaseModel):
    title: str | None = None
    link: str


class JobHighlight(BaseModel):
    title: str | None = None
    items: list[str] = Field(default_factory=list)


class JobResult(BaseModel):
    job_id: str | None = None
    title: str
    company: str | None = None
    location: str | None = None
    via: str | None = None
    posted_at: str | None = None
    salary_text: str | None = None
    work_arrangement: str | None = None
    description: str | None = None
    google_jobs_url: str | None = None
    apply_options: list[ApplyOption] = Field(default_factory=list)
    highlights: list[JobHighlight] = Field(default_factory=list)


class JobSearchResponse(BaseModel):
    jobs: list[JobResult]
    searches_used: int
    requested_count: int
    warnings: list[str]
