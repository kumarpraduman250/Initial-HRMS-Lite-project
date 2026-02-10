#!/usr/bin/env python3
"""
Test script for HRMS Lite API endpoints
"""

import requests
import json
from datetime import date

# API base URL
BASE_URL = "http://127.0.0.1:8000"

def test_connection():
    """Test basic API connection"""
    print("🔍 Testing API Connection...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ API is running")
            print(f"Response: {response.json()}")
            return True
        else:
            print(f"❌ API returned status: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to API: {e}")
        return False

def test_get_employees():
    """Test getting all employees"""
    print("\n👥 Testing Get Employees...")
    try:
        response = requests.get(f"{BASE_URL}/employees/")
        if response.status_code == 200:
            employees = response.json()
            print(f"✅ Found {len(employees)} employees")
            for emp in employees:
                print(f"  - {emp['employee_id']}: {emp['full_name']} ({emp['department']})")
            return employees
        else:
            print(f"❌ Failed to get employees: {response.status_code}")
            print(f"Response: {response.text}")
            return []
    except Exception as e:
        print(f"❌ Error getting employees: {e}")
        return []

def test_add_employee():
    """Test adding a new employee"""
    print("\n➕ Testing Add Employee...")
    
    # Test employee data
    test_employee = {
        "employee_id": "TEST001",
        "full_name": "Test User",
        "email": "test.user@company.com",
        "department": "Engineering"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/employees/",
            json=test_employee,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            print("✅ Employee added successfully")
            print(f"Response: {response.json()}")
            return response.json()
        else:
            print(f"❌ Failed to add employee: {response.status_code}")
            print(f"Response: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error adding employee: {e}")
        return None

def test_add_attendance(employee_id: int):
    """Test adding attendance for an employee"""
    print(f"\n📅 Testing Add Attendance for Employee ID: {employee_id}...")
    
    attendance_data = {
        "employee_id": employee_id,
        "date": date.today().isoformat(),
        "status": "Present"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/attendance/",
            json=attendance_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            print("✅ Attendance added successfully")
            print(f"Response: {response.json()}")
            return response.json()
        else:
            print(f"❌ Failed to add attendance: {response.status_code}")
            print(f"Response: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error adding attendance: {e}")
        return None

def test_get_attendance():
    """Test getting all attendance records"""
    print("\n📊 Testing Get Attendance Records...")
    try:
        response = requests.get(f"{BASE_URL}/attendance/")
        if response.status_code == 200:
            attendances = response.json()
            print(f"✅ Found {len(attendances)} attendance records")
            for att in attendances[:5]:  # Show first 5
                print(f"  - Employee {att['employee_id']}: {att['date']} ({att['status']})")
            return attendances
        else:
            print(f"❌ Failed to get attendance: {response.status_code}")
            print(f"Response: {response.text}")
            return []
    except Exception as e:
        print(f"❌ Error getting attendance: {e}")
        return []

def test_employee_attendance(employee_id: int):
    """Test getting attendance for specific employee"""
    print(f"\n👤 Testing Get Attendance for Employee ID: {employee_id}...")
    try:
        response = requests.get(f"{BASE_URL}/attendance/employee/{employee_id}")
        if response.status_code == 200:
            attendances = response.json()
            print(f"✅ Found {len(attendances)} attendance records for employee")
            for att in attendances:
                print(f"  - {att['date']}: {att['status']}")
            return attendances
        else:
            print(f"❌ Failed to get employee attendance: {response.status_code}")
            print(f"Response: {response.text}")
            return []
    except Exception as e:
        print(f"❌ Error getting employee attendance: {e}")
        return []

def test_delete_employee(employee_id: int):
    """Test deleting an employee"""
    print(f"\n🗑️ Testing Delete Employee ID: {employee_id}...")
    try:
        response = requests.delete(f"{BASE_URL}/employees/{employee_id}")
        if response.status_code == 200:
            print("✅ Employee deleted successfully")
            print(f"Response: {response.json()}")
            return True
        else:
            print(f"❌ Failed to delete employee: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error deleting employee: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 HRMS Lite API Test Suite")
    print("=" * 50)
    
    # Test connection
    if not test_connection():
        print("\n❌ Cannot proceed - API is not running")
        return
    
    # Test employees
    employees = test_get_employees()
    
    # Test adding employee
    new_employee = test_add_employee()
    
    # Get updated employee list
    updated_employees = test_get_employees()
    
    # Test attendance
    attendances = test_get_attendance()
    
    # Test adding attendance (use first employee ID)
    if updated_employees:
        test_add_attendance(updated_employees[0]['id'])
        test_employee_attendance(updated_employees[0]['id'])
    
    # Test deletion (use test employee if created)
    if new_employee:
        test_delete_employee(new_employee['id'])
    
    print("\n" + "=" * 50)
    print("🏁 Test Suite Complete")

if __name__ == "__main__":
    main()
