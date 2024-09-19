# filename: backend/app/crud/crud_time_period.py

from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from backend.app.models.time_period import TimePeriodModel
from backend.app.core.config import TimePeriod
from backend.app.services.logging_service import logger

def create_time_period_in_db(db: Session, time_period: TimePeriod) -> TimePeriodModel:
    try:
        db_time_period = TimePeriodModel(id=time_period.value, name=time_period.name.lower())
        db.add(db_time_period)
        db.commit()
        db.refresh(db_time_period)
        return db_time_period
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error creating time period: {str(e)}")
        raise

def read_time_period_from_db(db: Session, time_period_id: int) -> Optional[TimePeriodModel]:
    return db.query(TimePeriodModel).filter(TimePeriodModel.id == time_period_id).first()

def read_all_time_periods_from_db(db: Session) -> List[TimePeriodModel]:
    return db.query(TimePeriodModel).all()

def update_time_period_in_db(db: Session, time_period_id: int, new_name: str) -> Optional[TimePeriodModel]:
    try:
        db_time_period = db.query(TimePeriodModel).filter(TimePeriodModel.id == time_period_id).first()
        if db_time_period:
            db_time_period.name = new_name
            db.commit()
            db.refresh(db_time_period)
        return db_time_period
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error updating time period: {str(e)}")
        raise

def delete_time_period_from_db(db: Session, time_period_id: int) -> bool:
    try:
        db_time_period = db.query(TimePeriodModel).filter(TimePeriodModel.id == time_period_id).first()
        if db_time_period:
            db.delete(db_time_period)
            db.commit()
            return True
        return False
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error deleting time period: {str(e)}")
        raise

def init_time_periods_in_db(db: Session) -> None:
    try:
        existing_periods = read_all_time_periods_from_db(db)
        existing_ids = {period.id for period in existing_periods}

        for time_period in TimePeriod:
            if time_period.value not in existing_ids:
                create_time_period_in_db(db, time_period)
        
        logger.info("Time periods initialized successfully")
    except SQLAlchemyError as e:
        logger.error(f"Error initializing time periods: {str(e)}")
        raise