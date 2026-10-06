from uuid import uuid4

from fastapi import APIRouter, status

from apps.api.schemas.research import (
    JobAcceptedResponse,
    ResearchRequest,
)


router = APIRouter()


@router.post(
    "/",
    response_model=JobAcceptedResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
def create_research(request: ResearchRequest) -> JobAcceptedResponse:
    job_id = uuid4()

    print(f"Adding research job {job_id} to queue")

    return JobAcceptedResponse(
        job_id=job_id,
        status="queued",
        message="Research job accepted",
    )