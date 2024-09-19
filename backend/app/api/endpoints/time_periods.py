# filename: backend/app/api/endpoints/time_periods.py

from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.crud import crud_time_period
from backend.app.schemas.time_period import TimePeriodSchema
from backend.app.db.session import get_db
from backend.app.core.config import TimePeriod

router = APIRouter()

@router.get("/time-periods/", response_model=List[TimePeriodSchema])
def read_time_periods(db: Session = Depends(get_db)):
    return crud_time_period.read_all_time_periods_from_db(db)

@router.get("/time-periods/{time_period_id}", response_model=TimePeriodSchema)
def read_time_period(time_period_id: int, db: Session = Depends(get_db)):
    db_time_period = crud_time_period.read_time_period_from_db(db, time_period_id)
    if db_time_period is None:
        raise HTTPException(status_code=404, detail="Time period not found")
    return db_time_period

@router.post("/time-periods/", response_model=TimePeriodSchema)
def create_time_period(time_period: TimePeriod, db: Session = Depends(get_db)):
    return crud_time_period.create_time_period_in_db(db, time_period)

@router.put("/time-periods/{time_period_id}", response_model=TimePeriodSchema)
def update_time_period(time_period_id: int, new_name: str, db: Session = Depends(get_db)):
    db_time_period = crud_time_period.update_time_period_in_db(db, time_period_id, new_name)
    if db_time_period is None:
        raise HTTPException(status_code=404, detail="Time period not found")
    return db_time_period

@router.delete("/time-periods/{time_period_id}", response_model=bool)
def delete_time_period(time_period_id: int, db: Session = Depends(get_db)):
    success = crud_time_period.delete_time_period_from_db(db, time_period_id)
    if not success:
        raise HTTPException(status_code=404, detail="Time period not found")
    return success