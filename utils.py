"""
HRMS Lite - Utility Functions
Common utility functions for the application
"""

import os
import json
import csv
import io
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import hashlib
import secrets
import base64

def load_config():
    """Load configuration from environment variables or defaults"""
    
    return {
        'database_url': os.getenv('DATABASE_URL', 'sqlite:///./hrms.db'),
        'secret_key': os.getenv('SECRET_KEY', secrets.token_urlsafe(32)),
        'debug': os.getenv('DEBUG', 'False').lower() == 'true',
        'cors_origins': os.getenv('CORS_ORIGINS', '*').split(','),
        'log_level': os.getenv('LOG_LEVEL', 'INFO'),
        'rate_limit': int(os.getenv('RATE_LIMIT', '100')),
        'cache_ttl': int(os.getenv('CACHE_TTL', '300'))
    }

def format_error_response(error: Exception, include_traceback: bool = False) -> Dict[str, Any]:
    """Format error responses consistently"""
    
    error_response = {
        'error': True,
        'message': str(error),
        'timestamp': datetime.now().isoformat()
    }
    
    if include_traceback and os.getenv('DEBUG', 'False').lower() == 'true':
        import traceback
        error_response['traceback'] = traceback.format_exc()
    
    return error_response

def validate_date_range(start_date: str, end_date: str) -> Dict[str, Any]:
    """Validate date range for reports"""
    
    try:
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')
        
        if start > end:
            return {
                'valid': False,
                'error': 'Start date cannot be after end date'
            }
        
        # Check if range is too large (more than 1 year)
        if (end - start).days > 365:
            return {
                'valid': False,
                'error': 'Date range cannot exceed 1 year'
            }
        
        return {
            'valid': True,
            'start_date': start_date,
            'end_date': end_date,
            'days_count': (end - start).days + 1
        }
        
    except ValueError as e:
        return {
            'valid': False,
            'error': f'Invalid date format: {str(e)}'
        }

def generate_csv(data: List[Dict[str, Any]], filename: str = None) -> str:
    """Generate CSV file from data"""
    
    if not data:
        return ''
    
    output = io.StringIO()
    if data:
        fieldnames = data[0].keys()
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)
    
    return output.getvalue()

