from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func, and_
from typing import List, Optional
from datetime import date
from ..database import get_db
from ..models import Employee, Attendance
from ..schemas import (
    EmployeeCreate,
    EmployeeResponse,
    AttendanceResponse,
    AttendanceSummary,
)

router = APIRouter(prefix="/api/employees", tags=["Employees"])

@router.post("", response_model=EmployeeResponse, status_code=status.HTTP_201_CREATED)
def create_employee(employee: EmployeeCreate, db: Session = Depends(get_db)):
    """
    Create a new employee.

    Validations:
    - All fields required
    - employee_id unique
    - email unique and valid
    """
    try:
        if db.query(Employee).filter(Employee.employee_id == employee.employee_id).first():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Employee ID already exists",
            )
        if db.query(Employee).filter(Employee.email == employee.email).first():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already exists",
            )
        db_employee = Employee(
            employee_id=employee.employee_id,
            full_name=employee.full_name,
            email=employee.email,
            department=employee.department,
        )
        db.add(db_employee)
        db.commit()
        db.refresh(db_employee)
        return db_employee
    except HTTPException:
        raise
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid data provided",
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error creating employee: {str(e)}",
        )

@router.get("", response_model=List[EmployeeResponse])
def list_employees(db: Session = Depends(get_db)):
    """List all employees."""
    return db.query(Employee).all()

@router.get("/{employee_id}", response_model=EmployeeResponse)
def get_employee(employee_id: str, db: Session = Depends(get_db)):
    """
    Get a single employee by user Employee ID.
    """
    employee = db.query(Employee).filter(Employee.employee_id == employee_id).first()
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee with ID {employee_id} not found",
        )
    return employee

@router.delete("/{employee_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_employee(employee_id: str, db: Session = Depends(get_db)):
    """
    Delete an employee by user Employee ID.

    Cascades to attendance records via FK.
    """
    employee = db.query(Employee).filter(Employee.employee_id == employee_id).first()
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee with ID {employee_id} not found",
        )

    db.delete(employee)
    db.commit()
    return None

@router.get("/{employee_id}/attendance", response_model=List[AttendanceResponse])
def get_employee_attendance(
    employee_id: str,
    start_date: Optional[date] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="End date (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
):
    """
    Get attendance records for a specific employee by user Employee ID.
    """
    employee = db.query(Employee).filter(Employee.employee_id == employee_id).first()
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee with ID {employee_id} not found",
        )

    query = db.query(Attendance).filter(Attendance.employee_id == employee_id)

    if start_date:
        query = query.filter(Attendance.date >= start_date)
    if end_date:
        query = query.filter(Attendance.date <= end_date)

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

@router.get("/{employee_id}/attendance/summary", response_model=AttendanceSummary)
def get_attendance_summary(employee_id: str, db: Session = Depends(get_db)):
    """
    Get attendance summary (total present/absent days) for an employee.
    """
    employee = db.query(Employee).filter(Employee.employee_id == employee_id).first()
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee with ID {employee_id} not found",
        )

    present_count = (
        db.query(func.count(Attendance.id))
        .filter(
            and_(
                Attendance.employee_id == employee_id,
                Attendance.is_present.is_(True),
            )
        )
        .scalar()
        or 0
    )

    absent_count = (
        db.query(func.count(Attendance.id))
        .filter(
            and_(
                Attendance.employee_id == employee_id,
                Attendance.is_present.is_(False),
            )
        )
        .scalar()
        or 0
    )

    return AttendanceSummary(
        employee_id=employee.employee_id,
        full_name=employee.full_name,
        total_present_days=present_count,
        total_absent_days=absent_count,
    )
