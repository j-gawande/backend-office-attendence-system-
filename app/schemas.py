from pydantic import BaseModel, EmailStr, Field
from datetime import date as DateType
from typing import List

class EmployeeBase(BaseModel):
    employee_id: str = Field(..., min_length=1, max_length=50, description="User Employee ID (unique)")
    full_name: str = Field(..., min_length=1, max_length=100, description="Full name of the employee")
    email: EmailStr = Field(..., description="Email address of the employee")
    department: str = Field(..., min_length=1, max_length=100, description="Department of the employee")

class EmployeeCreate(EmployeeBase):
    pass

class EmployeeResponse(EmployeeBase):
    id: int
    class Config:
        from_attributes = True

class AttendanceBase(BaseModel):
    employee_id: str = Field(..., min_length=1, max_length=50, description="User Employee ID")
    date: DateType = Field(..., description="Date of attendance")
    is_present: bool = Field(..., description="True = Present, False = Absent")

class AttendanceCreate(AttendanceBase):
    pass

class AttendanceResponse(AttendanceBase):
    id: int
    class Config:
        from_attributes = True

class AttendanceSummary(BaseModel):
    employee_id: str
    full_name: str
    total_present_days: int
    total_absent_days: int
    class Config:
        from_attributes = True
