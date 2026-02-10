from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import sessionmaker, Session, relationship, declarative_base
from pydantic import BaseModel
from datetime import date
from typing import List
import re

# -----------------------------
# App Setup
# -----------------------------
app = FastAPI(title="HRMS Lite API", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------
# Database Setup
# -----------------------------
DATABASE_URL = "sqlite:///./hrms.db"

engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


# -----------------------------
# Database Models
# -----------------------------
class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    department = Column(String, nullable=False)

    attendances = relationship(
        "Attendance",
        back_populates="employee",
        cascade="all, delete"
    )


class Attendance(Base):
    __tablename__ = "attendances"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"))
    date = Column(Date, nullable=False)
    status = Column(String, nullable=False)

    employee = relationship("Employee", back_populates="attendances")


# Create Tables
Base.metadata.create_all(bind=engine)


# -----------------------------
# DB Dependency
# -----------------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# -----------------------------
# Schemas (Pydantic)
# -----------------------------
class EmployeeBase(BaseModel):
    employee_id: str
    full_name: str
    email: str
    department: str


class EmployeeCreate(EmployeeBase):
    pass


class EmployeeResponse(EmployeeBase):
    id: int

    class Config:
        from_attributes = True


class AttendanceBase(BaseModel):
    date: date
    status: str


class AttendanceCreate(AttendanceBase):
    employee_id: int


class AttendanceResponse(AttendanceBase):
    id: int
    employee_id: int

    class Config:
        from_attributes = True


class EmployeeWithAttendance(EmployeeResponse):
    attendances: List[AttendanceResponse] = []


# -----------------------------
# Utils
# -----------------------------
def is_valid_email(email: str):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email)


# -----------------------------
# Home Route (Fixes 404 /)
# -----------------------------
@app.get("/")
def home():
    return {
        "message": "HRMS API is running 🚀",
        "docs": "/docs"
    }


# -----------------------------
# Employee APIs
# -----------------------------
@app.post("/employees/", response_model=EmployeeResponse)
def create_employee(
    employee: EmployeeCreate,
    db: Session = Depends(get_db)
):

    if not is_valid_email(employee.email):
        raise HTTPException(400, "Invalid email format")

    if db.query(Employee).filter(Employee.employee_id == employee.employee_id).first():
        raise HTTPException(400, "Employee ID already exists")

    if db.query(Employee).filter(Employee.email == employee.email).first():
        raise HTTPException(400, "Email already exists")

    db_employee = Employee(**employee.dict())

    db.add(db_employee)
    db.commit()
    db.refresh(db_employee)

    return db_employee


@app.get("/employees/", response_model=List[EmployeeResponse])
def get_employees(db: Session = Depends(get_db)):
    return db.query(Employee).all()


@app.get("/employees/{employee_id}", response_model=EmployeeWithAttendance)
def get_employee(employee_id: int, db: Session = Depends(get_db)):

    employee = db.query(Employee).filter(Employee.id == employee_id).first()

    if not employee:
        raise HTTPException(404, "Employee not found")

    return employee


@app.delete("/employees/{employee_id}")
def delete_employee(employee_id: int, db: Session = Depends(get_db)):

    employee = db.query(Employee).filter(Employee.id == employee_id).first()

    if not employee:
        raise HTTPException(404, "Employee not found")

    db.delete(employee)
    db.commit()

    return {"message": "Employee deleted successfully"}


# -----------------------------
# Attendance APIs
# -----------------------------
@app.post("/attendance/", response_model=AttendanceResponse)
def mark_attendance(
    attendance: AttendanceCreate,
    db: Session = Depends(get_db)
):

    employee = db.query(Employee).filter(Employee.id == attendance.employee_id).first()

    if not employee:
        raise HTTPException(404, "Employee not found")

    if attendance.status not in ["Present", "Absent"]:
        raise HTTPException(400, "Status must be Present or Absent")

    exists = db.query(Attendance).filter(
        Attendance.employee_id == attendance.employee_id,
        Attendance.date == attendance.date
    ).first()

    if exists:
        raise HTTPException(400, "Attendance already marked")

    db_attendance = Attendance(**attendance.dict())

    db.add(db_attendance)
    db.commit()
    db.refresh(db_attendance)

    return db_attendance


@app.get("/attendance/", response_model=List[AttendanceResponse])
def get_all_attendance(db: Session = Depends(get_db)):
    return db.query(Attendance).all()


@app.get("/attendance/employee/{employee_id}", response_model=List[AttendanceResponse])
def get_employee_attendance(employee_id: int, db: Session = Depends(get_db)):

    if not db.query(Employee).filter(Employee.id == employee_id).first():
        raise HTTPException(404, "Employee not found")

    return db.query(Attendance).filter(
        Attendance.employee_id == employee_id
    ).all()


# -----------------------------
# Health Check
# -----------------------------
@app.get("/health")
def health():
    return {"status": "healthy"}


# -----------------------------
# Run Server
# -----------------------------
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
