-- HRMS Lite Database Initialization Script
-- SQLite Database Schema

-- Drop existing tables (for fresh start)
DROP TABLE IF EXISTS attendances;
DROP TABLE IF EXISTS employees;

-- Create employees table
CREATE TABLE employees (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    employee_id TEXT NOT NULL UNIQUE,
    full_name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    department TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create attendances table
CREATE TABLE attendances (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    employee_id INTEGER NOT NULL,
    date DATE NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('Present', 'Absent')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (employee_id) REFERENCES employees(id) ON DELETE CASCADE
);

-- Create indexes for better performance
CREATE INDEX idx_employees_employee_id ON employees(employee_id);
CREATE INDEX idx_employees_email ON employees(email);
CREATE INDEX idx_attendances_employee_id ON attendances(employee_id);
CREATE INDEX idx_attendances_date ON attendances(date);

-- Insert sample data (optional)
INSERT INTO employees (employee_id, full_name, email, department) VALUES
('EMP001', 'John Doe', 'john.doe@company.com', 'Engineering'),
('EMP002', 'Jane Smith', 'jane.smith@company.com', 'Marketing'),
('EMP003', 'Mike Johnson', 'mike.johnson@company.com', 'Sales'),
('A023166922056', 'Praduman Kumar', 'kumarpraduman250@gmail.com', 'Engineering');

-- Insert sample attendance records
INSERT INTO attendances (employee_id, date, status) VALUES
(1, '2024-01-15', 'Present'),
(1, '2024-01-16', 'Present'),
(1, '2024-01-17', 'Absent'),
(2, '2024-01-15', 'Present'),
(2, '2024-01-16', 'Present'),
(3, '2024-01-15', 'Present'),
(3, '2024-01-16', 'Absent');
