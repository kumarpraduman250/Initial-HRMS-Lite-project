#!/usr/bin/env python3
"""
HRMS Lite Database Setup Script
Automates database initialization and sample data insertion
"""

import sqlite3
import os
from datetime import datetime, timedelta

def setup_database():
    """Initialize the HRMS Lite database with schema and sample data"""
    
    # Database path
    db_path = os.path.join(os.path.dirname(__file__), '..', 'hrms.db')
    
    print(f"Setting up database at: {db_path}")
    
    # Connect to SQLite database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Drop existing tables for fresh start
        print("Dropping existing tables...")
        cursor.execute("DROP TABLE IF EXISTS attendances")
        cursor.execute("DROP TABLE IF EXISTS employees")
        
        # Create employees table
        print("Creating employees table...")
        cursor.execute("""
            CREATE TABLE employees (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                employee_id TEXT NOT NULL UNIQUE,
                full_name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                department TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create attendances table
        print("Creating attendances table...")
        cursor.execute("""
            CREATE TABLE attendances (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                employee_id INTEGER NOT NULL,
                date DATE NOT NULL,
                status TEXT NOT NULL CHECK (status IN ('Present', 'Absent')),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (employee_id) REFERENCES employees(id) ON DELETE CASCADE
            )
        """)
        
        # Create indexes for performance
        print("Creating indexes...")
        cursor.execute("CREATE INDEX idx_employees_employee_id ON employees(employee_id)")
        cursor.execute("CREATE INDEX idx_employees_email ON employees(email)")
        cursor.execute("CREATE INDEX idx_attendances_employee_id ON attendances(employee_id)")
        cursor.execute("CREATE INDEX idx_attendances_date ON attendances(date)")
        
        # Insert sample employees
        print("Inserting sample employees...")
        employees_data = [
            ('EMP001', 'John Doe', 'john.doe@company.com', 'Engineering'),
            ('EMP002', 'Jane Smith', 'jane.smith@company.com', 'Marketing'),
            ('EMP003', 'Mike Johnson', 'mike.johnson@company.com', 'Sales'),
            ('EMP004', 'Sarah Wilson', 'sarah.wilson@company.com', 'HR'),
            ('EMP005', 'Tom Brown', 'tom.brown@company.com', 'Finance'),
            ('EMP006', 'Lisa Chen', 'lisa.chen@company.com', 'Operations'),
            ('EMP007', 'David Kumar', 'david.kumar@company.com', 'Engineering'),
            ('EMP008', 'Emily Davis', 'emily.davis@company.com', 'Marketing')
        ]
        
        cursor.executemany("""
            INSERT INTO employees (employee_id, full_name, email, department) 
            VALUES (?, ?, ?, ?)
        """, employees_data)
        
        # Get employee IDs for attendance records
        cursor.execute("SELECT id, employee_id FROM employees")
        employee_map = {emp_id: db_id for db_id, emp_id in cursor.fetchall()}
        
        # Insert sample attendance records for the last 30 days
        print("Inserting sample attendance records...")
        import random
        
        attendance_data = []
        for emp_id, db_id in employee_map.items():
            # Generate random attendance for last 30 days
            for days_ago in range(30):
                date = (datetime.now() - timedelta(days=days_ago)).strftime('%Y-%m-%d')
                status = random.choice(['Present', 'Absent'])
                # Skip weekends (70% chance of attendance on weekdays)
                if datetime.strptime(date, '%Y-%m-%d').weekday() < 5:  # Monday-Friday
                    if random.random() < 0.9:  # 90% attendance rate
                        attendance_data.append((db_id, date, status))
        
        cursor.executemany("""
            INSERT INTO attendances (employee_id, date, status) 
            VALUES (?, ?, ?)
        """, attendance_data)
        
        # Commit changes
        conn.commit()
        print("Database setup completed successfully!")
        
        # Print statistics
        cursor.execute("SELECT COUNT(*) FROM employees")
        emp_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM attendances")
        att_count = cursor.fetchone()[0]
        
        print(f"Created {emp_count} employees")
        print(f"Created {att_count} attendance records")
        
        # Show sample data
        print("\nSample employees:")
        cursor.execute("SELECT employee_id, full_name, department FROM employees LIMIT 3")
        for emp in cursor.fetchall():
            print(f"  - {emp[0]}: {emp[1]} ({emp[2]})")
        
    except Exception as e:
        print(f"Error setting up database: {e}")
        conn.rollback()
    finally:
        conn.close()

def verify_database():
    """Verify database setup and show basic statistics"""
    
    db_path = os.path.join(os.path.dirname(__file__), '..', 'hrms.db')
    
    if not os.path.exists(db_path):
        print("Database file not found!")
        return False
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if tables exist
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name IN ('employees', 'attendances')
        """)
        tables = [row[0] for row in cursor.fetchall()]
        
        if 'employees' not in tables or 'attendances' not in tables:
            print("Required tables not found!")
            return False
        
        print("Database verification passed!")
        print(f"Tables found: {', '.join(tables)}")
        
        # Show record counts
        cursor.execute("SELECT COUNT(*) FROM employees")
        emp_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM attendances")
        att_count = cursor.fetchone()[0]
        
        print(f"Employees: {emp_count}")
        print(f"Attendance Records: {att_count}")
        
        return True
        
    except Exception as e:
        print(f"Error verifying database: {e}")
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    print("HRMS Lite Database Setup")
    print("=" * 40)
    
    # Setup database
    setup_database()
    
    print("\n" + "=" * 40)
    
    # Verify setup
    verify_database()
    
    print("\nDatabase setup complete!")
    print("You can now start the HRMS Lite application.")
