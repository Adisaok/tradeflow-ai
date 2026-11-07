from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.business import Business
from app.models.vendor import Vendor
from app.schemas.vendor import VendorCreate, VendorResponse, VendorUpdate

router = APIRouter(
    prefix="/businesses/{business_id}/vendors",
    tags=["vendors"],
)


async def get_existing_business(
    business_id: UUID,
    db: AsyncSession,
) -> Business:
    business = await db.get(Business, business_id)

    if business is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Business not found",
        )

    return business


@router.post(
    "",
    response_model=VendorResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_vendor(
    business_id: UUID,
    payload: VendorCreate,
    db: AsyncSession = Depends(get_db),
):
    await get_existing_business(business_id, db)

    vendor = Vendor(
        business_id=business_id,
        **payload.model_dump(),
    )

    db.add(vendor)
    await db.commit()
    await db.refresh(vendor)

    return vendor


@router.get("", response_model=list[VendorResponse])
async def list_vendors(
    business_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    await get_existing_business(business_id, db)

    result = await db.execute(
        select(Vendor)
        .where(Vendor.business_id == business_id)
        .order_by(Vendor.created_at.desc())
    )

    return result.scalars().all()


@router.patch("/{vendor_id}", response_model=VendorResponse)
async def update_vendor(
    business_id: UUID,
    vendor_id: UUID,
    payload: VendorUpdate,
    db: AsyncSession = Depends(get_db),
):
    await get_existing_business(business_id, db)

    vendor = await db.scalar(
        select(Vendor).where(
            Vendor.id == vendor_id,
            Vendor.business_id == business_id,
        )
    )

    if vendor is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vendor not found",
        )

    updates = payload.model_dump(exclude_unset=True)

    for field, value in updates.items():
        setattr(vendor, field, value)

    await db.commit()
    await db.refresh(vendor)

    return vendor
