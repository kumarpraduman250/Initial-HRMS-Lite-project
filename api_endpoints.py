"""
HRMS Lite - Additional API Endpoints
Extended API endpoints for enhanced functionality
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, date
from pydantic import BaseModel
import re

from .main import get_db
from .nore_functions import (
    generate_employee_id,
    validate_employee_data,
    calculate_attendance_stats,
    get_monthly_attendance,
    export_attendance_report,
    get_department_summary,
    generate_employee_report,
    validate_attendance_data,
    search_employees
)

router = APIRouter(prefix="/api/v2", tags=["Extended Features"])

# Pydantic models for extended endpoints
class EmployeeSearchRequest(BaseModel):
    query: str = ""
    department: Optional[str] = None
    limit: int = 50

class EmployeeStatsResponse(BaseModel):
    employee_id: str
    full_name: str
    department: str
    total_days: int
    present_days: int
    absent_days: int
    attendance_percentage: float

class DepartmentStatsResponse(BaseModel):
    department: str
    employee_count: int
    present_count: int
    absent_count: int
    total_attendance: int

class AttendanceReportRequest(BaseModel):
    format: str = "csv"  # csv, json
    employee_id: Optional[int] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None

class BulkAttendanceRequest(BaseModel):
    employee_ids: List[int]
    date: date
    status: str  # Present or Absent

@router.post("/employees/generate-id")
def generate_employee_id_endpoint(
    department: str = Query(..., description="Department name"),
    db: Session = Depends(get_db)
):
    """Generate next available employee ID for a department"""
    
    # Get existing employee IDs
    from .main import Employee
    existing_ids = [emp.employee_id for emp in db.query(Employee).all()]
    
    new_id = generate_employee_id(department, existing_ids)
    
    return {
        "employee_id": new_id,
        "department": department,
        "status": "generated"
    }

@router.get("/employees/search")
def search_employees_endpoint(
    query: str = Query("", description="Search query"),
    department: Optional[str] = Query(None, description="Filter by department"),
    limit: int = Query(50, description="Maximum results to return"),
    db: Session = Depends(get_db)
):
    """Search employees by name, ID, email, or department"""
    
    from .main import Employee
    
    # Get all employees
    employees = db.query(Employee).all()
    employee_dicts = [
        {
            "id": emp.id,
            "employee_id": emp.employee_id,
            "full_name": emp.full_name,
            "email": emp.email,
            "department": emp.department
        }
        for emp in employees
    ]
    
    # Apply search and filters
    filtered_employees = search_employees(employee_dicts, query)
    
    if department:
        filtered_employees = [
            emp for emp in filtered_employees 
            if emp.get('department', '').lower() == department.lower()
        ]
    
    # Apply limit
    filtered_employees = filtered_employees[:limit]
    
    return {
        "query": query,
        "department": department,
        "results": filtered_employees,
        "total": len(filtered_employees)
    }

@router.get("/employees/{employee_id}/stats")
def get_employee_stats(
    employee_id: int,
    db: Session = Depends(get_db)
):
    """Get comprehensive statistics for an employee"""
    
    from .main import Employee, Attendance
    
    # Get employee
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    # Get attendance records
    attendances = db.query(Attendance).filter(Attendance.employee_id == employee_id).all()
    attendance_dicts = [
        {
            "date": att.date.isoformat(),
            "status": att.status
        }
        for att in attendances
    ]
    
    # Calculate statistics
    stats = calculate_attendance_stats(attendance_dicts)
    
    return {
        "employee": {
            "id": employee.id,
            "employee_id": employee.employee_id,
            "full_name": employee.full_name,
            "email": employee.email,
            "department": employee.department
        },
        "statistics": stats
    }

@router.get("/employees/{employee_id}/report")
def get_employee_report_endpoint(
    employee_id: int,
    db: Session = Depends(get_db)
):
    """Generate comprehensive employee report"""
    
    from .main import Employee, Attendance
    
    # Get employee
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    # Get attendance records
    attendances = db.query(Attendance).filter(Attendance.employee_id == employee_id).all()
    attendance_dicts = [
        {
            "date": att.date.isoformat(),
            "status": att.status
        }
        for att in attendances
    ]
    
    # Generate report
    report = generate_employee_report(
        {
            "id": employee.id,
            "employee_id": employee.employee_id,
            "full_name": employee.full_name,
            "email": employee.email,
            "department": employee.department
        },
        attendance_dicts
    )
    
    return report

@router.get("/departments/stats")
def get_department_stats(db: Session = Depends(get_db)):
    """Get department-wise statistics"""
    
    from .main import Employee, Attendance
    
    # Get all data
    employees = db.query(Employee).all()
    attendances = db.query(Attendance).all()
    
    employee_dicts = [
        {
            "id": emp.id,
            "department": emp.department
        }
        for emp in employees
    ]
    
    attendance_dicts = [
        {
            "employee_id": att.employee_id,
            "status": att.status
        }
        for att in attendances
    ]
    
    # Calculate summary
    summary = get_department_summary(employee_dicts, attendance_dicts)
    
    return {
        "summary": summary,
        "generated_at": datetime.now().isoformat()
    }

@router.get("/attendance/monthly")
def get_monthly_attendance_endpoint(
    year: int = Query(..., description="Year"),
    month: int = Query(..., description="Month (1-12)"),
    employee_id: Optional[int] = Query(None, description="Filter by employee"),
    db: Session = Depends(get_db)
):
    """Get monthly attendance data"""
    
    from .main import Employee, Attendance
    
    # Base query
    query = db.query(Attendance)
    
    # Apply employee filter if provided
    if employee_id:
        query = query.filter(Attendance.employee_id == employee_id)
    
    # Get all attendances
    attendances = query.all()
    attendance_dicts = [
        {
            "employee_id": att.employee_id,
            "date": att.date.isoformat(),
            "status": att.status
        }
        for att in attendances
    ]
    
    # Filter by month
    monthly_attendance = get_monthly_attendance(attendance_dicts, year, month)
    
    # Add employee names
    if monthly_attendance:
        employee_ids = list(set([att['employee_id'] for att in monthly_attendance]))
        employees = db.query(Employee).filter(Employee.id.in_(employee_ids)).all()
        employee_map = {emp.id: emp.full_name for emp in employees}
        
        for att in monthly_attendance:
            att['employee_name'] = employee_map.get(att['employee_id'], 'Unknown')
    
    return {
        "year": year,
        "month": month,
        "attendance_records": monthly_attendance,
        "total_records": len(monthly_attendance)
    }

@router.post("/attendance/bulk")
def mark_bulk_attendance(
    bulk_request: BulkAttendanceRequest,
    db: Session = Depends(get_db)
):
    """Mark attendance for multiple employees at once"""
    
    from .main import Employee, Attendance
    
    results = []
    errors = []
    
    for employee_id in bulk_request.employee_ids:
        # Validate employee exists
        employee = db.query(Employee).filter(Employee.id == employee_id).first()
        if not employee:
            errors.append(f"Employee ID {employee_id} not found")
            continue
        
        # Check for duplicate
        existing = db.query(Attendance).filter(
            Attendance.employee_id == employee_id,
            Attendance.date == bulk_request.date
        ).first()
        
        if existing:
            errors.append(f"Attendance already marked for employee {employee_id} on {bulk_request.date}")
            continue
        
        # Create attendance record
        attendance = Attendance(
            employee_id=employee_id,
            date=bulk_request.date,
            status=bulk_request.status
        )
        db.add(attendance)
        results.append({
            "employee_id": employee_id,
            "status": "marked"
        })
    
    if errors:
        db.rollback()
        raise HTTPException(status_code=400, detail={"errors": errors})
    else:
        db.commit()
    
    return {
        "date": bulk_request.date.isoformat(),
        "status": bulk_request.status,
        "marked_employees": len(results),
        "results": results
    }

@router.post("/reports/attendance")
def export_attendance_endpoint(
    request: AttendanceReportRequest,
    db: Session = Depends(get_db)
):
    """Export attendance data in various formats"""
    
    from .main import Employee, Attendance
    
    # Build query
    query = db.query(Attendance)
    
    # Apply filters
    if request.employee_id:
        query = query.filter(Attendance.employee_id == request.employee_id)
    
    if request.start_date:
        query = query.filter(Attendance.date >= request.start_date)
    
    if request.end_date:
        query = query.filter(Attendance.date <= request.end_date)
    
    # Get data
    attendances = query.all()
    
    # Add employee information
    employee_ids = list(set([att.employee_id for att in attendances]))
    employees = db.query(Employee).filter(Employee.id.in_(employee_ids)).all()
    employee_map = {emp.id: emp for emp in employees}
    
    attendance_data = []
    for att in attendances:
        employee = employee_map.get(att.employee_id)
        attendance_data.append({
            "employee_id": employee.employee_id if employee else "Unknown",
            "employee_name": employee.full_name if employee else "Unknown",
            "date": att.date.isoformat(),
            "status": att.status
        })
    
    # Export data
    try:
        exported_data = export_attendance_report(attendance_data, request.format)
        
        return {
            "format": request.format,
            "records_count": len(attendance_data),
            "data": exported_data,
            "exported_at": datetime.now().isoformat()
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/dashboard/stats")
def get_dashboard_stats(db: Session = Depends(get_db)):
    """Get dashboard statistics"""
    
    from .main import Employee, Attendance
    
    # Employee statistics
    total_employees = db.query(Employee).count()
    
    # Department breakdown
    dept_counts = {}
    for dept in ['Engineering', 'Sales', 'Marketing', 'HR', 'Finance', 'Operations']:
        count = db.query(Employee).filter(Employee.department == dept).count()
        dept_counts[dept] = count
    
    # Today's attendance
    today = date.today()
    today_attendance = db.query(Attendance).filter(Attendance.date == today).all()
    present_today = len([att for att in today_attendance if att.status == 'Present'])
    absent_today = len([att for att in today_attendance if att.status == 'Absent'])
    
    # This week's attendance
    from datetime import timedelta
    week_start = today - timedelta(days=today.weekday())
    week_attendance = db.query(Attendance).filter(Attendance.date >= week_start).all()
    present_week = len([att for att in week_attendance if att.status == 'Present'])
    
    return {
        "employees": {
            "total": total_employees,
            "by_department": dept_counts
        },
        "attendance_today": {
            "date": today.isoformat(),
            "present": present_today,
            "absent": absent_today,
            "total": present_today + absent_today
        },
        "attendance_this_week": {
            "present": present_week,
            "total": len(week_attendance),
            "percentage": round((present_week / len(week_attendance)) * 100, 2) if week_attendance else 0
        },
        "generated_at": datetime.now().isoformat()
    }
