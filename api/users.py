from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, ConfigDict
from typing import List
from datetime import datetime

import database.users as db_users

class UserSchema(BaseModel):
    id: int
    user_id: int
    username: str | None = None 
    first_name: str | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

@router.get("/", response_model=List[UserSchema])
async def get_users():
    users_from_db = await db_users.get_all_users()
    return users_from_db


@router.get("/{user_id}", response_model=UserSchema)
async def get_user(user_id: int):
    user = await db_users.get_user_by_user_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
