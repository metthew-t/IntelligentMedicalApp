# Intelligent Medical System - Backend

Django REST Framework backend for the Intelligent Medical and Hospital Management System.

## Prerequisites

- Python 3.11+
- PostgreSQL 15+
- Redis 7+
- pip and virtualenv

## Quick Start (Local Development)

### 1. Create Virtual Environment

```powershell
# Windows PowerShell
python -m venv venv
.\venv\Scripts\activate
```

```bash
# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Set Up PostgreSQL Database

```sql
-- Create database
CREATE DATABASE intelligent_medical_db;

-- Create user (optional)
CREATE USER postgres WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE intelligent_medical_db TO postgres;
```

### 4. Configure Environment Variables

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your configuration
# Required: SECRET_KEY, DB_PASSWORD
```

### 5. Run Migrations

```bash
python manage.py migrate
```

### 6. Create Initial Data

```bash
python setup.py
```

This will create:
- Default roles (Doctor, Nurse, Pharmacist, etc.)
- Superuser account

### 7. Create Superuser (Alternative)

```bash
python manage.py createsuperuser
```

### 8. Run Development Server

```bash
python manage.py runserver
```

The API will be available at: http://localhost:8000

## Quick Start (Docker)

### 1. Create .env File

```bash
cp .env.example .env
# Edit .env with your configuration
```

### 2. Build and Run with Docker Compose

```bash
# From project root
docker-compose up -d
```

### 3. Run Migrations

```bash
docker-compose exec backend python manage.py migrate
```

### 4. Create Superuser

```bash
docker-compose exec backend python manage.py createsuperuser
```

### 5. Access the Application

- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/api/docs/
- Admin Panel: http://localhost:8000/admin/

## Project Structure

```
backend/
├── apps/                      # Django applications
│   ├── accounts/             # User authentication and authorization
│   ├── organizations/        # Facilities and departments
│   ├── patients/             # Patient management
│   ├── encounters/           # Clinical encounters
│   ├── medical_knowledge/    # Diseases, symptoms, medicines
│   ├── decision_support/     # CDSS engine
│   ├── prescriptions/        # Prescription management
│   ├── laboratory/           # Lab tests and results
│   ├── pharmacy/             # Inventory and dispensing
│   ├── appointments/         # Scheduling
│   ├── admissions/           # Inpatient management
│   ├── nursing/              # Nursing care
│   ├── billing/              # Billing management
│   ├── ml_governance/        # ML lifecycle management
│   ├── audit/                # Audit logging
│   └── reports/              # Reporting
├── config/                    # Django configuration
│   ├── settings.py           # Main settings
│   ├── urls.py               # URL configuration
│   ├── wsgi.py               # WSGI config
│   └── celery.py             # Celery config
├── static/                    # Static files
├── media/                     # User uploaded files
├── logs/                      # Application logs
├── manage.py                  # Django management script
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

## API Documentation

After starting the server, visit:

- **Swagger UI**: http://localhost:8000/api/docs/
- **ReDoc**: http://localhost:8000/api/redoc/
- **OpenAPI Schema**: http://localhost:8000/api/schema/

## Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=apps --cov-report=html

# Run specific test file
pytest apps/accounts/tests/test_models.py

# Run with verbose output
pytest -v
```

## Database Migrations

```bash
# Create new migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Show migration status
python manage.py showmigrations

# Rollback migration
python manage.py migrate app_name migration_name
```

## Celery (Background Tasks)

### Start Celery Worker

```bash
celery -A config worker -l info
```

### Start Celery Beat (Scheduler)

```bash
celery -A config beat -l info
```

### Monitor Celery with Flower

```bash
pip install flower
celery -A config flower
# Visit http://localhost:5555
```

## Common Management Commands

```bash
# Create superuser
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic

# Open Django shell
python manage.py shell

# Show installed apps
python manage.py showmigrations

# Create app
python manage.py startapp app_name

# Run SQL for migration
python manage.py sqlmigrate app_name migration_number

# Check for issues
python manage.py check
```

## Development Tools

### Django Shell Plus

```bash
python manage.py shell_plus
```

### Django Extensions

```bash
# Show URLs
python manage.py show_urls

# Generate ERD (requires graphviz)
python manage.py graph_models -a -o erd.png

# Run development server with SSL
python manage.py runserver_plus --cert-file cert.pem
```

### Code Quality

```bash
# Format code with Black
black .

# Sort imports
isort .

# Lint with flake8
flake8 .

# Run all at once
black . && isort . && flake8 .
```

## Environment Variables

Key environment variables (see `.env.example` for full list):

| Variable | Description | Default |
|----------|-------------|---------|
| DEBUG | Debug mode | True |
| SECRET_KEY | Django secret key | (required) |
| DB_NAME | Database name | intelligent_medical_db |
| DB_USER | Database user | postgres |
| DB_PASSWORD | Database password | (required) |
| DB_HOST | Database host | localhost |
| DB_PORT | Database port | 5432 |
| REDIS_URL | Redis connection URL | redis://localhost:6379/0 |
| ALLOWED_HOSTS | Allowed hosts (comma-separated) | localhost,127.0.0.1 |
| CORS_ALLOWED_ORIGINS | CORS origins (comma-separated) | http://localhost:3000 |

## Security Checklist

Before deploying to production:

- [ ] Set DEBUG=False
- [ ] Change SECRET_KEY to a strong random value
- [ ] Set secure database password
- [ ] Configure ALLOWED_HOSTS
- [ ] Enable HTTPS (SSL/TLS)
- [ ] Configure CORS properly
- [ ] Set up secure session cookies
- [ ] Enable HSTS
- [ ] Configure CSP headers
- [ ] Set up rate limiting
- [ ] Configure secure file uploads
- [ ] Enable audit logging
- [ ] Set up monitoring and alerts
- [ ] Configure automated backups
- [ ] Review security settings in settings.py

## Troubleshooting

### Database Connection Error

```bash
# Check PostgreSQL is running
# Windows
Get-Service postgresql*

# Linux
sudo systemctl status postgresql

# Test connection
psql -U postgres -h localhost -d intelligent_medical_db
```

### Migration Errors

```bash
# Reset migrations (development only!)
python manage.py migrate app_name zero
python manage.py migrate

# Fake initial migration
python manage.py migrate --fake-initial
```

### Redis Connection Error

```bash
# Check Redis is running
# Windows
# Check in Services or run redis-server.exe

# Linux
sudo systemctl status redis

# Test connection
redis-cli ping
```

### Import Errors

```bash
# Ensure virtual environment is activated
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

## Performance Optimization

### Database Query Optimization

```python
# Use select_related for foreign keys
patients = Patient.objects.select_related('registered_facility').all()

# Use prefetch_related for reverse foreign keys
encounters = Encounter.objects.prefetch_related('observations').all()

# Use only() to fetch specific fields
patients = Patient.objects.only('id', 'first_name', 'last_name')

# Use values() for dictionaries
patients = Patient.objects.values('id', 'first_name')
```

### Caching

```python
from django.core.cache import cache

# Set cache
cache.set('key', 'value', timeout=300)

# Get cache
value = cache.get('key')

# Delete cache
cache.delete('key')
```

## Contributing

1. Create a feature branch
2. Make your changes
3. Write tests
4. Run tests and linting
5. Submit pull request

## Support

For issues and questions:
- Check documentation in `/docs`
- Review API documentation at `/api/docs/`
- Contact development team

## License

[Specify License]

---

**Last Updated**: 2026-10-19  
**Version**: 1.0.0
