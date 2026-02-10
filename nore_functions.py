"""
HRMS Lite - Additional Functions
Utility functions for enhanced HRMS functionality
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any
import re

def generate_employee_id(department: str = None, existing_ids: List[str] = None) -> str:
    """Generate unique employee ID based on department"""
    
    dept_codes = {
        'Engineering': 'ENG',
        'Sales': 'SAL',
        'Marketing': 'MKT',
        'HR': 'HR',
        'Finance': 'FIN',
        'Operations': 'OPS'
    }
    
    code = dept_codes.get(department, 'EMP')
    
    # Find next available number
    max_num = 0
    if existing_ids:
        for emp_id in existing_ids:
            if emp_id.startswith(code):
                try:
                    num = int(emp_id[3:])
                    max_num = max(max_num, num)
                except:
                    continue
    
    next_num = max_num + 1
    
    return f"{code}{next_num:03d}"

def validate_employee_data(employee_data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate and clean employee data"""
    
    errors = []
    cleaned_data = employee_data.copy()
    
    # Validate employee_id
    emp_id = str(employee_data.get('employee_id', '')).strip()
    if not emp_id:
        errors.append('Employee ID is required')
    elif len(emp_id) > 20:
        errors.append('Employee ID too long (max 20 characters)')
    else:
        cleaned_data['employee_id'] = emp_id.upper()
    
    # Validate full_name
    full_name = str(employee_data.get('full_name', '')).strip()
    if not full_name:
        errors.append('Full name is required')
    elif len(full_name) > 100:
        errors.append('Full name too long (max 100 characters)')
    elif not re.match(r'^[a-zA-Z\s\-\.]+$', full_name):
        errors.append('Full name contains invalid characters')
    else:
        cleaned_data['full_name'] = full_name.title()
    
    # Validate email
    email = str(employee_data.get('email', '')).strip().lower()
    if not email:
        errors.append('Email is required')
    elif not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
        errors.append('Invalid email format')
    elif len(email) > 100:
        errors.append('Email too long (max 100 characters)')
    else:
        cleaned_data['email'] = email
    
    # Validate department
    department = str(employee_data.get('department', '')).strip()
    valid_departments = ['Engineering', 'Sales', 'Marketing', 'HR', 'Finance', 'Operations']
    
    if not department:
        errors.append('Department is required')
    elif department not in valid_departments:
        errors.append(f'Invalid department. Must be one of: {", ".join(valid_departments)}')
    else:
        cleaned_data['department'] = department
    
    return {
        'is_valid': len(errors) == 0,
        'errors': errors,
        'cleaned_data': cleaned_data
    }

