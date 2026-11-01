# Quick Start Guide

Get the Intelligent Medical System up and running in minutes!

## 🎯 Prerequisites Checklist

Before starting, ensure you have:

- [ ] **Python 3.11 or higher** - [Download here](https://www.python.org/downloads/)
- [ ] **PostgreSQL 15+** (optional) - SQLite works for development
- [ ] **Git** - For version control
- [ ] **Code editor** - VS Code recommended
- [ ] **Postman** (optional) - For API testing

## ⚡ 5-Minute Setup (Windows PowerShell)

### Step 1: Navigate to Backend

```powershell
cd "INTELLIGENT MEDICAL AND HOSPITAL MANAGEMENT SYSTEM/backend"
```

### Step 2: Run Automated Setup

```powershell
.\setup_and_test.ps1
```

This script automatically:
- ✅ Checks Python installation
- ✅ Creates virtual environment
- ✅ Installs dependencies
- ✅ Creates database migrations
- ✅ Initializes system data (roles, permissions, facility types)
- ✅ Runs all tests

### Step 3: Create Your Admin Account

```powershell
python manage.py createsuperuser
```

Enter:
- Email: `admin@example.com` (or your email)
- Username: `admin`
- Password: (your secure password)

### Step 4: Start the Server

```powershell
python manage.py runserver
```

### Step 5: Open Your Browser

Visit these URLs:
- 🎛️ **Admin Panel**: http://localhost:8000/admin/
- 📚 **API Docs**: http://localhost:8000/api/docs/
- 🏥 **API Base**: http://localhost:8000/api/v1/

## 🎉 You're Done!

The system is now running with:
- ✅ 9 predefined roles (Doctor, Nurse, Pharmacist, etc.)
- ✅ 30+ permissions
- ✅ 7 facility types
- ✅ Complete authentication system
- ✅ Organizational structure ready

## 🧪 Test the System

### 1. Login via Admin Panel

Go to http://localhost:8000/admin/ and login with your superuser credentials.

### 2. Create Your First Organization

In Django admin:
1. Click **Organizations** > **Add**
2. Fill in:
   - Name: "My Hospital Group"
   - Code: "MHG001"
   - City: "Addis Ababa"
   - Region: "Addis Ababa"
3. Click **Save**

### 3. Create Your First Facility

In Django admin:
1. Click **Facilities** > **Add**
2. Fill in:
   - Organization: Select the organization you created
   - Facility Type: Choose "General Hospital"
   - Name: "My General Hospital"
   - Code: "MGH001"
   - City: "Addis Ababa"
   - Bed Capacity: 200
3. Click **Save**

### 4. Create a Doctor User

In Django admin:
1. Click **Users** > **Add user**
2. Enter:
   - Email: "doctor@hospital.com"
   - Username: "doctor1"
   - Password: (set a password)
   - First name: "John"
   - Last name: "Doe"
3. Click **Save**
4. Click **User roles** > **Add**
5. Assign "Doctor" role to the user
6. Click **Save**

### 5. Test API with Swagger

1. Go to http://localhost:8000/api/docs/
2. Click **Authorize** button
3. Login with your credentials
4. Try API endpoints:
   - GET `/api/v1/accounts/users/` - List users
   - GET `/api/v1/organizations/facilities/` - List facilities
   - GET `/api/v1/accounts/roles/` - List roles

## 📱 Frontend Setup (Optional)

If you want to run the Flutter frontend:

### Step 1: Install Flutter

Download from https://flutter.dev/docs/get-started/install/windows

### Step 2: Navigate to Frontend

```powershell
cd ../frontend
```

### Step 3: Install Dependencies

```powershell
flutter pub get
```

### Step 4: Run the App

```powershell
# For web browser
flutter run -d chrome

# For Windows desktop
flutter run -d windows
```

## 🐛 Troubleshooting

### Python not found?

Install Python 3.11+ from https://www.python.org/downloads/

### Port 8000 already in use?

```powershell
# Run on different port
python manage.py runserver 8001
```

### Tests failing?

```powershell
# Reset database and rerun
python manage.py flush --no-input
python manage.py migrate
python manage.py init_system
python manage.py test
```

### Virtual environment issues?

```powershell
# Delete and recreate
Remove-Item -Recurse -Force venv
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## 📚 What's Next?

Now that your system is running:

1. **Explore the Admin Interface**
   - Create more users with different roles
   - Set up your organizational structure
   - Explore the audit logs

2. **Test the APIs**
   - Use Swagger UI at http://localhost:8000/api/docs/
   - Test authentication flows
   - Try CRUD operations

3. **Read the Documentation**
   - `PROJECT_STATUS.md` - Overall project status
   - `FEATURES_CHECKLIST.md` - Feature completion tracking
   - `backend/TESTING.md` - Detailed testing guide
   - `docs/` - Complete technical documentation

4. **Start Development**
   - Review `docs/implementation-roadmap.md`
   - Choose next module to implement
   - Follow the established patterns

## 🎓 Learn the System

### Key Concepts

**1. Roles**
- System Administrator - Full system access
- Hospital Administrator - Hospital management
- Doctor - Clinical care
- Nurse - Patient care
- Pharmacist - Medication management
- Lab Technician - Laboratory work
- Radiologist - Imaging interpretation
- Receptionist - Front desk
- Billing Clerk - Financial operations

**2. Permissions**
- Format: `resource:action` (e.g., `patient:read`)
- Assigned to roles
- Checked in API views

**3. Organizations**
- Top level: Organization (hospital chain)
- Mid level: Facility (individual hospital)
- Department level: Departments (Emergency, Surgery, etc.)
- Ward level: Wards (ICU, General, etc.)

**4. Multi-tenancy**
- Users can have different roles at different facilities
- Facility-level data scoping
- Organization-wide reporting

## 🔐 Default System Data

After running `init_system`, you have:

### 9 Roles
- system_admin, hospital_admin, doctor, nurse, pharmacist, lab_tech, radiologist, receptionist, billing_clerk

### 30+ Permissions
- patient:read, patient:write, patient:delete
- encounter:read, encounter:write, encounter:delete
- prescription:read, prescription:write, prescription:approve
- lab:read, lab:write, lab:approve
- imaging:read, imaging:write, imaging:approve
- pharmacy:read, pharmacy:dispense, pharmacy:manage
- appointment:read, appointment:write
- admission:read, admission:write
- billing:read, billing:write, billing:approve
- user:read, user:write, user:manage_roles
- system:manage

### 7 Facility Types
- Primary Hospital (PH)
- General Hospital (GH)
- Specialized Hospital (SH)
- Referral Hospital (RH)
- Health Center (HC)
- Clinic (CL)
- Diagnostic Center (DC)

## 💡 Pro Tips

1. **Use Django Admin** for quick data management during development
2. **Check API Docs** at `/api/docs/` for endpoint details
3. **Run Tests** frequently: `python manage.py test`
4. **Check Logs** in `backend/logs/` for debugging
5. **Use SQLite** for local development, PostgreSQL for production
6. **Enable Debug Toolbar** in development for SQL query analysis

## 🎊 Congratulations!

You now have a fully functional medical system foundation running locally. The system includes:

✅ Complete authentication and authorization  
✅ User and role management  
✅ Organizational structure (orgs, facilities, departments, wards)  
✅ Security features (account locking, audit logging)  
✅ RESTful APIs with documentation  
✅ Django admin interface  
✅ Comprehensive test suite  

Ready to build the clinical modules! 🚀

## 📞 Need Help?

- **Documentation**: Check `docs/` folder for detailed specifications
- **Testing Guide**: Read `backend/TESTING.md`
- **Project Status**: Review `PROJECT_STATUS.md`
- **API Issues**: Check Django logs and API documentation
- **General Questions**: Review the comprehensive documentation

---

**Happy Coding! 🎉**
