from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.core.security import get_current_active_user
from app.schemas.schemas import UserResponse, UserUpdate
from app.services.user_service import UserService

router = APIRouter()


@router.get("/me", response_model=UserResponse)
async def get_profile(
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    count = await UserService.get_prediction_count(db, current_user.id)
    current_user.total_predictions = count
    return current_user


@router.patch("/me", response_model=UserResponse)
async def update_profile(
    data: UserUpdate,
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    if data.email and data.email != current_user.email:
        existing = await UserService.get_user_by_email(db, data.email)
        if existing:
            raise HTTPException(status_code=400, detail="Email already in use")
    user = await UserService.update_user(db, current_user, data)
    return user