def generate_excel_report(data: List[Dict[str, Any]], filename: str = None) -> bytes:
    """Generate Excel-like HTML report"""
    
    if not data:
        return b'<html><body><p>No data available</p></body></html>'
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>HRMS Report</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            table {{ border-collapse: collapse; width: 100%; }}
            th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
            th {{ background-color: #f2f2f2; font-weight: bold; }}
            .header {{ font-size: 24px; margin-bottom: 20px; color: #333; }}
            .summary {{ background-color: #f9f9f9; padding: 15px; margin: 20px 0; border-radius: 5px; }}
        </style>
    </head>
    <body>
        <div class="header">HRMS Lite Report</div>
        
        <div class="summary">
            <h3>Summary</h3>
            <p>Total Records: {len(data)}</p>
            <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
        
        <table>
            <thead>
                <tr>
                    <th>Employee ID</th>
                    <th>Name</th>
                    <th>Date</th>
                    <th>Status</th>
                </tr>
            </thead>
            <tbody>
    """
    
    for item in data:
        html += f"""
                <tr>
                    <td>{item.get('employee_id', '')}</td>
                    <td>{item.get('employee_name', '')}</td>
                    <td>{item.get('date', '')}</td>
                    <td>{item.get('status', '')}</td>
                </tr>
        """
    
    html += """
            </tbody>
        </table>
    </body>
    </html>
    """
    
    return html.encode('utf-8')

def calculate_working_days(start_date: datetime, end_date: datetime) -> int:
    """Calculate working days between two dates (excluding weekends)"""
    
    working_days = 0
    current_date = start_date
    
    while current_date <= end_date:
        # Monday to Friday are working days (0-4)
        if current_date.weekday() < 5:
            working_days += 1
        current_date += timedelta(days=1)
    
    return working_days

def get_holidays(year: int) -> List[datetime]:
    """Get list of holidays for a given year"""
    
    # This is a placeholder - in a real system, 
    # you'd fetch from a database or API
    holidays = []
    
    # Add some common holidays (example)
    common_holidays = [
        f"{year}-01-01",  # New Year
        f"{year}-12-25",  # Christmas
        f"{year}-07-04",  # Independence Day (US)
        f"{year}-05-01",  # Labor Day (US)
    ]
    
    for holiday_str in common_holidays:
        try:
            holidays.append(datetime.strptime(holiday_str, '%Y-%m-%d'))
        except ValueError:
            continue
    
    return holidays

def is_holiday(date: datetime, holidays: List[datetime] = None) -> bool:
    """Check if a given date is a holiday"""
    
    if holidays is None:
        holidays = get_holidays(date.year)
    
    return date in holidays

def hash_password(password: str) -> str:
    """Hash password using SHA-256"""
    
    return hashlib.sha256(password.encode()).hexdigest()

def generate_api_key() -> str:
    """Generate a secure API key"""
    
    return secrets.token_urlsafe(32)

def validate_api_key(api_key: str, secret_key: str) -> bool:
    """Validate API key against secret"""
    
    try:
        decoded = base64.urlsafe_b64decode(api_key)
        return secrets.compare_digest(decoded, secret_key)
    except Exception:
        return False

def format_currency(amount: float, currency: str = 'USD') -> str:
    """Format amount as currency"""
    
    return f"{currency} {amount:,.2f}"

def calculate_overtime_hours(
    check_in: datetime, 
    check_out: datetime, 
    standard_hours: float = 8.0
) -> float:
    """Calculate overtime hours based on check-in/check-out times"""
    
    if not check_in or not check_out:
        return 0.0
    
    # Calculate total hours
    total_hours = (check_out - check_in).total_seconds() / 3600.0
    
    # Overtime is hours beyond standard
    overtime = max(0.0, total_hours - standard_hours)
    
    return round(overtime, 2)

def get_attendance_trends(
    attendances: List[Dict[str, Any]], 
    days: int = 30
) -> Dict[str, Any]:
    """Analyze attendance trends over specified period"""
    
    if not attendances:
        return {
            'trend': 'no_data',
            'message': 'No attendance data available'
        }
    
    # Sort by date
    sorted_attendances = sorted(attendances, key=lambda x: x.get('date', ''))
    
    # Take last N days
    recent_attendances = sorted_attendances[-days:]
    
    # Calculate daily statistics
    daily_stats = {}
    for attendance in recent_attendances:
        date = attendance.get('date', '')
        if date not in daily_stats:
            daily_stats[date] = {'present': 0, 'absent': 0}
        
        if attendance.get('status') == 'Present':
            daily_stats[date]['present'] += 1
        else:
            daily_stats[date]['absent'] += 1
    
    # Calculate trend
    total_days = len(daily_stats)
    present_days = sum(stats['present'] for stats in daily_stats.values())
    attendance_rate = (present_days / total_days * 100) if total_days > 0 else 0
    
    # Determine trend
    if attendance_rate >= 95:
        trend = 'excellent'
    elif attendance_rate >= 85:
        trend = 'good'
    elif attendance_rate >= 75:
        trend = 'average'
    else:
        trend = 'poor'
    
    return {
        'period_days': days,
        'total_days': total_days,
        'present_days': present_days,
        'attendance_rate': round(attendance_rate, 2),
        'trend': trend,
        'daily_breakdown': daily_stats
    }

def backup_database(backup_path: str = None) -> Dict[str, Any]:
    """Create database backup"""
    
    if backup_path is None:
        backup_path = f"hrms_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
    
    try:
        import shutil
        shutil.copy2('hrms.db', backup_path)
        
        return {
            'success': True,
            'backup_path': backup_path,
            'timestamp': datetime.now().isoformat(),
            'size': os.path.getsize(backup_path)
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }

def cleanup_old_backups(days: int = 7) -> Dict[str, Any]:
    """Clean up old backup files"""
    
    import glob
    import os
    
    # Find old backup files
    backup_pattern = "hrms_backup_*.db"
    old_files = []
    
    for file_path in glob.glob(backup_pattern):
        file_age = datetime.now() - datetime.fromtimestamp(os.path.getctime(file_path))
        if file_age.days > days:
            old_files.append(file_path)
    
    # Remove old files
    removed_files = []
    for file_path in old_files:
        try:
            os.remove(file_path)
            removed_files.append(file_path)
        except Exception as e:
            pass  # Log error but continue
    
    return {
        'removed_count': len(removed_files),
        'removed_files': removed_files,
        'cleanup_date': datetime.now().isoformat()
    }
