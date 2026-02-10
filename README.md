# HRMS Lite - Employee and Attendance Management System

A lightweight Human Resource Management System that allows administrators to manage employee records and track daily attendance.

## Features

### Employee Management
-  Add new employees with unique ID, full name, email, and department
-  View list of all employees
-  Delete employee records
-  Email validation and duplicate prevention

### Attendance Management
- Mark attendance for employees (Present/Absent)
- View attendance records for each employee
- Filter attendance records by employee
- Date-based attendance tracking

### UI/UX Features
-  Professional, responsive design
- Loading states for better user experience
- Error handling with user-friendly messages
- Empty states when no data is available
- Tab-based navigation between modules

## Tech Stack

### Backend
- **FastAPI** - Modern, fast web framework for building APIs
- **SQLAlchemy** - SQL toolkit and ORM
- **SQLite** - Lightweight database for data persistence
- **Pydantic** - Data validation using Python type annotations
- **Uvicorn** - ASGI server

### Frontend
- **React 18** - JavaScript library for building user interfaces
- **TypeScript** - Type-safe JavaScript
- **Axios** - HTTP client for API requests
- **CSS3** - Modern styling with responsive design

### Deployment
- **Render** (Backend) - Cloud platform for hosting APIs
- **Vercel** (Frontend) - Platform for hosting static web applications

## Project Structure

```
HRP/
├── backend/
│   ├── main.py              # FastAPI application
│   ├── requirements.txt     # Python dependencies
│   └── Procfile            # Deployment configuration
├── frontend/
│   ├── public/
│   │   └── index.html      # HTML template
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── App.tsx         # Main application component
│   │   ├── api.ts          # API client
│   │   ├── types.ts        # TypeScript type definitions
│   │   └── *.css           # Styling
│   ├── package.json        # Node.js dependencies
│   └── tsconfig.json       # TypeScript configuration
└── README.md               # This file
```

## API Endpoints

### Employee Management
- `POST /employees/` - Create a new employee
- `GET /employees/` - Get all employees
- `GET /employees/{id}` - Get employee by ID with attendance records
- `DELETE /employees/{id}` - Delete an employee

### Attendance Management
- `POST /attendance/` - Mark attendance for an employee
- `GET /attendance/` - Get all attendance records
- `GET /attendance/employee/{employee_id}` - Get attendance for specific employee

### Health Check
- `GET /health` - Check API health status

## Setup and Installation

### Prerequisites
- Node.js (v16 or higher)
- Python (v3.8 or higher)
- Git

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment:
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Start the backend server:
```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm start
```

The frontend will be available at `http://localhost:3000`

## Running the Application

1. Start the backend server (as described above)
2. Start the frontend server (as described above)
3. Open your browser and navigate to `http://localhost:3000`

## Data Validation

### Employee Validation
- Employee ID must be unique
- Email must be valid format and unique
- All fields (Employee ID, Full Name, Email, Department) are required
- Department must be one of: Engineering, Sales, Marketing, HR, Finance, Operations

### Attendance Validation
- Employee must exist in the system
- Date cannot be in the future
- Status must be either "Present" or "Absent"
- Cannot mark duplicate attendance for the same employee and date

## Error Handling

The application includes comprehensive error handling:
- **Client-side validation** for immediate feedback
- **Server-side validation** for data integrity
- **User-friendly error messages** for better UX
- **HTTP status codes** following REST conventions

## Deployment

### Backend Deployment (Render)
1. Push the code to a GitHub repository
2. Connect the repository to Render
3. Set the build command: `pip install -r requirements.txt`
4. Set the start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Deploy the service

### Frontend Deployment (Vercel)
1. Push the code to a GitHub repository
2. Connect the repository to Vercel
3. Set the build command: `npm run build`
4. Set the output directory: `build`
5. Update the API URL in the environment variables
6. Deploy the application

## Assumptions and Limitations

### Assumptions
- Single admin user (no authentication required)
- Email format follows standard patterns
- Department list is predefined and limited
- Attendance is marked on a daily basis

### Limitations
- No user authentication system
- No bulk operations (e.g., bulk attendance marking)
- No advanced reporting or analytics
- No leave management or payroll features
- No file upload capabilities for employee photos/documents

## Future Enhancements

### Potential Features
- User authentication and role-based access
- Advanced reporting and analytics dashboard
- Bulk attendance operations
- Leave management system
- Payroll integration
- Employee profile photos
- Email notifications for attendance
- Mobile-responsive improvements
- Data export functionality

### Technical Improvements
- Database migration to PostgreSQL/MySQL for production
- Caching layer for improved performance
- API rate limiting
- Comprehensive test suite
- CI/CD pipeline setup
- Monitoring and logging

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is open source and available under the [MIT License](LICENSE).

## Contact

For questions or support, please open an issue in the GitHub repository.
