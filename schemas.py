from typing import Optional

from pydantic import BaseModel


class UserCreate(BaseModel):
    username: str

    height_cm: Optional[float] = None
    bust_cm: Optional[float] = None
    waist_cm: Optional[float] = None
    hip_cm: Optional[float] = None

    preferred_fit: Optional[str] = None
    preferred_colors: Optional[str] = None
    style_preferences: Optional[str] = None


class UserResponse(UserCreate):
    id: int

    class Config:
        from_attributes = True


class TryOnCreate(BaseModel):
    user_id: Optional[int] = None

    garment_name: Optional[str] = None

    person_image: Optional[str] = None
    garment_image: Optional[str] = None
    result_image: Optional[str] = None

    style_score: Optional[float] = None
    occasion: Optional[str] = None


class TryOnResponse(TryOnCreate):
    id: int

    class Config:
        from_attributes = True