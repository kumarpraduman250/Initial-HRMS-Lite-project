-- HRMS Lite Database Schema Documentation
-- SQLite Database Structure

-- =====================================================
-- EMPLOYEES TABLE
-- =====================================================
-- Stores employee information
CREATE TABLE employees (
    id INTEGER PRIMARY KEY AUTOINCREMENT,  -- Auto-incrementing unique identifier
    employee_id TEXT NOT NULL UNIQUE,         -- Employee ID (e.g., EMP001)
    full_name TEXT NOT NULL,                  -- Employee's full name
    email TEXT NOT NULL UNIQUE,               -- Employee's email address
    department TEXT NOT NULL,                  -- Department name
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP  -- Record creation timestamp
);

-- =====================================================
-- ATTENDANCES TABLE
-- =====================================================
-- Stores daily attendance records
CREATE TABLE attendances (
    id INTEGER PRIMARY KEY AUTOINCREMENT,  -- Auto-incrementing unique identifier
    employee_id INTEGER NOT NULL,            -- Reference to employees.id
    date DATE NOT NULL,                      -- Attendance date (YYYY-MM-DD)
    status TEXT NOT NULL CHECK (status IN ('Present', 'Absent')), -- Attendance status
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- Record creation timestamp
    FOREIGN KEY (employee_id) REFERENCES employees(id) ON DELETE CASCADE  -- Foreign key constraint
);

-- =====================================================
-- INDEXES FOR PERFORMANCE
-- =====================================================

-- Index for employee lookups by employee_id
CREATE INDEX idx_employees_employee_id ON employees(employee_id);

-- Index for employee lookups by email
CREATE INDEX idx_employees_email ON employees(email);

-- Index for attendance lookups by employee
CREATE INDEX idx_attendances_employee_id ON attendances(employee_id);

-- Index for attendance lookups by date
CREATE INDEX idx_attendances_date ON attendances(date);

-- =====================================================
-- CONSTRAINTS AND VALIDATIONS
-- =====================================================

-- Employees table constraints:
-- - employee_id must be unique (no duplicate employee IDs)
-- - email must be unique (no duplicate emails)
-- - All fields except id and created_at are required

-- Attendances table constraints:
-- - employee_id must reference existing employee
-- - status must be either 'Present' or 'Absent'
-- - date cannot be null
-- - Deleting an employee deletes all their attendance records (CASCADE)

-- =====================================================
-- SAMPLE DATA
-- =====================================================

-- Sample employees
INSERT INTO employees (employee_id, full_name, email, department) VALUES
('EMP001', 'John Doe', 'john.doe@company.com', 'Engineering'),
('EMP002', 'Jane Smith', 'jane.smith@company.com', 'Marketing'),
('EMP003', 'Mike Johnson', 'mike.johnson@company.com', 'Sales'),
('EMP004', 'Sarah Wilson', 'sarah.wilson@company.com', 'HR'),
('EMP005', 'Tom Brown', 'tom.brown@company.com', 'Finance');

-- Sample attendance records
INSERT INTO attendances (employee_id, date, status) VALUES
(1, '2024-01-15', 'Present'),
(1, '2024-01-16', 'Present'),
(1, '2024-01-17', 'Absent'),
(2, '2024-01-15', 'Present'),
(2, '2024-01-16', 'Present'),
(2, '2024-01-17', 'Present'),
(3, '2024-01-15', 'Present'),
(3, '2024-01-16', 'Absent'),
(4, '2024-01-15', 'Present'),
(4, '2024-01-16', 'Present'),
(5, '2024-01-15', 'Present'),
(5, '2024-01-16', 'Present'),
(5, '2024-01-17', 'Absent');
