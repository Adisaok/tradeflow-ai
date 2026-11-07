from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.business import Business
from app.schemas.business import BusinessCreate, BusinessResponse

router = APIRouter(prefix="/businesses", tags=["businesses"])


@router.post(
    "",
    response_model=BusinessResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_business(
    payload: BusinessCreate,
    db: AsyncSession = Depends(get_db),
):
    business = Business(**payload.model_dump())
    db.add(business)
    await db.commit()
    await db.refresh(business)
    return business


@router.get("", response_model=list[BusinessResponse])
async def list_businesses(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Business).order_by(Business.created_at.desc())
    )
    return result.scalars().all()


@router.get("/{business_id}", response_model=BusinessResponse)
async def get_business(
    business_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    business = await db.get(Business, business_id)

    if business is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Business not found",
        )

    return business
