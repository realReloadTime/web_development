from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class BookingBase(BaseModel):
    user_id: int
    book_id: int
    take_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


class BookingDefault(BookingBase):
    pass


class BookingFull(BookingBase):
    id: int

    class Config:
        from_attributes = True


class BookingComplete(BaseModel):
    end_date: datetime = Field(default_factory=datetime.now)