def calculate_attendance_stats(attendances: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Calculate attendance statistics"""
    
    if not attendances:
        return {
            'total_days': 0,
            'present_days': 0,
            'absent_days': 0,
            'attendance_percentage': 0.0
        }
    
    total_days = len(attendances)
    present_days = len([a for a in attendances if a.get('status') == 'Present'])
    absent_days = total_days - present_days
    
    attendance_percentage = (present_days / total_days * 100) if total_days > 0 else 0.0
    
    return {
        'total_days': total_days,
        'present_days': present_days,
        'absent_days': absent_days,
        'attendance_percentage': round(attendance_percentage, 2)
    }

def get_monthly_attendance(attendances: List[Dict[str, Any]], year: int, month: int) -> List[Dict[str, Any]]:
    """Filter attendance for specific month and year"""
    
    filtered_attendances = []
    for attendance in attendances:
        attendance_date = datetime.strptime(attendance['date'], '%Y-%m-%d')
        if attendance_date.year == year and attendance_date.month == month:
            filtered_attendances.append(attendance)
    
    return filtered_attendances

def export_attendance_report(attendances: List[Dict[str, Any]], format: str = 'csv') -> str:
    """Export attendance data in different formats"""
    
    if format.lower() == 'csv':
        return export_to_csv(attendances)
    elif format.lower() == 'json':
        return export_to_json(attendances)
    else:
        raise ValueError(f'Unsupported export format: {format}')

def export_to_csv(attendances: List[Dict[str, Any]]) -> str:
    """Export attendance data to CSV format"""
    
    if not attendances:
        return 'No attendance data available'
    
    csv_lines = ['Employee ID,Employee Name,Date,Status']
    
    for attendance in attendances:
        line = f"{attendance.get('employee_id', '')},{attendance.get('employee_name', '')},{attendance.get('date', '')},{attendance.get('status', '')}"
        csv_lines.append(line)
    
    return '\n'.join(csv_lines)

def export_to_json(attendances: List[Dict[str, Any]]) -> str:
    """Export attendance data to JSON format"""
    
    import json
    return json.dumps(attendances, indent=2, default=str)

def get_department_summary(employees: List[Dict[str, Any]], attendances: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Get department-wise employee and attendance summary"""
    
    # Count employees by department
    dept_counts = {}
    for emp in employees:
        dept = emp.get('department', 'Unknown')
        dept_counts[dept] = dept_counts.get(dept, 0) + 1
    
    # Count attendance by department
    attendance_by_dept = {}
    for attendance in attendances:
        # Find employee's department
        emp_dept = None
        for emp in employees:
            if emp['id'] == attendance['employee_id']:
                emp_dept = emp.get('department', 'Unknown')
                break
        
        if emp_dept:
            if emp_dept not in attendance_by_dept:
                attendance_by_dept[emp_dept] = {'present': 0, 'absent': 0}
            
            if attendance['status'] == 'Present':
                attendance_by_dept[emp_dept]['present'] += 1
            else:
                attendance_by_dept[emp_dept]['absent'] += 1
    
    # Combine data
    summary = {}
    for dept in dept_counts:
        summary[dept] = {
            'employee_count': dept_counts[dept],
            'attendance_present': attendance_by_dept.get(dept, {}).get('present', 0),
            'attendance_absent': attendance_by_dept.get(dept, {}).get('absent', 0),
            'total_attendance': attendance_by_dept.get(dept, {}).get('present', 0) + attendance_by_dept.get(dept, {}).get('absent', 0)
        }
    
    return summary

def calculate_overtime(attendances: List[Dict[str, Any]], standard_hours: int = 8) -> Dict[str, Any]:
    """Calculate overtime based on attendance patterns"""
    
    # This is a placeholder for future enhancement
    # In a real system, you'd track check-in/check-out times
    
    return {
        'total_days': len(attendances),
        'present_days': len([a for a in attendances if a.get('status') == 'Present']),
        'potential_overtime_days': len([a for a in attendances if a.get('status') == 'Present']),
        'standard_hours_per_day': standard_hours,
        'total_standard_hours': len([a for a in attendances if a.get('status') == 'Present']) * standard_hours
    }

def generate_employee_report(employee: Dict[str, Any], attendances: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Generate comprehensive employee report"""
    
    stats = calculate_attendance_stats(attendances)
    
    # Get recent attendance (last 10 days)
    recent_attendance = sorted(attendances, key=lambda x: x.get('date', ''), reverse=True)[:10]
    
    # Calculate monthly attendance for current month
    current_date = datetime.now()
    monthly_attendance = get_monthly_attendance(
        attendances, 
        current_date.year, 
        current_date.month
    )
    monthly_stats = calculate_attendance_stats(monthly_attendance)
    
    return {
        'employee_info': employee,
        'overall_stats': stats,
        'monthly_stats': monthly_stats,
        'recent_attendance': recent_attendance,
        'report_generated': datetime.now().isoformat()
    }

def validate_attendance_data(attendance_data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate attendance data"""
    
    errors = []
    cleaned_data = attendance_data.copy()
    
    # Validate employee_id
    if not attendance_data.get('employee_id'):
        errors.append('Employee ID is required')
    
    # Validate date
    date_str = str(attendance_data.get('date', ''))
    try:
        attendance_date = datetime.strptime(date_str, '%Y-%m-%d')
        if attendance_date > datetime.now():
            errors.append('Date cannot be in the future')
        cleaned_data['date'] = date_str
    except ValueError:
        errors.append('Invalid date format. Use YYYY-MM-DD')
    
    # Validate status
    status = str(attendance_data.get('status', '')).strip()
    if status not in ['Present', 'Absent']:
        errors.append('Status must be either "Present" or "Absent"')
    else:
        cleaned_data['status'] = status
    
    return {
        'is_valid': len(errors) == 0,
        'errors': errors,
        'cleaned_data': cleaned_data
    }

def search_employees(employees: List[Dict[str, Any]], query: str) -> List[Dict[str, Any]]:
    """Search employees by name, ID, or email"""
    
    if not query:
        return employees
    
    query_lower = query.lower()
    results = []
    
    for emp in employees:
        # Search in employee_id
        if query_lower in emp.get('employee_id', '').lower():
            results.append(emp)
            continue
        
        # Search in full_name
        if query_lower in emp.get('full_name', '').lower():
            results.append(emp)
            continue
        
        # Search in email
        if query_lower in emp.get('email', '').lower():
            results.append(emp)
            continue
        
        # Search in department
        if query_lower in emp.get('department', '').lower():
            results.append(emp)
    
    # Remove duplicates and return
    return list({emp['id']: emp for emp in results}.values())
