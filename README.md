# Database Documentation - HRMS Lite

## Overview

HRMS Lite uses SQLite as its database backend. The database consists of two main tables: `employees` and `attendances`.

## Database Files

- **`init.sql`** - Complete database initialization with sample data
- **`schema.sql`** - Database schema documentation with detailed comments
- **`hrms.db`** - Runtime database file (auto-generated)

## Table Structure

### Employees Table

| Column | Type | Constraints | Description |
|---------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY, AUTOINCREMENT | Unique identifier |
| employee_id | TEXT | NOT NULL, UNIQUE | Employee ID (e.g., EMP001) |
| full_name | TEXT | NOT NULL | Employee's full name |
| email | TEXT | NOT NULL, UNIQUE | Email address |
| department | TEXT | NOT NULL | Department name |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Creation timestamp |

### Attendances Table

| Column | Type | Constraints | Description |
|---------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY, AUTOINCREMENT | Unique identifier |
| employee_id | INTEGER | NOT NULL, FOREIGN KEY | Reference to employees.id |
| date | DATE | NOT NULL | Attendance date (YYYY-MM-DD) |
| status | TEXT | NOT NULL, CHECK | 'Present' or 'Absent' |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Creation timestamp |

## Relationships

- **One-to-Many**: One employee can have many attendance records
- **Cascade Delete**: Deleting an employee removes all their attendance records
- **Foreign Key**: attendance.employee_id references employees.id

## Indexes

For optimal performance, the following indexes are created:

- `idx_employees_employee_id` - Fast employee lookup by ID
- `idx_employees_email` - Fast employee lookup by email
- `idx_attendances_employee_id` - Fast attendance lookup by employee
- `idx_attendances_date` - Fast attendance lookup by date

## Database Initialization

### Method 1: Using init.sql
```bash
# Navigate to database directory
cd database

# Run SQLite with init script
sqlite3 ../hrms.db < init.sql
```

### Method 2: Automatic (Recommended)
The FastAPI application automatically creates the database and tables on first run.

## Sample Data

The `init.sql` file includes sample data:

- **5 Sample Employees** across different departments
- **12 Attendance Records** showing various scenarios
- **Realistic Data** for testing and demonstration

## Data Validation

### Employee Validation
- Employee ID must be unique
- Email must be valid format and unique
- All fields except id and created_at are required

### Attendance Validation
- Employee must exist in employees table
- Status must be 'Present' or 'Absent'
- Date cannot be in the future
- No duplicate attendance for same employee and date

## Backup and Recovery

### Backup Database
```bash
# Create backup
cp hrms.db hrms_backup_$(date +%Y%m%d_%H%M%S).db

# Or using SQLite dump
sqlite3 hrms.db .dump > hrms_backup_$(date +%Y%m%d_%H%M%S).sql
```

### Restore Database
```bash
# Restore from backup
cp hrms_backup_20240115_120000.db hrms.db

# Or from SQL dump
sqlite3 hrms.db < hrms_backup_20240115_120000.sql
```

## Query Examples

### Get All Employees
```sql
SELECT * FROM employees ORDER BY created_at DESC;
```

### Get Employee Attendance
```sql
SELECT e.full_name, e.employee_id, a.date, a.status
FROM employees e
LEFT JOIN attendances a ON e.id = a.employee_id
WHERE e.id = 1
ORDER BY a.date DESC;
```

### Attendance Summary
```sql
SELECT 
    e.full_name,
    e.department,
    COUNT(CASE WHEN a.status = 'Present' THEN 1 END) as present_days,
    COUNT(CASE WHEN a.status = 'Absent' THEN 1 END) as absent_days,
    COUNT(*) as total_days
FROM employees e
LEFT JOIN attendances a ON e.id = a.employee_id
GROUP BY e.id, e.full_name, e.department;
```

### Department-wise Attendance
```sql
SELECT 
    e.department,
    COUNT(CASE WHEN a.status = 'Present' THEN 1 END) as present_count,
    COUNT(CASE WHEN a.status = 'Absent' THEN 1 END) as absent_count
FROM employees e
LEFT JOIN attendances a ON e.id = a.employee_id
GROUP BY e.department;
```

## Migration Notes

### Version 1.0 (Current)
- Initial database schema
- Basic employee and attendance tracking
- SQLite backend for simplicity

### Future Considerations
- Migration to PostgreSQL for production
- Add user authentication table
- Add leave management tables
- Add payroll-related tables

## Performance Optimization

### Recommended Settings
```python
# For high-traffic applications
SQLALCHEMY_ENGINE_OPTIONS = {
    "pool_size": 20,
    "max_overflow": 30,
    "pool_pre_ping": True,
    "pool_recycle": 3600
}
```

### Query Optimization
- Use indexes for frequent queries
- Avoid SELECT * in production
- Implement pagination for large datasets
- Consider read replicas for reporting queries
