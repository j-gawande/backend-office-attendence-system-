from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import and_
from typing import List, Optional
from datetime import date
from ..database import get_db
from ..models import Employee, Attendance
from ..schemas import AttendanceCreate, AttendanceResponse

router = APIRouter(prefix="/api/attendance", tags=["Attendance"])

@router.post("", response_model=AttendanceResponse, status_code=status.HTTP_201_CREATED)
def mark_attendance(attendance: AttendanceCreate, db: Session = Depends(get_db)):
    """
    Mark attendance for an employee.

    Request body uses:
    - employee_id (string, user Employee ID)
    - date
    - is_present (bool)
    """
    employee = db.query(Employee).filter(Employee.employee_id == attendance.employee_id).first()
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee with ID {attendance.employee_id} not found",
        )

    existing = (
        db.query(Attendance)
        .filter(
            and_(
                Attendance.employee_id == attendance.employee_id,
                Attendance.date == attendance.date,
            )
        )
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                f"Attendance for employee {attendance.employee_id} "
                f"on date {attendance.date} already exists"
            ),
        )

    try:
        db_attendance = Attendance(
            employee_id=attendance.employee_id,
            date=attendance.date,
            is_present=attendance.is_present,
        )
        db.add(db_attendance)
        db.commit()
        db.refresh(db_attendance)
        return AttendanceResponse(
            id=db_attendance.id,
            employee_id=db_attendance.employee_id,
            date=db_attendance.date,
            is_present=db_attendance.is_present,
        )
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Attendance record already exists for this employee and date",
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error creating attendance record: {str(e)}",
        )

@router.get("", response_model=List[AttendanceResponse])
def list_attendance(
    date: Optional[date] = Query(None, description="Filter by date (YYYY-MM-DD)"),
    employee_id: Optional[str] = Query(None, description="Filter by user Employee ID"),
    db: Session = Depends(get_db),
):
    """
    List attendance records with optional filters.
    """
    query = db.query(Attendance)

    if date:
        query = query.filter(Attendance.date == date)
    if employee_id:
        query = query.filter(Attendance.employee_id == employee_id)

    records = query.order_by(Attendance.date.desc()).all()
    return [
        AttendanceResponse(
            id=r.id,
            employee_id=r.employee_id,
            date=r.date,
            is_present=r.is_present,
        )
        for r in records
    ]
