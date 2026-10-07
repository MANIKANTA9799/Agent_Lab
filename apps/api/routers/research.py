from uuid import uuid4

from fastapi import APIRouter, status
from fastapi import Depends
from apps.api.schemas.research import (
    JobAcceptedResponse,
    ResearchRequest,
)
from apps.api.dependencies.auth import get_current_user

router = APIRouter()


@router.post(
    "/",
    response_model=JobAcceptedResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
def create_research(
    request: ResearchRequest,
    current_user: dict = Depends(get_current_user),
) -> JobAcceptedResponse:
    job_id = uuid4()

    print(f"Adding research job {job_id} to queue")

    return JobAcceptedResponse(
        job_id=job_id,
        status="queued",
        message="Research job accepted",
    )