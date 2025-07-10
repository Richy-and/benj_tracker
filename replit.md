# QR Code Attendance System

## Overview

This is a Flask-based QR code attendance tracking system designed for monitoring worker presence. The application allows administrators to register workers, generate unique QR codes for each worker, and track attendance through QR code scanning. The system provides a simple web interface in French for managing workers and viewing attendance logs.

## User Preferences

Preferred communication style: Simple, everyday language.

## Recent Changes (January 2025)

✓ Migrated project from Replit Agent to standard Replit environment
✓ Fixed Flask application structure and database configuration
✓ Created complete HTML template system with Bootstrap styling
✓ Added Render.com deployment configuration
✓ Fixed session secret key issues for production deployment
✓ Added PostgreSQL URL compatibility for various hosting platforms

## System Architecture

### Backend Architecture
- **Framework**: Flask web framework with Python
- **Database**: PostgreSQL database with SQLAlchemy ORM
- **Session Management**: Flask sessions with configurable secret key
- **Logging**: Python's built-in logging module for debugging

### Frontend Architecture
- **Templates**: Jinja2 templating engine with HTML templates
- **Styling**: Bootstrap 5 with dark theme and Font Awesome icons
- **Responsive Design**: Mobile-friendly interface with print styles for QR codes
- **Language**: French UI for all user-facing elements

### Data Storage
- **Primary Storage**: PostgreSQL database with two main tables:
  - `workers`: Stores worker information (id, matricule, name, created_at)
  - `attendance`: Stores attendance records with foreign key relationship to workers
- **Data Structure**: Relational database with proper foreign key constraints and unique constraints

## Key Components

### Worker Management
- **Registration**: Add new workers with unique matricule (ID) and full name
- **Validation**: Input validation for matricule format (alphanumeric only)
- **QR Code Generation**: Dynamic QR code creation using the `qrcode` library
- **Worker Listing**: View all registered workers with management options

### Attendance Tracking
- **QR Code Scanning**: Each worker gets a unique QR code linking to their attendance URL
- **Automatic Recording**: Attendance is recorded when the QR code URL is accessed
- **Timestamp Tracking**: Records both date and time of attendance
- **Duplicate Prevention**: Prevents multiple attendance records for the same day

### Reporting and Analytics
- **Daily Reports**: View attendance for specific dates
- **Statistics Dashboard**: Shows total workers and daily attendance counts
- **Attendance Log**: Comprehensive view of all attendance records

## Data Flow

1. **Worker Registration**: Admin adds worker → System generates unique QR code → Worker data stored in DB
2. **Attendance Recording**: Worker scans QR code → System validates worker → Attendance recorded with timestamp
3. **Report Generation**: Admin selects date → System queries attendance records → Displays statistics and worker lists

## External Dependencies

### Python Libraries
- **Flask**: Web framework for routing and request handling
- **Flask-SQLAlchemy**: ORM for database operations
- **qrcode**: QR code generation with PIL/Pillow for image processing
- **Pillow**: Image processing library for QR code generation
- **psycopg2-binary**: PostgreSQL database adapter
- **base64/io**: Image encoding for QR code display

### Frontend Dependencies
- **Bootstrap 5**: CSS framework with dark theme variant
- **Font Awesome 6**: Icon library for UI elements
- **Custom CSS**: Mobile-responsive and print-friendly styles

### Environment Variables
- **SESSION_SECRET**: Flask session security (defaults to development key)
- **DATABASE_URL**: PostgreSQL connection string for database access

## Deployment Strategy

### Replit Platform
- **Main Entry Point**: `main.py` runs the Flask application
- **Development Mode**: Debug enabled for development environment
- **Port Configuration**: Runs on port 5000 with host binding to 0.0.0.0
- **Static Assets**: Served directly by Flask for CSS and other static files

### Database Initialization
- **Auto-setup**: Database tables are created automatically using SQLAlchemy
- **Data Persistence**: PostgreSQL provides robust persistent storage with ACID properties
- **Migration Strategy**: Uses SQLAlchemy models with automatic table creation

### Security Considerations
- **Session Security**: Configurable secret key for session management
- **Input Validation**: Basic validation on worker matricule format
- **No Authentication**: Currently designed for internal/trusted network use