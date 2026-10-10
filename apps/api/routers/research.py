import uuid
from fastapi import APIRouter, status, Depends
from sqlalchemy.orm import Session

from apps.api.schemas.research import (
    JobAcceptedResponse,
    ResearchRequest,
)
from apps.api.dependencies.auth import get_current_user
from packages.db.database import get_db
from packages.db.models import ResearchJob, JobStatus

router = APIRouter()

@router.post(
    "/",
    response_model=JobAcceptedResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_research(
    request: ResearchRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> JobAcceptedResponse:
    job_id = uuid.uuid4()

    # Actually persist the job to the database to ensure architectural consistency
    new_job = ResearchJob(
        id=job_id,
        user_id=uuid.UUID(current_user["id"]),
        query=request.query,
        status=JobStatus.PENDING
    )
    db.add(new_job)
    db.commit()
    
    print(f"Added research job {job_id} to database queue")

    return JobAcceptedResponse(
        job_id=job_id,
        status="queued",
        message="Research job accepted",
    )